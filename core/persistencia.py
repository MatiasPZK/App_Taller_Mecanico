# Lectura/escritura CSV con try-except y datos semilla

import os
import csv
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

HEADERS = {
    "usuarios.csv": ["id_usuario", "username", "password_hash", "rol", "activo"],
    "clientes.csv": ["id_cliente", "nombre", "casa", "numero_email", "id_vehiculo"],
    "vehiculos.csv": ["id_vehiculo", "id_cliente", "tipo", "marca", "modelo_anio", "patente", "tarea_asignada"],
    "servicios.csv": ["id_servicio", "detalles", "categoria", "precio", "total_iva"],
    "ordenes.csv": ["id_orden", "fecha", "cliente", "marca_modelo_patente", "tipo_tarea", "total", "estado", "metodo_pago", "mecanico_asignado"]
}

# Datos iniciales para que el sistema funcione apenas arranca
DATOS_SEMILLA = {
    "usuarios.csv": [
        {
            "id_usuario": "1",
            "username": "admin",
            "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
            "rol": "ADMIN",
            "activo": "true"
        },
        {
            "id_usuario": "2",
            "username": "recepcion",
            "password_hash": hashlib.sha256("recep123".encode()).hexdigest(),
            "rol": "RECEPCIONISTA (ventas)",
            "activo": "true"
        },
        {
            "id_usuario": "3",
            "username": "mecanico1",
            "password_hash": hashlib.sha256("meca123".encode()).hexdigest(),
            "rol": "MECANICO",
            "activo": "true"
        }
    ],
    "servicios.csv": [
        {"id_servicio": "1", "detalles": "Cambio de Aceite y Filtro", "categoria": "Mantenimiento", "precio": "15000.00", "total_iva": "17250.00"},
        {"id_servicio": "2", "detalles": "Pastillas de Freno", "categoria": "Frenos", "precio": "25000.00", "total_iva": "28750.00"},
        {"id_servicio": "3", "detalles": "Alineacion y Balanceo", "categoria": "Tren Delantero", "precio": "18000.00", "total_iva": "20700.00"}
    ]
}

def obtener_ruta(nombre_Archivos: str) -> str:
    return os.path.join(DATA_DIR, nombre_Archivos)

def inicializar_archivos():
    os.makedirs(DATA_DIR, exist_ok=True)
    for nombre, cabeceras in HEADERS.items():
        ruta = obtener_ruta(nombre)
        # Si no existe o si pesa 0 bytes (vacío corrupto), se inicializa
        if not os.path.exists(ruta) or os.path.getsize(ruta) == 0:
            try:
                with open(ruta, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=cabeceras)
                    writer.writeheader()
                    # Si tiene datos semilla (usuarios o servicios iniciales), los escribe
                    if nombre in DATOS_SEMILLA:
                        writer.writerows(DATOS_SEMILLA[nombre])
            except IOError as e:
                print(f"[Error Persistencia] {e}")

def leer_csv_como_diccionarios(nombre_archivo: str) -> list[dict]:
    ruta = obtener_ruta(nombre_archivo)
    if not os.path.exists(ruta) or os.path.getsize(ruta) == 0:
        inicializar_archivos()
    try:
        with open(ruta, mode="r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except (IOError, csv.Error):
        return []

def escribir_csv_completo(nombre_archivo: str, registros: list[dict]) -> bool:
    ruta = obtener_ruta(nombre_archivo)
    cabeceras = HEADERS.get(nombre_archivo, list(registros[0].keys()) if registros else [])
    try:
        with open(ruta, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cabeceras)
            writer.writeheader()
            writer.writerows(registros)
        return True
    except IOError:
        return False

def agregar_registro_csv(nombre_archivo: str, nuevo_registro: dict) -> bool:
    ruta = obtener_ruta(nombre_archivo)
    if not os.path.exists(ruta) or os.path.getsize(ruta) == 0:
        inicializar_archivos()
    cabeceras = HEADERS.get(nombre_archivo, list(nuevo_registro.keys()))
    try:
        with open(ruta, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cabeceras)
            writer.writerow(nuevo_registro)
        return True
    except IOError:
        return False