"""Generación de datos sintéticos y modelo de árbol de decisión.

Plan de la semana 3:
- Dia 1: simular partidas Minimax (IA) contra un jugador aleatorio y
  registrar cada jugada de la IA como una fila de datos.
- Dia 2: guardar el dataset en un archivo CSV.
- Dia 3: entrenar un arbol de decision con scikit-learn.
- Dia 4: conectar el agente de ML a la interfaz.
- Dia 5: comparar precision y tiempos contra Minimax.

La idea central del proyecto: en vez de buscar la jugada explorando
el arbol (Minimax), el modelo de ML aprende a predecirla directamente
a partir de ejemplos de partidas donde Minimax ya eligio bien.

Codificacion usada en el dataset:
- casilla vacia -> 0
- ficha X -> 1
- ficha O -> 2

Cada fila tiene 10 columnas: las 9 casillas del tablero en orden
(izquierda a derecha, de arriba hacia abajo) y al final la casilla
que eligio la IA, numerada del 0 al 8.
"""

import random

from model.game_model import GameModel
from model.minimax_agent import MinimaxAgent

CODIGO_VACIO = 0
CODIGO_X = 1
CODIGO_O = 2


def codificar_tablero(tablero):
    """Convierte la matriz 3x3 en una lista plana de 9 numeros.

    El arbol de decision no entiende matrices: solo acepta filas de
    numeros. Por eso se aplana el tablero y se cambian las letras
    por codigos numericos.
    """
    codigos = {
        GameModel.VACIO: CODIGO_VACIO,
        GameModel.JUGADOR_X: CODIGO_X,
        GameModel.JUGADOR_O: CODIGO_O,
    }
    return [codigos[tablero[fila][columna]]
            for fila in range(3) for columna in range(3)]


def casilla_a_numero(fila, columna):
    """Convierte una casilla (fila, columna) en un numero del 0 al 8."""
    return fila * 3 + columna


class GeneradorDatos:
    """Simula partidas y registra las jugadas de la IA como datos.

    La IA (Minimax) siempre juega con O y el jugador aleatorio con X.
    En cada turno de la IA se guarda una fila: el estado del tablero
    antes de mover y la casilla que Minimax eligio. Se usa una semilla
    para que la simulacion sea repetible (misma semilla, mismos datos).
    """

    def __init__(self, semilla=42):
        self.azar = random.Random(semilla)
        self.agente = MinimaxAgent()

    def _jugada_aleatoria(self, modelo):
        """Elige una casilla vacia al azar (jugador humano simulado)."""
        movimientos = modelo.obtener_movimientos_disponibles()
        return self.azar.choice(movimientos)

    def simular_partida(self):
        """Juega una partida completa X aleatorio contra O Minimax.

        Devuelve una tupla (filas, resultado): la lista de filas de
        datos de las jugadas de la IA y quien gano ("X", "O" o
        "empate"). La partida se juega sobre un tablero nuevo.
        """
        modelo = GameModel()
        filas = []

        while not modelo.juego_terminado():
            if modelo.jugador_actual == GameModel.JUGADOR_O:
                # Antes de que la IA mueva, se guarda el tablero y la
                # jugada que va a hacer: ese par es un ejemplo de datos.
                estado = codificar_tablero(modelo.tablero)
                fila, columna = self.agente.mejor_jugada(modelo)
                estado.append(casilla_a_numero(fila, columna))
                filas.append(estado)
            else:
                fila, columna = self._jugada_aleatoria(modelo)
            modelo.hacer_movimiento(fila, columna)

        if modelo.hay_ganador(GameModel.JUGADOR_O):
            resultado = GameModel.JUGADOR_O
        elif modelo.hay_ganador(GameModel.JUGADOR_X):
            resultado = GameModel.JUGADOR_X
        else:
            resultado = "empate"
        return filas, resultado

    def generar(self, num_partidas):
        """Simula num_partidas partidas y junta todas las filas.

        Devuelve la lista de filas de datos y un conteo de resultados
        para saber cuantas partidas gano cada quien.
        """
        datos = []
        resultados = {"X": 0, "O": 0, "empate": 0}
        for _ in range(num_partidas):
            filas, resultado = self.simular_partida()
            datos.extend(filas)
            resultados[resultado] += 1
        return datos, resultados
