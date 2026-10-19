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

import pandas as pd

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


NOMBRES_CARACTERISTICAS = ["c{}".format(i) for i in range(9)]
NOMBRE_ETIQUETA = "jugada"
VALORES_CASILLA = (CODIGO_VACIO, CODIGO_X, CODIGO_O)


def construir_dataset(datos):
    """Convierte la lista de filas en un DataFrame de pandas.

    Las 9 primeras columnas (c0 a c8) son las caracteristicas, es
    decir el estado del tablero. La ultima (jugada) es la etiqueta,
    la casilla que Minimax eligio en ese estado.
    """
    columnas = NOMBRES_CARACTERISTICAS + [NOMBRE_ETIQUETA]
    return pd.DataFrame(datos, columns=columnas)


def validar_dataset(tabla):
    """Revisa que el dataset este bien formado y devuelve los problemas.

    Se llama antes de guardar el CSV para descartar filas corruptas:
    valores fuera de rango, etiquetas imposibles o datos vacios.
    Si todo esta bien devuelve una lista vacia.
    """
    problemas = []
    if tabla.empty:
        problemas.append("el dataset esta vacio")
        return problemas
    for nombre in NOMBRES_CARACTERISTICAS:
        valores = set(tabla[nombre].unique())
        if not valores.issubset(set(VALORES_CASILLA)):
            problemas.append("la columna {} tiene valores invalidos: {}"
                             .format(nombre, sorted(valores)))
    jugadas = set(tabla[NOMBRE_ETIQUETA].unique())
    if not jugadas.issubset(set(range(9))):
        problemas.append("hay etiquetas fuera del rango 0-8: {}"
                         .format(sorted(jugadas)))
    return problemas


def guardar_dataset(tabla, ruta):
    """Guarda el DataFrame en un archivo CSV con encabezado.

    El encabezado (c0...c8, jugada) es importante: cuando el modelo
    entrena, cada columna debe tener nombre para saber cual es cual.
    """
    tabla.to_csv(ruta, index=False)


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
