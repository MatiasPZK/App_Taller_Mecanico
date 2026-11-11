"""
GESTION DEL TALLER:
    - Logica de negocio del taller mecanico
    - Funciones de gestion de clientes, vehiculos, ordenes y servicios
    - Maquina de estados para transicion de ordenes
    - Calculo automatico del 15% de IVA
"""
import datetime 
from core.persistencia import (
    leer_csv_como_diccionarios, 
    escribir_csv_completo, 
    agregar_registro_csv
)
from core.validaciones import (
    validar_texto, 
    validar_numero_positivo, 
    normalizar_patente
)

ESTADOS_ORDEN = ["Pendiente", "En Reparacion", "Finalizada", "Pagada", "Cancelada"]

# ========================================================
# 1. GESTION DE CLIENTES
# ========================================================

def listar_clientes() -> list[dict]:
    """Devuelve la lista de clientes registrados."""
    return leer_csv_como_diccionarios("clientes.csv")

def registrar_cliente(nombre: str, casa: str, numero_email: str) -> tuple[bool, str]:
    """Valida y registra un nuevo cliente devolviendo su ID generado."""
    ok_nom, res_nom = validar_texto(nombre, "Nombre")
    if not ok_nom:
        return False, res_nom
    
    ok_cont, res_cont = validar_texto(numero_email, "Contacto (Email/Telefono)")
    if not ok_cont:
        return False, res_cont

    clientes = listar_clientes()
    nuevo_id = str(len(clientes) + 1)

    nuevo_cliente = {
        "id_cliente": nuevo_id,
        "nombre": res_nom,
        "casa": casa.strip(),
        "numero_email": res_cont,
        "id_vehiculo": ""
    }

    if agregar_registro_csv("clientes.csv", nuevo_cliente):
        # Devuelve el ID directamente para poder vincularlo al vehiculo
        return True, nuevo_id
    return False, "Error de escritura al registrar el cliente."

# ========================================================
# 2. GESTION DE VEHICULOS
# ========================================================

def listar_vehiculos() -> list[dict]:
    """Devuelve la lista de vehiculos registrados."""
    return leer_csv_como_diccionarios("vehiculos.csv")

def registrar_vehiculo(id_cliente: str, tipo: str, marca: str, modelo_ano: str, patente: str) -> tuple[bool, str]:
    """Valida, asocia al cliente y persiste el vehiculo en el archivo."""
    ok_marca, res_marca = validar_texto(marca, "Marca")
    if not ok_marca:
        return False, res_marca

    ok_modelo, res_modelo = validar_texto(modelo_ano, "Modelo y Año")
    if not ok_modelo:
        return False, res_modelo

    ok_pat, res_pat = normalizar_patente(patente)
    if not ok_pat:
        return False, res_pat

    vehiculos = listar_vehiculos()
    for v in vehiculos:
        if v.get("patente", "").upper() == res_pat:
            return False, f"El vehículo con patente '{res_pat}' ya está registrado."

    nuevo_id = str(len(vehiculos) + 1)
    nuevo_vehiculo = {
        "id_vehiculo": nuevo_id,
        "id_cliente": str(id_cliente).strip(),
        "tipo": tipo.strip() if tipo.strip() else "Auto",
        "marca": res_marca,
        "modelo_anio": res_modelo,
        "patente": res_pat,
        "tarea_asignada": "Ninguna"
    }

    if agregar_registro_csv("vehiculos.csv", nuevo_vehiculo):
        # Actualiza la referencia del vehiculo en el registro del cliente
        clientes = listar_clientes()    
        for c in clientes:
            if c["id_cliente"] == str(id_cliente).strip():
                c["id_vehiculo"] = nuevo_id
                escribir_csv_completo("clientes.csv", clientes)
                break
        return True, nuevo_id
    return False, "Error de escritura al registrar el vehículo."

# ========================================================
# 3. CATALOGO DE SERVICIOS
# ========================================================

def listar_servicios() -> list[dict]:
    """Devuelve los servicios registrados en el catalogo."""
    return leer_csv_como_diccionarios("servicios.csv")

