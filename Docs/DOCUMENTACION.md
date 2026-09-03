# Documentación técnica — Sistema de Enfermería Escolar

## 1. Arquitectura general

Aplicación de escritorio monolítica (no cliente-servidor). Cada PC tiene su propia base de datos SQLite local (`data/enfermeria.db`). No hay conexión de red entre las dos PCs durante el uso normal; la sincronización se hace de forma manual mediante archivos exportados (`.json`).

```
┌─────────────┐        archivo .json         ┌─────────────┐
│     PC1      │  ───────(USB / correo)────►  │     PC2      │
│ enfermeria.db │                              │ enfermeria.db │
└─────────────┘  ◄───────(USB / correo)────   └─────────────┘
```

## 2. Modelo de datos (SQLite)

### Tabla `estudiantes`
| Campo | Tipo | Notas |
|---|---|---|
| id | TEXT (UUID) | Clave primaria |
| nombre | TEXT | En mayúsculas (forzado en la interfaz) |
| curso | TEXT | Ver `constantes.py` → `CURSOS` |
| paralelo | TEXT | A/B/C/D (EGB) o especialidad (Bachillerato) |
| sexo | TEXT | "Masculino" / "Femenino" |
| origen_pc | TEXT | PC1 / PC2, según dónde se creó |
| fecha_creacion | DATETIME | |

### Tabla `atenciones`
| Campo | Tipo | Notas |
|---|---|---|
| id | TEXT (UUID) | Clave primaria |
| estudiante_id | TEXT (UUID) | FK → estudiantes.id |
| fecha | DATE | |
| hora_llegada | TIME | |
| hora_salida | TIME | NULL hasta que se marque salida |
| saturacion | INTEGER | % |
| temperatura | REAL | °C |
| frecuencia_cardiaca | INTEGER | lpm |
| diagnostico | TEXT | Uno de `DIAGNOSTICOS` o texto libre ("Otros") |
| recomendacion | TEXT | |
| enfermera_responsable | TEXT | FK → usuarios.id |
| origen_pc | TEXT | |
| fecha_registro | DATETIME | Timestamp exacto de creación |

### Tabla `usuarios`
| Campo | Tipo | Notas |
|---|---|---|
| id | TEXT (UUID) | |
| nombre_completo | TEXT | |
| usuario | TEXT | Único |
| password_hash | TEXT | PBKDF2-SHA256, formato `salt$hash` |
| rol | TEXT | Actualmente sin uso funcional (reservado) |
| activo | BOOLEAN | |

### Tabla `log_sincronizacion`
Registra cada importación realizada (fecha, cuántos registros nuevos, cuántos duplicados detectados).

## 3. Lógica de Curso/Paralelo dinámico

`gui/constantes.py` define las listas base:
- `CURSOS`: lista completa para el desplegable de Curso.
- `CURSOS_EGB` / `CURSOS_BACHILLERATO`: subconjuntos usados para decidir qué opciones de Paralelo mostrar.
- `PARALELOS_EGB` = `["A", "B", "C", "D"]`.
- `ESPECIALIDADES_BACHILLERATO`: las 4 especialidades técnicas.

Al elegir un Curso, `_on_cambiar_curso()` reconfigura el ComboBox de Paralelo con la lista correspondiente y lo habilita (antes de elegir Curso, Paralelo está deshabilitado).

## 4. Autenticación y sesión

- Contraseñas: hash **PBKDF2-HMAC-SHA256** (100,000 iteraciones), sin dependencias externas (solo `hashlib` de la librería estándar).
- Creación de cuentas: requiere un **código de autorización** fijo (`CODIGO_AUTORIZACION_CUENTAS` en `auth.py`) para evitar que cualquiera cree cuentas.
- Sesión: se guarda en `data/session.json` (no se sube a Git). Expira por **inactividad** (no por tiempo fijo desde el login): cada evento de mouse/teclado/clic en la ventana refresca la expiración. Duración configurable en `auth.py` → `DURACION_SESION_MINUTOS`.
- El último usuario que inició sesión se recuerda en `data/ultimo_usuario.json`, para pre-llenar el campo al reabrir el programa.

> **Todas las cuentas ven los mismos datos.** El login sirve para trazabilidad (quién registró cada atención), no para aislar información entre usuarios. No hay control de permisos por rol implementado todavía (el campo `rol` existe en la BD pero no se usa para restringir acciones).

## 5. Identificación de PC (PC1 / PC2)

`config.py` guarda en `data/config.json` (no se sube a Git) si esta instalación es "PC1" o "PC2". Se pregunta una sola vez, en el primer arranque (`vista_principal.py` → `_solicitar_identificacion_pc()`), y se usa para:
- Etiquetar el campo `origen_pc` de cada estudiante/atención nueva.
- Identificar el archivo exportado (`enfermeria_PC1_2026-08.json`).
- Advertir si intentas importar un archivo generado por la misma PC.

## 6. Sincronización (exportar / importar)

**Exportar** (`exportar_datos_mes`): genera un `.json` con todos los estudiantes y atenciones de un mes específico, incluyendo sus UUIDs originales.

**Importar** (`procesar_importacion`):
1. Para cada estudiante del archivo: si el UUID ya existe en la BD local, se reutiliza. Si no, busca coincidencia exacta por nombre+curso+paralelo (por si se creó independientemente en ambas PCs). Si no hay coincidencia, se crea nuevo.
2. Para cada atención: si el UUID ya existe, se omite (ya se había importado antes). Si no hay conflicto de horario con ninguna atención existente del mismo estudiante/fecha, se inserta directo.
3. Si se detecta una atención con hora de llegada dentro de ±15 minutos de otra ya existente del mismo estudiante/fecha, se marca como **posible duplicado** y se muestra en una ventana de revisión manual (`_mostrar_revision_duplicados`), donde el usuario decide "Descartar" o "Importar de todas formas".

## 7. Reportes

- Tendencia mensual, diagnósticos más frecuentes (agrupando cualquier texto libre de "Otros" bajo una sola categoría), atenciones por curso EGB/Bachillerato.
- Sección filtrable por Curso + Paralelo específico (tendencia + diagnósticos de ese grupo).
- Tarjetas de métricas: total del mes, total global, promedio de atenciones por día activo.
- Alerta de estudiantes con **3+ visitas en la semana actual o 5+ en el mes actual** (`listar_estudiantes_frecuentes`), calculado sobre la fecha real del sistema. La misma lógica se usa para mostrar un aviso inline al seleccionar un estudiante en "Registrar atención".

## 8. Empaquetado y advertencia de "publicador no reconocido"

El `.exe` generado con PyInstaller no está firmado digitalmente. Windows 11 SmartScreen mostrará una advertencia la primera vez que se ejecute en cada PC. Esto **no depende del lenguaje de programación** — ocurre con cualquier ejecutable sin firma (Python, Java, C#, etc.).

Opciones para reducirlo:
- Certificado de firma de código (Code Signing), de pago.
- Aceptar la advertencia manualmente ("Más información" → "Ejecutar de todas formas") — suficiente para software interno de bajo volumen de instalación.

## 9. Limitaciones conocidas / deuda técnica

- No hay control de permisos por rol (todas las cuentas pueden editar/eliminar cualquier registro).
- La sincronización es manual (requiere USB/correo), no automática por red.
- No hay pruebas automatizadas (unit tests).
- El código del ícono de la ventana (`iconbitmap`) depende de un `after()` con retraso fijo, por una limitación conocida de CustomTkinter.
- La detección de duplicados en importación usa una ventana de ±15 minutos fija (no configurable desde la interfaz).
