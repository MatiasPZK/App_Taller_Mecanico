# Taller Motor - Sistema Integral de Gestión

Sistema de escritorio profesional para la administración y control operativo de un taller mecánico automotriz. Desarrollado en **Python** con **CustomTkinter**, implementa una arquitectura modular desacoplada (`core` / `views`), control de acceso por roles (RBAC) y persistencia en archivos planos CSV.

---

## Tecnologías y Librerías

- **Lenguaje:** Python 3.10+
- **Interfaz Gráfica:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Diseño Dark Neon / Cyber Dashboard)
- **Componentes Tabulares:** `tkinter.ttk` (Treeviews con personalización de temas oscuros)
- **Seguridad:** Encriptación y verificación de contraseñas mediante hashing `SHA-256`
- **Persistencia:** Archivos planos `CSV` con codificación estándar `UTF-8`

---

## Características del Sistema

- **Control de Acceso Basado en Roles (RBAC):**
  - **Administrador (`ADMIN`):** Acceso integral al sistema, alta y baja lógica de usuarios, métricas financieras y visualización de la matriz de rendimiento.
  - **Recepción / Ventas (`RECEPCIONISTA (ventas)`):** Registro de clientes y vehículos, cotización, generación de órdenes de servicio y cobro/facturación.
  - **Mecánico (`MECANICO`):** Bandeja operativa de tareas asignadas y actualización de estados del vehículo (`Pendiente` ➔ `En Reparación` ➔ `Finalizada`).
- **Matriz Analítica de Rendimiento:** Algoritmo dinámico bidimensional que procesa y cruza los servicios realizados frente a los mecánicos asignados, totalizando por rubro, por operario y facturación global.
- **Persistencia Robusta:** Auto-inicialización de la carpeta `data/` y generación de cabeceras oficiales junto a registros semilla iniciales si los archivos no existen o se encuentran vacíos.
- **Cálculo Impositivo:** Desglose automático de importes brutos y cálculo de alícuotas impositivas (IVA).

---

## 📂 Estructura del Proyecto

```text
App_Taller_Mecanico/
├── data/                    # Archivos de persistencia CSV (auto-generados)
│   ├── clientes.csv
│   ├── ordenes.csv
│   ├── servicios.csv
│   ├── usuarios.csv
│   └── vehiculos.csv
├── core/                    # Lógica de negocio y persistencia
│   ├── __init__.py
│   ├── auth.py              # Sesiones activas, hashing SHA-256 y roles
│   ├── gestion_taller.py    # Gestión de órdenes, clientes y vehículos
│   ├── persistencia.py      # Control de lectura, escritura e inicialización CSV
│   ├── reportes.py          # Lógica de cálculo de la matriz analítica
│   └── validaciones.py      # Sanitización y validaciones de entrada
├── views/                   # Interfaz gráfica de usuario
│   ├── __init__.py
│   ├── app.py               # Contenedor principal, sidebar y ruteador
│   ├── views_auth.py        # Login y administración de operadores
│   ├── views_finanzas.py    # Gestión de cobros y facturación
│   ├── views_mecanico.py    # Panel operativo de taller
│   ├── views_recepcion.py   # Recepción, clientes y órdenes
│   └── views_reportes.py    # Tablero de métricas y tabla matricial
├── main.py                  # Punto de entrada de la aplicación
├── requirements.txt         # Dependencias externas
└── README.md                # Documentación del proyecto
```
---

## **‼️Pasos para la EJECUCION**

### 1. Clonar el REPOSITORIO
```
git clone https://github.com/tu-usuario/App_Taller_Mecanico.git
cd App_Taller_Mecanico
```
### 2. Crear el entorno VIRTUAL
Windows:
```
python -m venv venv
.\venv\Scripts\activate
```
Linux / MacOS:
```
python3 -m venv venv
source venv/bin/activate
```
### 3. Instalar DEPENDENCIAS
```
pip install customtkinter
```
### 4. Iniciar la APLICACION
```
python main.py
```
> Nota: _Al ejecutar por primera vez, el sistema creará automáticamente la carpeta ```data/``` con todos los archivos CSV y los datos iniciales necesarios para operar._
---
## 🔒 Credenciales de Prueba 

| Rol | Usuario | Contraseña | Permisos |
| --- | --- | --- | --- |
| Administrador | admin | admin123 | Control total del sistema, reportes y usuarios |
| Recepcionista | recepcion | recepcion123 | Alta de clientes, vehículos, órdenes y cobros |
| Mecanico | mecanico | mecanico123 | Visualización de tareas y cambio de estados |
---
## Guia de COMMITS

El control de versiones del repositorio sigue el estándar de **Conventional Commits**:
- ```feat(...)```: Incorporación de nuevas funcionalidades o pantallas.
- ```fix(...)```: Corrección de errores o fallos en persistencia/vistas.
- ```refactor(...)```: Mejoras estructurales de código sin modificar la lógica externa.
- ```docs(...)```: Actualización de guías, comentarios y documentación del proyecto.

## **MUCHAS GRACIAS ♥️**