def registrar_servicio(categoria: str, detalles: str, precio: float) -> tuple[bool, str]:
    """Registra un servicio y calcula automaticamente el 15% de IVA."""
    ok_cat, res_cat = validar_texto(categoria, "Categoría")
    if not ok_cat:
        return False, res_cat

    ok_det, res_det = validar_texto(detalles, "Detalles")
    if not ok_det:
        return False, res_det

    ok_prec, res_prec = validar_numero_positivo(precio, "Precio")
    if not ok_prec:
        return False, str(res_prec)

    precio_float = float(res_prec)
    total_con_iva = round(precio_float * 1.15, 2)

    servicios = listar_servicios()
    nuevo_id = str(len(servicios) + 1)

    nuevo_servicio = {
        "id_servicio": nuevo_id,
        "detalles": res_det,
        "categoria": res_cat,
        "precio": f"{precio_float:.2f}",
        "total_iva": f"{total_con_iva:.2f}"
    }

    if agregar_registro_csv("servicios.csv", nuevo_servicio):
        return True, "Servicio registrado correctamente."
    return False, "Error de escritura al registrar el servicio."

# ========================================================
# 4. ORDENES DE TRABAJO
# ========================================================

def listar_ordenes() -> list[dict]:
    """Devuelve el listado completo de ordenes registradas."""
    return leer_csv_como_diccionarios("ordenes.csv")

def crear_orden(nombre_cliente: str, info_vehiculo: str, tipo_tarea: str, total_iva: float, mecanico: str) -> tuple[bool, str]:
    """Crea una nueva orden de trabajo en estado inicial 'Pendiente'."""
    ok_cli, res_cli = validar_texto(nombre_cliente, "Nombre del Cliente")
    if not ok_cli:
        return False, res_cli

    ok_veh, res_veh = validar_texto(info_vehiculo, "Información del Vehículo")
    if not ok_veh:
        return False, res_veh

    ok_tot, res_tot = validar_numero_positivo(total_iva, "Total con IVA")
    if not ok_tot:
        return False, str(res_tot)

    ok_mec, res_mec = validar_texto(mecanico, "Mecánico Asignado")
    if not ok_mec:
        return False, res_mec

    ordenes = listar_ordenes()
    nuevo_id = str(len(ordenes) + 1)
    fecha_actual = datetime.date.today().strftime("%Y-%m-%d")

    nueva_orden = {
        "id_orden": nuevo_id,
        "fecha": fecha_actual,
        "cliente": res_cli,
        "marca_modelo_patente": res_veh,
        "tipo_tarea": tipo_tarea.strip() if tipo_tarea.strip() else "Reparación General",
        "total": f"{float(res_tot):.2f}",
        "estado": "Pendiente",
        "metodo_pago": "Pendiente",
        "mecanico_asignado": res_mec
    }

    if agregar_registro_csv("ordenes.csv", nueva_orden):
        return True, nuevo_id
    return False, "Error al persistir la orden de trabajo."

# Alias por compatibilidad
registrar_orden = crear_orden

def transicionar_estado_orden(id_orden: str, nuevo_estado: str, metodo_pago: str = None) -> tuple[bool, str]:
    """Aplica la maquina de estados a la orden de trabajo."""
    if nuevo_estado not in ESTADOS_ORDEN:
        return False, f"Estado no válido. Permitidos: {', '.join(ESTADOS_ORDEN)}"

    ordenes = listar_ordenes()
    orden_encontrada = None

    for o in ordenes:
        if str(o.get("id_orden")) == str(id_orden):
            orden_encontrada = o
            break

    if not orden_encontrada:
        return False, f"No se encontró la orden con ID #{id_orden}."

    estado_actual = orden_encontrada.get("estado", "Pendiente")

    transiciones_validas = {
        "Pendiente": ["En Reparacion", "Cancelada"],
        "En Reparacion": ["Finalizada", "Cancelada"],
        "Finalizada": ["Pagada"],
        "Pagada": [],
        "Cancelada": []
    }

    if nuevo_estado not in transiciones_validas.get(estado_actual, []):
        return False, f"Transición inválida de '{estado_actual}' a '{nuevo_estado}'."

    orden_encontrada["estado"] = nuevo_estado
    if metodo_pago:
        orden_encontrada["metodo_pago"] = metodo_pago

    if escribir_csv_completo("ordenes.csv", ordenes):
        return True, f"Estado de la orden #{id_orden} actualizado a '{nuevo_estado}'."
    return False, "Error al actualizar la orden en el archivo."