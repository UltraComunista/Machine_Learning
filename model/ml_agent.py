"""Generación de datos y modelo de árbol de decision, todo propio.

Plan de la semana 3:
- Dia 1: simular partidas Minimax (IA) contra un jugador aleatorio y
  registrar cada jugada de la IA como una fila de datos.
- Dia 2: guardar el dataset en un archivo CSV.
- Dia 3: entrenar un arbol de decision.
- Dia 4: conectar el agente de ML a la interfaz.
- Dia 5: comparar precision y tiempos contra Minimax.

La idea central del proyecto: en vez de buscar la jugada explorando
el arbol (Minimax), el modelo de ML aprende a predecirla directamente
a partir de ejemplos de partidas donde Minimax ya eligio bien.

No se usan librerias de machine learning: el arbol de decision es
nuestra propia implementacion (model/arbol_decision.py), la separacion
entrenamiento/prueba se hace a mano y el CSV se lee con el modulo
estandar csv. Ver modelo/arbol_decision.py para la logica del arbol.

Codificacion usada en el dataset:
- casilla vacia -> 0
- ficha X -> 1
- ficha O -> 2

Cada fila tiene 10 columnas: las 9 casillas del tablero en orden
(izquierda a derecha, de arriba hacia abajo) y al final la casilla
que eligio la IA, numerada del 0 al 8.
"""

import csv
import random

from model.arbol_decision import ArbolDecision
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
NOMBRES_COLUMNAS = NOMBRES_CARACTERISTICAS + [NOMBRE_ETIQUETA]
VALORES_CASILLA = (CODIGO_VACIO, CODIGO_X, CODIGO_O)


class TablaDatos:
    """Tabla de datos con encabezado y filas, sin pandas.

    Guarda el encabezado (los nombres de columna) y las filas como
    listas de numeros. Es lo minimo que el proyecto necesita para
    mover datos entre el CSV, el entrenamiento y la validacion.
    """

    def __init__(self, encabezado, filas):
        self.encabezado = list(encabezado)
        self.filas = [list(f) for f in filas]

    def __len__(self):
        return len(self.filas)

    def columna(self, nombre):
        """Devuelve una columna completa como lista, por su nombre."""
        indice = self.encabezado.index(nombre)
        return [fila[indice] for fila in self.filas]


def construir_dataset(datos):
    """Convierte la lista de filas en una TablaDatos.

    Las 9 primeras columnas (c0 a c8) son las caracteristicas, es
    decir el estado del tablero. La ultima (jugada) es la etiqueta,
    la casilla que Minimax eligio en ese estado.
    """
    return TablaDatos(NOMBRES_COLUMNAS, datos)


def validar_dataset(tabla):
    """Revisa que el dataset este bien formado y devuelve los problemas.

    Se llama antes de guardar el CSV para descartar filas corruptas:
    valores fuera de rango, etiquetas imposibles o datos vacios.
    Si todo esta bien devuelve una lista vacia.
    """
    problemas = []
    if len(tabla) == 0:
        problemas.append("el dataset esta vacio")
        return problemas
    for nombre in NOMBRES_CARACTERISTICAS:
        valores = set(tabla.columna(nombre))
        if not valores.issubset(set(VALORES_CASILLA)):
            problemas.append("la columna {} tiene valores invalidos: {}"
                             .format(nombre, sorted(valores)))
    jugadas = set(tabla.columna(NOMBRE_ETIQUETA))
    if not jugadas.issubset(set(range(9))):
        problemas.append("hay etiquetas fuera del rango 0-8: {}"
                         .format(sorted(jugadas)))
    return problemas


