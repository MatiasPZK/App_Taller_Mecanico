"""
validaciones.py sirve para limpiar, validar y asegurar que los datos
ingresados por el usuario sean correctos antes de que el sistema los procese.
"""

def validar_texto(texto: str, nombre_campo: str = "Campo") -> tuple[bool, str]:
    #verifica que una cadena no este vacia ni contenga solo espacios en blanco
    if not isinstance(texto,str) or not texto.strip():
        return False, f"El campo '{nombre_campo}' no puede estar vacio"
    return True, texto.strip()

def validar_numero_positivo(valor, nombre_campo: str = "Precio/Monto") -> tuple[bool, str]:
    #convierte y valida que un valor numerico sea de tipo float y positivo
    try:
        numero = float(valor)
        if numero <= 0:
            return False, f"El campo '{nombre_campo}' debe ser mayor a 0"
        return True, numero
    except (ValueError, TypeError):
        return False, f"El campo '{nombre_campo}' debe ser un valor numerico valido"

def normalizar_patente(patente: str) -> tuple[bool, str]:
    #limpia y valida el formato base de la patente del vehiculo
    ok, resultado = validar_texto(patente, "Patente")
    if not ok:
        return False, resultado

    patente_limpia = resultado.replace(" ", " ").replace("-", "").upper()
    if len(patente_limpia) < 6 or len(patente_limpia) > 8:
        return False, "La pantente ingresada es muy larga (debe ser mayor a 6 y menor a 8)"
    return True, patente_limpia
