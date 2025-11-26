import pprint

# 1. Definimos el tablero (0 es vacío)
# Ejemplo pequeño: Hay que ir del 1 al 2, y del 2 al 3, llenando todo.
tablero = [
    [1, 0, 0],
    [0, 0, 2],
    [0, 0, 3]
]

FILAS = len(tablero)
COLS = len(tablero[0])
TOTAL_CASILLAS = FILAS * COLS

# Buscamos dónde está el número más alto (meta final)
MAX_NUM = max(max(fila) for fila in tablero)

def encontrar_inicio():
    for r in range(FILAS):
        for c in range(COLS):
            if tablero[r][c] == 1:
                return (r, c)
    return None

def es_valido(r, c, visitados):
    # Verificar límites del tablero
    if not (0 <= r < FILAS and 0 <= c < COLS):
        return False
    # Verificar si ya pasamos por aquí
    if (r, c) in visitados:
        return False
    return True

def resolver(r, c, ultimo_num_visto, camino):
    # r, c: posición actual
    # ultimo_num_visto: el último checkpoint que pasamos (ej: 1)
    # camino: lista de tuplas con las coordenadas [(0,0), (0,1)...]
    
    # 1. ¿Hemos ganado? 
    # Si estamos en el número más alto Y hemos llenado todas las casillas
    if tablero[r][c] == MAX_NUM and len(camino) == TOTAL_CASILLAS:
        return camino

    # 2. Definir movimientos (Arriba, Abajo, Izq, Der)
    movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in movimientos:
        nr, nc = r + dr, c + dc # Nuevas coordenadas

        if es_valido(nr, nc, camino):
            valor_casilla = tablero[nr][nc]
            
            # CASO A: La casilla está vacía (0)
            if valor_casilla == 0:
                # Nos movemos ahí y seguimos buscando
                res = resolver(nr, nc, ultimo_num_visto, camino + [(nr, nc)])
                if res: return res # ¡Encontramos solución!
            
            # CASO B: La casilla tiene un número (Checkpoint)
            elif valor_casilla > 0:
                # Solo podemos entrar si es EXACTAMENTE el siguiente número (ej: 1 -> 2)
                if valor_casilla == ultimo_num_visto + 1:
                    res = resolver(nr, nc, valor_casilla, camino + [(nr, nc)])
                    if res: return res
            
            # Si no es ninguno (ej: saltar del 1 al 3), no hacemos nada (Backtracking)

    return None # Camino sin salida

# --- EJECUCIÓN ---
print("--- Buscando solución para ZIP ---")
inicio = encontrar_inicio()

if inicio:
    # Empezamos la recursividad desde el 1
    ruta_solucion = resolver(inicio[0], inicio[1], 1, [inicio])
    
    if ruta_solucion:
        print("¡Solución encontrada!")
        
        # Visualización simple en texto
        mapa_visual = [['.' for _ in range(COLS)] for _ in range(FILAS)]
        for i, (r, c) in enumerate(ruta_solucion):
            mapa_visual[r][c] = str(i + 1) # Marcamos el orden del paso
        
        pprint.pprint(mapa_visual)
        print(f"\nCoordenadas paso a paso: {ruta_solucion}")
    else:
        print("No se encontró solución (o el tablero está mal planteado).")
else:
    print("No encontré el número 1 en el tablero.")