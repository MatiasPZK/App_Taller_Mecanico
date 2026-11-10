"""
GESTION DEL TALLER:
    -Logica de negocio del taller mecanico
    -Funciones de gestion de ordenes, servicios y usuarios
    -Calculo de rendimientos y reportes (15% de IVA)
"""
import datetime 
from core.persistencia import leer_csv_como_diccionarios, escribir_csv_completo, agregar_registro_csv
from core.validaciones import validar_texto, validar_numero_positivo, normalizar_patente

ESTADOS_ORDEN = ["Pendiente", "En Reparacion", "Finalizada", "Pagada", "Cancelada"]

#Gestion de clientes.

def listar_clientes() -> list[dict]:
    #devuelve una lista de diccionario con los clientes
    return leer_csv_como_diccionarios("clientes.csv")

def registrar_cliente(nombre: str, casa: str, numero_email: str) -> tuple[bool, str]:
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
        "nombre": nombre.strip(),
        "casa": casa.strip(),
        "contacto": res_cont.strip(),
        "id_vehiculo": ""
    }

    if agregar_registro_csv("clientes.csv", nuevo_cliente):
        return True, f"Cliente registrado con ID: {nuevo_id}"
    else:
        return False, "Error de escritura. Intente nuevamente."

#gestion de vehiculos
def listar_vehiculos() -> list[dict]:
    #devuelve una lista de diccionario con los vehiculos
    return leer_csv_como_diccionarios("vehiculos.csv")

def registrar_vehiculo(id_cliente: str, tipo: str, marca: str, modelo_ano: str, patente: str) -> tuple[bool, str]:

    ok_marca, res_marca = validar_texto(marca, "Marca")
    if not ok_marca:
        return False, res_marca

    ok_modelo, res_modelo = validar_texto(modelo_ano , "Modelo y Año")
    if not ok_modelo:
        return False, res_modelo

    ok_pat, res_pat = normalizar_patente(patente)
    if not ok_pat:
        return False, res_pat

    vehiculos = listar_vehiculos()
    nuevo_id = str(len(vehiculos) + 1)

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
        clientes = listar_clientes()    
        for c in clientes:
            if c["id_cliente"] == str(id_cliente).strip():
                c["id_vehiculo"] = nuevo_id
                escribir_csv_completo("clientes.csv", clientes)
                break
        return True, f"Vehículo registrado con ID: {nuevo_id}"
    return False, "Error de escritura. Intente nuevamente."

#SERVICIOS
def listar_servicios() -> list[dict]:
    #devuelve una lista de diccionario con los servicios
    return leer_csv_como_diccionarios("servicios.csv")

def registrar_servicio(detalles: str, categoria: str, precio: float) -> tuple[bool, str]:
    ok_cat, res_cat = validar_texto(categoria, "Categoría")
    if not ok_cat:
        return False, res_cat
    ok_det, res_det = validar_texto(detalles, "Detalles")
    if not ok_det:
        return False, res_det
    ok_prec, res_prec = validar_numero_positivo(precio, "Precio")
    if not ok_prec:
        return False, res_prec

    precio_float = float(res_prec)
    total_con_iva = round(precio_float * 1.15, 2)

    servicios = listar_servicios()
    nuevo_id = str(len(servicios) + 1)

    nuevo_servicio = {
        "id_servicio": nuevo_id,
        "detalles": res_det,
        "categoria": res_cat,
        "precio": f"{precio_float:.2f}",
        "total_con_iva": f"{total_con_iva:.2f}"
    }

    if agregar_registro_csv("servicios.csv", nuevo_servicio):
        return True, f"Servicio registrado con ID: {nuevo_id}"
    return False, "Error de escritura. Intente nuevamente."

#ORDENES DE TRABAJO
def listar_ordenes() -> list[dict]:
    #devuelve una lista de diccionario con las ordenes
    return leer_csv_como_diccionarios("ordenes.csv")

def registrar_orden(nombre_cliente: str, info_vehiculo: str, tipo_tarea: str, total_iva: str, mecanico: str) -> tuple[bool, str]:
    ok_cli, res_cli = validar_texto(nombre_cliente, "Nombre del Cliente")
    if not ok_cli:
        return False, res_cli

    ok_veh, res_veh = validar_texto(info_vehiculo, "Información del Vehículo")
    if not ok_veh:
        return False, res_veh

    ok_tot, res_tot = validar_numero_positivo(total_iva, "Total con IVA")
    if not ok_tot:
        return False, res_tot

    ok_mec, res_mec = validar_texto(mecanico, "Mecánico Asignado")
    if not ok_mec:
        return False, res_mec

    ordenes = listar_ordenes()
    nuevo_id = str(len(ordenes) + 1)
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    nueva_orden = {
        "id_orden": nuevo_id,
        "fecha": fecha_actual,
        "cliente": res_cli,
        "marca_modelo_patente": res_veh,
        "tipo_tarea": tipo_tarea.strip() if tipo_tarea.strip() else "Reparación General",
        "total_con_iva": f"{float(res_tot):.2f}",
        "estado": "Pendiente",
        "monto_pago": "Pendiente",
        "mecanico_asignado": res_mec
    }

    if agregar_registro_csv("ordenes.csv", nueva_orden):
        return True, f"Orden registrada con ID: {nuevo_id}"
    return False, "Error al persistir la orden de trabajo, intente nuevamente."

def transicionar_estado_orden(id_orden: str, nuevo_estado: str, metodo_pago: str = None) -> tuple[bool, str]:
    """aplica la maquina de estados a la orden de trabajo, permitiendo transiciones entre estados definidos en ESTADOS_ORDEN"""
    if nuevo_estado not in ESTADOS_ORDEN:
        return False, f"Estado no válido. Estados permitidos: {', '.join(ESTADOS_ORDEN)}"

    ordenes = listar_ordenes()
    orden_encontrada = None

    for o in ordenes:
        if str(o["id_orden"]) == str(id_orden):
            orden_encontrada = o
            break

    if not orden_encontrada:
        return False, "Orden no encontrada."

    estado_actual = orden_encontrada["estado"]

    transiciones_validas = {
        "Pendiente": ["En Reparacion", "Cancelada"],
        "En Reparacion": ["Finalizada", "Cancelada"],
        "Finalizada": ["Pagada"],
        "Pagada": [],
        "Cancelada": []
    }

    if nuevo_estado not in transiciones_validas(estado_actual, []):
        return False, f"Transición inválida de '{estado_actual}' a '{nuevo_estado}'."

    orden_encontrada["estado"] = nuevo_estado
    if metodo_pago:
        orden_encontrada["monto_pago"] = metodo_pago

    if escribir_csv_completo("ordenes.csv", ordenes):
        return (True, f"Estado de la orden {id_orden} actualizado a '{nuevo_estado}'.")
    return (False, "Error al actualizar la orden. Intente nuevamente.")
    