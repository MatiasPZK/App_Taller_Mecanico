#auth.py - Control de Acceso y Gestión de Usuarios

import hashlib
from core.persistencia import leer_csv_como_diccionarios, escribir_csv_completo, agregar_registro_csv

ROLES_VALIDOS = ["ADMIN", "RECEPCIONISTA", "MECANICO"]

def hash_contrasena(password: str) -> str:
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()

class SesionManager:
    usuario_actual = None

    @classmethod
    def iniciar_sesion(cls, username: str, password_plano: str) -> tuple[bool,str]:
        username = username.strip()
        if not username or not password_plano:
            return False, "Usuario y contraseña no pueden estar vacios."

        usuarios = leer_csv_como_diccionarios("usuarios.csv")
        pass_hash = hash_contrasena(password_plano)

        for u in usuarios:
            if u["username"].lower() == username.lower():
                if u["activo"].lower() != "true":
                    return False, "Lacuenta esta inactiva."
                if u["password_hash"] == pass_hash:
                    cls.usuario_actual = u
                    return True, f"Bienvenido/a {u['username']}"
                return False, "Contraseña incorrecta."
        return False, "El usuario no existe."

    @classmethod
    def cerrar_sesion(cls):
        cls.usuario_actual = None

    @classmethod
    def tiene_permiso(cls, roles_permitidos: list[str]) -> bool:
        return cls.usuario_actual is not None and cls.usuario_actual.get("rol") in roles_permitidos

def registrar_usuario(username: str, password_plano: str, rol:str) -> tuple[bool, str]:
    if not SesionManager.tiene_permiso(["ADMIN"]):
        return False, "Solo administradores pueden crear usuarios."
    if rol not in ROLES_VALIDOS:
        return False, "Rol no admitido."
    #aca compara si ya existe ese usuario
    usuarios = leer_csv_como_diccionarios("usuarios.csv")
    if any(u["username"].lower()==username.strip().lower() for u in usuarios):
        return False, "El usuario ya existe"
    #aca guarda el nuevo usuario con los datos que se fueron creando en un diccionario
    nuevo = {
        "id_usuario": str(len(usuarios) + 1),
        "username": username.strip(),
        "password_hash": hash_contrasena(password_plano),
        "rol": rol,
        "activo": "True"
    }
    return (True, "usuario registrado.") if agregar_registro_csv("usuarios.csv", nuevo) else (False, "error al guardar")

def dar_baja_usuario(id_usuario: str) -> tuple[bool, str]:
    #si no sos admin, no podes dar de baja a usuarios
    if not SesionManager.tiene_permiso(["ADMIN"]):
        return False, "Permiso denegado"
    #verificar si el usuario actual es un admin y si se quiere eliminarse a si mismo
    if str(SesionManager.usuario_actual["id_usuario"])==str(id_usuario):
        return False, "Regla RBAC: un administrador no puede eliminarse a sí mismo."
    usuarios = leer_csv_como_diccionarios("usuarios.csv")
    target = None
    admins_activos = 0

    for u in usuarios:
        if u["activo"].lower() == "true" and u["rol"] == "ADMIN":
            admins_activos += 1
        if str(u["id_usuario"]) == str(id_usuario):
            target = u

    if not target:
        return False, "Usuario no encontrado."
    #Si la etiqueta de rol es admin y los admins activos es menor a 1, no se puede 
    #eliminar a ese administrador ya que es el unico que queda
    if target["rol"] == "ADMIN" and admins_activos <=1:
        return False, "Regla RBAC: no se puede eliminar al unico administrador activo"
    #da de baja al usuario
    target["activo"] = "False"
    return (True, "Usuario desactivado.") if escribir_csv_completo("usuario.csv", usuarios) else (False, "Error de escritura.")
