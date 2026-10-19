"""Comparativa final: Minimax vs. arbol de decision (Semana 3, Dia 5).

Mide en las mismas posiciones cuanto tarda y cuantos nodos revisa
cada agente, y en cuantas jugadas coinciden. Tambien muestra:

- La traza de backtracking de Minimax en una posicion con pocas
  casillas libres (para ver el recorrido completo en consola).
- Las preguntas que el arbol de decision se hace para elegir jugada
  en un tablero de ejemplo (las reglas aprendidas, en texto).

Uso:
    python3.13 tools/comparar_agentes.py
"""

import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

from model.game_model import GameModel  # noqa: E402
from model.minimax_agent import MinimaxAgent  # noqa: E402
from model.ml_agent import (  # noqa: E402
    AgenteArbol,
    cargar_dataset,
    codificar_tablero,
    entrenar_arbol,
)

POSICIONES = 50
SEMILLA = 7


def posicion_aleatoria(azar):
    """Arma un tablero de turno de O, como los del dataset.

    Juega una mini partida alternando turnos: X mueve al azar y O con
    Minimax (igual que en la simulacion que genero el dataset). A la
    mitad de las veces se para justo antes de que O mueva: esa es la
    posicion que se mide. Si la partida se acaba antes, devuelve None.
    """
    modelo = GameModel()
    agente = MinimaxAgent()
    while not modelo.juego_terminado():
        fila, columna = azar.choice(
            modelo.obtener_movimientos_disponibles())
        modelo.hacer_movimiento(fila, columna)
        if modelo.juego_terminado():
            return None
        if azar.random() < 0.5:
            return modelo
        fila, columna = agente.mejor_jugada(modelo)
        modelo.hacer_movimiento(fila, columna)
    return None


def explicar_jugada_arbol(arbol, tablero):
    """Imprime las preguntas (reglas) que el arbol se hace para un
    tablero y la jugada final que decide.

    Baja nodo a nodo por decision_path: cada nodo es una pregunta
    del tipo "¿c4 <= 0.5?" (¿esta libre el centro?) y la hoja dice
    la clase, es decir, la casilla donde jugar.
    """
    estado = codificar_tablero(tablero)
    nodo = 0
    print("  Preguntas del arbol para este tablero:")
    while arbol.tree_.children_left[nodo] != -1:
        casilla = arbol.tree_.feature[nodo]
        umbral = arbol.tree_.threshold[nodo]
        if estado[casilla] <= umbral:
            print("    ¿c{} <= {:.1f}? c{}={} -> si".format(
                casilla, umbral, casilla, estado[casilla]))
            nodo = arbol.tree_.children_left[nodo]
        else:
            print("    ¿c{} <= {:.1f}? c{}={} -> no".format(
                casilla, umbral, casilla, estado[casilla]))
            nodo = arbol.tree_.children_right[nodo]
    jugada = int(arbol.classes_[arbol.tree_.value[nodo].argmax()])
    print("    -> jugar en la casilla {}".format(jugada))
    return jugada


def demo_traza_minimax():
    """Muestra el backtracking de Minimax en una posicion pequena.

    Con pocas casillas libres la traza cabe en consola y se ve como
        pruebo (f, c) turno de la IA
          pruebo ... (mas profundo)
        deshago (f, c) -> puntaje N
    """
    print("\n=== 1. Traza de backtracking de Minimax ===")
    modelo = GameModel()
    # X tiene la fila de arriba casi completa: la IA debe bloquear.
    for fila, columna in [(0, 0), (1, 1), (0, 1)]:
        modelo.hacer_movimiento(fila, columna)
    print("Tablero (turno de la IA, X amenaza en la fila 0):")
    print(modelo)
    agente = MinimaxAgent()
    fila, columna = agente.mejor_jugada(modelo, traza=True)
    print("Jugada elegida: ({}, {}), nodos explorados: {}".format(
        fila, columna, agente.nodos_evaluados))


def demo_reglas_arbol(agente_ml):
    """Muestra las reglas que el arbol aprendio para un tablero."""
    print("\n=== 2. Reglas aprendidas por el arbol de decision ===")
    modelo = GameModel()
    for fila, columna in [(0, 0), (1, 1), (0, 1)]:
        modelo.hacer_movimiento(fila, columna)
    print("Mismo tablero que arriba:")
    print(modelo)
    jugada = explicar_jugada_arbol(agente_ml.arbol, modelo.tablero)
    agente_ml.nodos_evaluados = 0
    print("  Jugada final del arbol: la casilla {}".format(jugada))


def comparacion(agente_ml):
    """Mide ambos agentes en las mismas posiciones aleatorias."""
    print("\n=== 3. Comparativa en {} posiciones aleatorias ===".format(
        POSICIONES))
    azar = random.Random(SEMILLA)
    agente_minimax = MinimaxAgent()

    coinciden = 0
    nodos_minimax = 0
    nodos_ml = 0
    tiempo_minimax = 0.0
    tiempo_ml = 0.0

    for _ in range(POSICIONES):
        modelo = posicion_aleatoria(azar)
        if modelo is None:
            continue

        inicio = time.perf_counter()
        jugada_minimax = agente_minimax.mejor_jugada(modelo)
        tiempo_minimax += time.perf_counter() - inicio
        nodos_minimax += agente_minimax.nodos_evaluados

        inicio = time.perf_counter()
        jugada_ml = agente_ml.mejor_jugada(modelo)
        tiempo_ml += time.perf_counter() - inicio
        nodos_ml += agente_ml.nodos_evaluados

        if jugada_minimax == jugada_ml:
            coinciden += 1

    print("Coincidencia en la jugada elegida: {}/{} ({:.1%})".format(
        coinciden, POSICIONES, coinciden / POSICIONES))
    print("Tiempo total Minimax:  {:.1f} ms (promedio {:.1f} ms/jugada)"
          .format(tiempo_minimax * 1000,
                  tiempo_minimax * 1000 / POSICIONES))
    print("Tiempo total ML:       {:.1f} ms (promedio {:.2f} ms/jugada)"
          .format(tiempo_ml * 1000, tiempo_ml * 1000 / POSICIONES))
    print("Nodos totales Minimax: {}".format(nodos_minimax))
    print("Nodos totales ML:      {}".format(nodos_ml))


def main():
    print("Cargando dataset y entrenando el arbol...")
    tabla = cargar_dataset(os.path.join("data", "partidas.csv"))
    arbol, precision = entrenar_arbol(tabla)
    print("Precision del arbol: {:.1%}\n".format(precision))
    agente_ml = AgenteArbol(arbol)

    demo_traza_minimax()
    demo_reglas_arbol(agente_ml)
    comparacion(agente_ml)


if __name__ == "__main__":
    main()
