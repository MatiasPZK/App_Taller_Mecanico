"""
reportes.py - Matriz analítica bidimensional
aca se genera la matriz analitica no hardcodeada que pedia la consigna
"""
from core.persistencia import leer_csv_como_diccionarios

def generar_matriz_rendimiento() -> dict:
    ordenes = leer_csv_como_diccionarios("ordenes.csv")
    servicios = leer_csv_como_diccionarios("servicios.csv")
    usuarios = leer_csv_como_diccionarios("usuarios.csv")
    #guardamos la cantidad de categorias y mecanicos
    categorias = sorted(list(set(s.get("categoria", "").strip() for s in servicios if s.get("categoria")))) or ["General"]
    mecanicos = sorted([u["username"] for u in usuarios if u.get("rol") == "MECANICO" and u.get("activo", "").lower() == "true"]) or ["Sin Asignar"]
    
    #guardamos lo anterior en estas 2 variables
    num_filas = len(categorias)
    num_cols = len(mecanicos)

    #armamos la matriz categorias x mecanicos
    matriz = [[0.0 for _ in range(num_cols)] for _ in range(num_filas)]
    for ord_item in ordenes:
        #si algunas de las ordenes estan finalizadas guarda la informacion 
        #de esta para devolver el monto
        if ord_item.get("estado") in ["Finalizada", "Entregada", "Pagada"]:
            cat = ord_item.get("tipo_tarea", "").strip()
            mec = ord_item.get("mecanico_asignado", "").strip()
            try:
                monto = float(ord_item.get("total", 0))
            except ValueError:
                monto = 0.0

            if cat in categorias and mec in mecanicos:
                matriz[categorias.index(cat)][mecanicos.index(mec)] += monto

    totales_filas = [0.0] * num_filas
    totales_columnas = [0.0] * num_cols
    gran_total = 0.0

    for i in range(num_filas):
        for j in range(num_cols):
            valor = matriz[i][j]
            totales_filas[i] += valor
            totales_columnas[j] += valor
            gran_total += valor

    return {
        "categorias": categorias,
        "mecanicos": mecanicos,
        "matriz": matriz,
        "totales_filas": totales_filas,
        "totales_columnas": totales_columnas,
        "gran_total": gran_total
    }