def guardar_dataset(tabla, ruta):
    """Guarda la tabla en un CSV con encabezado, con el modulo csv.

    El encabezado (c0...c8, jugada) es importante: cuando el modelo
    entrena, cada columna debe tener nombre para saber cual es cual.
    """
    with open(ruta, "w", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(tabla.encabezado)
        escritor.writerows(tabla.filas)


def cargar_dataset(ruta):
    """Lee un CSV del dataset y lo devuelve como TablaDatos.

    Lee numeros enteros a partir del encabezado; sin pandas.
    """
    with open(ruta, newline="") as archivo:
        lector = csv.reader(archivo)
        encabezado = next(lector)
        filas = [[int(valor) for valor in fila] for fila in lector if fila]
    return TablaDatos(encabezado, filas)


def separar_entrenamiento_prueba(tabla, semilla,
                                 proporcion_prueba=0.2):
    """Mezcla las filas y las parte en entrenamiento (80%) y prueba
    (20%).

    La mezcla usa su propio generador aleatorio con la semilla dada,
    asi que la separacion es identica en cada ejecucion (misma semilla,
    mismos datos de entrenamiento y de prueba).
    """
    azar = random.Random(semilla)
    indices = list(range(len(tabla)))
    azar.shuffle(indices)
    corte = int(len(indices) * (1 - proporcion_prueba))
    entrenamiento = [tabla.filas[i] for i in indices[:corte]]
    prueba = [tabla.filas[i] for i in indices[corte:]]
    return entrenamiento, prueba


def entrenar_arbol(tabla, semilla=42):
    """Entrena un arbol de decision y devuelve (arbol, precision).

    Separa el dataset en 80% para entrenar y 20% para probar. La
    precision es la proporcion de jugadas del 20% de prueba que el
    arbol acierta. El arbol es nuestra implementacion propia de
    model/arbol_decision.py: el criterio de Gini, la busqueda de la
    mejor pregunta y la recursion son codigo nuestro.
    """
    entrenamiento, prueba = separar_entrenamiento_prueba(tabla, semilla)
    indice_etiqueta = tabla.encabezado.index(NOMBRE_ETIQUETA)
    filas = [fila[:indice_etiqueta] for fila in entrenamiento]
    etiquetas = [fila[indice_etiqueta] for fila in entrenamiento]
    arbol = ArbolDecision().ajustar(filas, etiquetas)

    aciertos = 0
    for fila in prueba:
        if arbol.predecir(fila[:indice_etiqueta]) == fila[indice_etiqueta]:
            aciertos += 1
    precision = aciertos / len(prueba) if prueba else 0.0
    return arbol, precision


class AgenteArbol:
    """Envuelve el arbol entrenado con la misma interfaz que MinimaxAgent.

    MinimaxAgent explora el arbol de jugadas recursivamente; este
    agente solo le pregunta al arbol de decision entrenado y obtiene
    la jugada de inmediato, sin buscar nada.
    """

    def __init__(self, arbol, jugador_ia=GameModel.JUGADOR_O):
        self.arbol = arbol
        self.jugador_ia = jugador_ia
        self.nodos_evaluados = 0

    def predecir_jugada(self, tablero):
        """Devuelve la casilla elegida (numero del 0 al 8) para un
        tablero dado. Cuenta cuantos nodos del arbol recorrio la
        prediccion (las preguntas mas la hoja) para poder comparar con
        los miles de nodos que explora Minimax."""
        estado = codificar_tablero(tablero)
        jugada, ruta = self.arbol.predecir_con_ruta(estado)
        self.nodos_evaluados = len(ruta) + 1
        return jugada

    def mejor_jugada(self, modelo):
        """Devuelve la casilla (fila, columna) que propone el arbol.

        Recibe el GameModel igual que MinimaxAgent, asi el
        controlador puede usar cualquiera de los dos sin cambios.
        """
        numero = self.predecir_jugada(modelo.tablero)
        return (numero // 3, numero % 3)

    def explicar_jugada(self, tablero):
        """Devuelve (jugada, reglas) para un tablero: la casilla que
        eligiria y las preguntas que se hizo para decidir.

        Cada regla es un nodo del arbol: una pregunta del tipo
        "¿c4 <= 0.5?" (¿esta libre el centro?) con la respuesta que
        tomo para ese tablero. Es el mismo recorrido que hace
        predecir_jugada, pero guardando el camino.
        """
        estado = codificar_tablero(tablero)
        jugada, ruta = self.arbol.predecir_con_ruta(estado)
        reglas = []
        for caracteristica, umbral, respuesta in ruta:
            reglas.append("¿c{} <= {:.1f}? c{}={} -> {}".format(
                caracteristica, umbral, caracteristica,
                estado[caracteristica], respuesta))
        return jugada, reglas


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
