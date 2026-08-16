from database.consultas import crear_estudiante, crear_atencion, listar_atenciones_por_fecha

# Crear un estudiante de prueba
id_est = crear_estudiante(
    codigo_estudiante="EST001",
    nombres="Juan",
    apellidos="Pérez",
    curso_grado="8vo A",
    alergias="Ninguna"
)
print("Estudiante creado con id:", id_est)

# Registrar una atención para ese estudiante
id_atencion = crear_atencion(
    estudiante_id=id_est,
    motivo_consulta="Dolor de cabeza",
    observaciones="Se le dio reposo 15 minutos"
)
print("Atención creada con id:", id_atencion)

# Listar atenciones del día
from datetime import datetime
hoy = datetime.now().strftime("%Y-%m-%d")
print(listar_atenciones_por_fecha(hoy))