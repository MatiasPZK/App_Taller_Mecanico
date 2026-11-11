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

    @classmethod
    def obtener_rol(cls) -> str:
        """Devuelve el rol del usuario actualmente autenticado."""
        if cls.usuario_actual:
            return cls.usuario_actual.get("rol", "INVITADO")
        return "INVITADO"

    @classmethod
    def obtener_usuario_actual(cls) -> dict | None:
        """Devuelve el diccionario con los datos del usuario logueado."""
        return cls.usuario_actual

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
    """Marca un usuario como inactivo (baja lógica) y actualiza el CSV."""
    usuarios = obtener_todos_usuarios()
    usuario_encontrado = None

    for u in usuarios:
        if str(u.get("id_usuario")) == str(id_usuario):
            usuario_encontrado = u
            break

    if not usuario_encontrado:
        return False, f"Usuario con ID #{id_usuario} no encontrado."

    if usuario_encontrado.get("rol") == "ADMIN":
        return False, "No se puede dar de baja a un Administrador."

    # Baja lógica
    usuario_encontrado["activo"] = "false"

    # Persiste sobre data/usuarios.csv sin crear archivos duplicados
    if escribir_csv_completo("usuarios.csv", usuarios):
        return True, f"Usuario '{usuario_encontrado.get('username')}' dado de baja correctamente."
    return False, "Error al guardar los cambios en el archivo."

def obtener_todos_usuarios() -> list[dict]:
    """Devuelve la lista completa de usuarios registrados en el sistema."""
    return leer_csv_como_diccionarios("usuarios.csv")