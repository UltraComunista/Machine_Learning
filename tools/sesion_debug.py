"""Sesion de debugging en tiempo real: ver el backtracking de Minimax.

Juegas con X contra Minimax (O) desde una posicion con pocas casillas
libres. Cada vez que la IA responde, su razonamiento se imprime PASO
A PASO con una pausa entre llamadas, como en una sesion de debugging
a mano: se la ve probar una casilla, bajar por el arbol, deshacer el
movimiento y probar otra, en vivo.

Al terminar, compara la jugada de Minimax con el arbol de decision
del modo ML: muestra las reglas (preguntas) que el arbol se haria
para el mismo tablero y si hubiera elegido lo mismo.

Uso:
    python3.13 tools/sesion_debug.py
"""

import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from model.game_model import GameModel  # noqa: E402
from model.minimax_agent import MinimaxAgent  # noqa: E402
from model.ml_agent import (  # noqa: E402
    AgenteArbol,
    cargar_dataset,
    entrenar_arbol,
)

# Segundos de pausa entre pasos de la traza. Sube el numero para ir
# mas lento, bajalo para ir mas rapido.
DEMORA = 0.4

# Partida ya empezada (5 fichas: X, O, X, O, X) para que la IA decida
# con pocas casillas libres y la traza quepa en consola. X amenaza en
# la columna 0 con (0,0) y (1,0): la IA debe tapar en (2,0).
MOVIMIENTOS_INICIALES = [(0, 0), (1, 1), (1, 0), (2, 2), (2, 1)]


def nueva_partida():
    """Devuelve el tablero inicial de la sesion (turno de O)."""
    modelo = GameModel()
    for fila, columna in MOVIMIENTOS_INICIALES:
        modelo.hacer_movimiento(fila, columna)
    return modelo


def pedir_jugada(modelo):
    """Lee la jugada del usuario como 'fila columna' o 's' para salir.

    Devuelve (fila, columna) o None si quiere salir.
    """
    while True:
        entrada = input("Tu jugada X (fila columna, 0-2, o 's' salir): ")
        if entrada.strip().lower() == "s":
            return None
        try:
            fila, columna = [int(v) for v in entrada.split()]
        except ValueError:
            print("  Escribe dos numeros separados por espacio.")
            continue
        if modelo.es_movimiento_valido(fila, columna):
            return fila, columna
        print("  Casilla ocupada o fuera del tablero, prueba otra.")


def turno_ia(modelo, agente):
    """La IA responde mostrando la traza del backtracking en vivo."""
    print("\n--- La IA (O) empieza a pensar; sigue la traza ---")
    time.sleep(0.5)
    fila, columna = agente.mejor_jugada(
        modelo, traza=True, demora=DEMORA)
    print("--- Fin de la traza: eligio ({}, {}) tras explorar {} "
          "nodos ---\n".format(fila, columna, agente.nodos_evaluados))
    modelo.hacer_movimiento(fila, columna)


def mostrar_reglas_ml(agente_ml, tablero):
    """Muestra que habria decidido el arbol de ML en el mismo tablero
    y las reglas que uso, para compararlas con la traza de Minimax."""
    jugada, reglas = agente_ml.explicar_jugada(tablero)
    print("Las mismas reglas que export_text, paso a paso:")
    for regla in reglas:
        print("   " + regla)
    print("    -> el arbol de ML jugaria en la casilla {} "
          "(fila {}, columna {})".format(jugada, jugada // 3, jugada % 3))


def main():
    print("Sesion de debugging: backtracking de Minimax en tiempo real")
    print("==========================================================")
    print("Cargando el arbol de ML para la comparacion final...")
    tabla = cargar_dataset(os.path.join(RAIZ, "data", "partidas.csv"))
    arbol, precision = entrenar_arbol(tabla)
    print("Arbol de ML cargado (precision {:.1%}).\n".format(precision))
    agente_ml = AgenteArbol(arbol)

    agente = MinimaxAgent()
    modelo = nueva_partida()

    print("Empiezas desde esta posicion (turno de la IA):")
    print(modelo)
    turno_ia(modelo, agente)

    while not modelo.juego_terminado():
        print(modelo)
        jugada = pedir_jugada(modelo)
        if jugada is None:
            print("Sesion terminada.")
            return
        modelo.hacer_movimiento(*jugada)
        if modelo.juego_terminado():
            break
        turno_ia(modelo, agente)

    print(modelo)
    if modelo.hay_ganador("X"):
        print("Ganaste (imposible contra Minimax perfecto; revisa).")
    elif modelo.hay_ganador("O"):
        print("Gana la IA (como era de esperar).")
    else:
        print("Empate.")

    print("\n=== Comparacion: que habria hecho el arbol de ML? ===")
    print("(tablero de la ultima decision de la IA)")
    mostrar_reglas_ml(agente_ml, modelo.tablero)


if __name__ == "__main__":
    main()
