#Lectura/escritura CSV con try-except

import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

HEADERS = {
    "usuarios.csv": ["id_usuario", "username", "password_hash", "rol", "activo"],
    "clientes.csv": ["id_cliente", "nombre", "casa", "numero_email", "id_vehiculo"],
    "vehiculos.csv": ["id_vehiculo", "id_cliente", "tipo", "marca", "modelo_anio", "patente", "tarea_asignada"],
    "servicios.csv": ["id_servicio", "detalles", "categoria", "precio", "total_iva"],
    "ordenes.csv": ["id_orden", "fecha", "cliente", "marca_modelo_patente", "tipo_tarea", "total", "estado", "metodo_pago", "mecanico_asignado"]
}

def obtener_ruta(nombre_Archivos: str) -> str:
    return os.path.join(DATA_DIR, nombre_Archivos)

def inicializar_archivos():
    os.makedirs(DATA_DIR, exist_ok=True)
    for nombre, cabeceras in HEADERS.item():
        ruta = obtener_ruta(nombre)
        if not os.path.exist(ruta):
            try:
                with open(ruta, mode="w", newline="",encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(cabeceras)
            except IOError as e:
                print(f"[Error Persistencia] {e}")

def leer_csv_como_diccionarios(nombre_archivo: str) -> list[dict]:
    ruta = obtener_ruta(nombre_archivo)
    if not os.path.exists(ruta):
        inicializar_archivos()
    try:
        with open(ruta, mode="r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except(IOError, csv.Error):
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
    if not os.path.exists(ruta):
        inicializar_archivos()
    cabeceras = HEADERS.get(nombre_archivo, list(nuevo_registro.keys()))
    try:
        with open(ruta, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cabeceras)
            writer.writerow(nuevo_registro)
        return True
    except IOError:
        return False
