"""Exploracion del arbol de jugadas con backtracking (Semana 2, Dia 1).

El modelo ya sabe aplicar y deshacer movimientos (hacer_movimiento /
deshacer_movimiento). Este script usa ese mecanismo para recorrer
TODAS las partidas posibles desde el tablero vacio: baja por una rama
aplicando movimientos y retrocede con deshacer_movimiento para probar
la siguiente. Es el mismo recorrido que hara Minimax en los dias
siguientes, pero aqui solo contamos nodos, sin elegir jugadas.

Uso:
    python3.13 tools/explorar_arbol.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

from model.game_model import GameModel  # noqa: E402

# Contadores del recorrido
nodos = 0
nodos_por_profundidad = {}
ganadas_x = 0
ganadas_o = 0
empates = 0


def explorar(modelo, profundidad, profundidad_max, traza=False):
    """Recorre el arbol de jugadas aplicando y deshaciendo movimientos.

    En cada nodo: si la partida termino, cuenta el resultado; si no,
    prueba cada casilla libre, baja recursivamente y retrocede.
    """
    global nodos
    nodos += 1
    nodos_por_profundidad[profundidad] = \
        nodos_por_profundidad.get(profundidad, 0) + 1

    if modelo.juego_terminado():
        contar_resultado(modelo)
        return
    if profundidad == profundidad_max:
        return

    for fila, columna in modelo.obtener_movimientos_disponibles():
        sangria = "  " * profundidad
        if traza:
            print(sangria + "Prueba ({}, {}) y baja:"
                  .format(fila, columna))
        modelo.hacer_movimiento(fila, columna)
        if traza:
            for linea in str(modelo).splitlines():
                print(sangria + "  " + linea)
        explorar(modelo, profundidad + 1, profundidad_max, traza)
        modelo.deshacer_movimiento(fila, columna)
        if traza:
            print(sangria + "Retrocede de ({}, {}) -> siguiente rama"
                  .format(fila, columna))


def contar_resultado(modelo):
    """Suma la partida terminada al marcador correspondiente."""
    global ganadas_x, ganadas_o, empates
    if modelo.hay_ganador(GameModel.JUGADOR_X):
        ganadas_x += 1
    elif modelo.hay_ganador(GameModel.JUGADOR_O):
        ganadas_o += 1
    else:
        empates += 1


def reiniciar_contadores():
    global nodos, ganadas_x, ganadas_o, empates
    nodos = 0
    ganadas_x = 0
    ganadas_o = 0
    empates = 0
    nodos_por_profundidad.clear()


def main():
    # Primero: traza corta de la primera rama para ver el mecanismo
    print("=== Traza del backtracking (primeras dos jugadas) ===")
    print()
    explorar(GameModel(), 0, profundidad_max=1, traza=True)

    # Despues: recorrido completo del arbol, solo contando
    reiniciar_contadores()
    print()
    print("=== Recorrido completo del arbol de jugadas ===")
    explorar(GameModel(), 0, profundidad_max=9)

    print()
    print("Nodos visitados en total: {}".format(nodos))
    print("Nodos por profundidad:")
    for profundidad in sorted(nodos_por_profundidad):
        cantidad = nodos_por_profundidad[profundidad]
        print("  profundidad {}: {} nodos".format(profundidad, cantidad))
    print()
    print("Partidas terminadas (contando el orden de jugadas):")
    print("  Gana X: {}".format(ganadas_x))
    print("  Gana O: {}".format(ganadas_o))
    print("  Empates: {}".format(empates))


if __name__ == "__main__":
    main()
