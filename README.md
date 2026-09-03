# Sistema de Enfermería Escolar — AMMI

Aplicación de escritorio para registrar, consultar y sincronizar las atenciones de enfermería del departamento médico escolar. Funciona **100% sin conexión a internet**, pensada para instalarse en dos computadoras que trabajan en red local y sincronizan sus registros periódicamente.

## Índice
- [Características](#características)
- [Tecnologías](#tecnologías)
- [Requisitos previos](#requisitos-previos)
- [Instalación (entorno de desarrollo)](#instalación-entorno-de-desarrollo)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Uso básico](#uso-básico)
- [Empaquetado (.exe)](#empaquetado-exe)
- [Licencia](#licencia)

## Características

- **Registro de atenciones**: nombre (con autocompletado), curso, paralelo/especialidad, sexo, saturación, temperatura, frecuencia cardíaca, diagnóstico (con opción "Otros") y recomendación.
- **Paralelo dinámico**: A/B/C/D para cursos de Inicial a 10mo BCG; especialidades técnicas (Informática, Diseño Gráfico, Mecánica Automotriz, Servicios Hoteleros) para Bachillerato.
- **Atenciones pendientes**: lista global (sin importar la fecha) de atenciones sin hora de salida registrada.
- **Historial de atenciones**: búsqueda, edición y eliminación de cualquier registro pasado.
- **Reportes con gráficas**: tendencia mensual, diagnósticos más frecuentes, atenciones por curso (EGB/Bachillerato), filtro por curso y paralelo específico, métricas globales, y alertas de estudiantes con visitas frecuentes (3+/semana o 5+/mes).
- **Exportación**: a `.json` (para sincronizar con la otra PC) y a `.xlsx` (Excel, con formato).
- **Sincronización entre 2 PCs**: exporta/importa datos por mes, fusiona automáticamente evitando duplicados, y permite revisar manualmente los casos ambiguos.
- **Login de usuarios**: cada atención queda asociada a quién la registró; sesión con expiración por inactividad.
- **Interfaz con tema institucional** (colores amarillo/negro), sin depender de internet.

## Tecnologías

| Componente | Herramienta |
|---|---|
| Lenguaje | Python 3.12 |
| Interfaz gráfica | CustomTkinter |
| Base de datos | SQLite (archivo local, sin servidor) |
| Gráficas | Matplotlib |
| Exportación a Excel | OpenPyXL |
| Empaquetado a `.exe` | PyInstaller |

## Requisitos previos

- **Python 3.12** (evitar 3.14+ por problemas de compatibilidad con algunas librerías al momento de escribir esto).
- **Windows 10/11** (probado en este entorno; el código base es multiplataforma pero no se ha probado en Mac/Linux).

## Instalación (entorno de desarrollo)

```bash
# 1. Clonar el repositorio
git clone https://github.com/<usuario>/sistema-enfermeria-escolar.git
cd sistema-enfermeria-escolar

# 2. Crear entorno virtual con Python 3.12
py -3.12 -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python src/main.py
```

Al primer inicio, el sistema pedirá:
1. Identificar esta computadora como **PC1** o **PC2** (una sola vez).
2. Crear una cuenta de usuario (usuario, contraseña y código de autorización).

## Estructura del proyecto

```
sistema-enfermeria-escolar/
├── assets/                     # logo, ícono de la app
├── data/                       # BD SQLite y configuración local (no se sube a Git)
├── src/
│   ├── main.py                 # punto de entrada
│   ├── auth.py                 # login, hashing de contraseñas, sesión
│   ├── config.py                # identificación de la PC (PC1/PC2)
│   ├── database/
│   │   ├── modelos.py          # creación de tablas
│   │   └── consultas.py        # funciones CRUD y consultas
│   └── gui/
│       ├── vista_principal.py       # ventana principal / menú
│       ├── vista_login.py           # pantalla de inicio de sesión
│       ├── vista_atenciones.py      # registrar atención
│       ├── vista_pendientes.py      # atenciones sin hora de salida
│       ├── vista_estudiantes.py     # historial de atenciones
│       ├── vista_reportes.py        # gráficas y métricas
│       ├── vista_sincronizacion.py  # exportar/importar entre PCs
│       ├── constantes.py            # listas de cursos, paralelos, diagnósticos
│       ├── estilos.py               # colores y fuentes reutilizables
│       └── tema_escuela.json        # tema visual de CustomTkinter
├── requirements.txt
├── .gitignore
└── README.md
```

## Uso básico

1. **Registrar atención**: buscar/escribir el nombre del estudiante (autocompleta si ya existe), completar curso/paralelo/sexo y los datos clínicos, guardar.
2. **Marcar salida**: desde la tabla del día o desde "Atenciones pendientes".
3. **Historial**: buscar, editar o eliminar cualquier atención pasada.
4. **Reportes**: revisar tendencias, diagnósticos frecuentes y estudiantes con visitas repetidas.
5. **Sincronización** (al final del día/semana): exportar el mes desde una PC, llevar el archivo a la otra (USB o correo), e importarlo ahí.

## Empaquetado (.exe)

```bash
pyinstaller --onefile --windowed --icon=assets/icono.ico src/main.py
```

> Nota: el `.exe` generado no está firmado digitalmente, por lo que Windows 11 puede mostrar una advertencia de "publicador no reconocido" la primera vez que se ejecuta. Ver la sección correspondiente en `DOCUMENTACION.md` para más detalle.

## Licencia

Uso interno — Departamento de Enfermería, Unidad Educativa AMMI.