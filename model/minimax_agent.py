"""Agente de IA basado en el algoritmo Minimax con backtracking.

Plan de la semana 2:
- Dia 2: funcion de evaluacion para estados terminales.
- Dia 3: algoritmo Minimax recursivo con contador de nodos.

La IA maximiza su propio puntaje y asume que el humano jugara
siempre lo mejor para el, es decir, lo peor para la IA (minimiza
el puntaje de la IA). De ahi el nombre Minimax.
"""


class MinimaxAgent:
    """Explora el arbol de jugadas y elige la mejor jugada posible.

    En su turno la IA maximiza el puntaje; en el turno del humano
    asume que el humano minimiza el puntaje de la IA. Al explorar,
    aplica movimientos con hacer_movimiento y los deshace con
    deshacer_movimiento (backtracking), asi el tablero queda igual
    que al empezar.
    """

    PUNTAJE_VICTORIA = 10
    PUNTAJE_DERROTA = -10
    PUNTAJE_EMPATE = 0

    def __init__(self, jugador_ia="O", jugador_humano="X"):
        self.jugador_ia = jugador_ia
        self.jugador_humano = jugador_humano
        self.nodos_evaluados = 0

    def evaluar(self, modelo):
        """Puntua el estado del tablero desde el punto de vista de la IA.

        Devuelve +10 si gano la IA, -10 si gano el humano y 0 si hay
        empate o la partida sigue abierta. Son los casos base que
        Minimax propagara hacia arriba en el arbol de jugadas.
        """
        if modelo.hay_ganador(self.jugador_ia):
            return self.PUNTAJE_VICTORIA
        if modelo.hay_ganador(self.jugador_humano):
            return self.PUNTAJE_DERROTA
        return self.PUNTAJE_EMPATE

    def minimax(self, modelo, profundidad, maximizando):
        """Devuelve el mejor puntaje alcanzable desde este estado.

        Llega a las hojas del arbol (partidas terminadas) con
        backtracking y propaga los puntajes: el nivel de la IA toma
        el maximo y el nivel del humano el minimo.
        """
        self.nodos_evaluados += 1
        puntaje = self.evaluar(modelo)

        # Casos base: hojas del arbol de juego. El ajuste por
        # profundidad premia ganar rapido y retrasar la derrota.
        if puntaje == self.PUNTAJE_VICTORIA:
            return puntaje - profundidad
        if puntaje == self.PUNTAJE_DERROTA:
            return puntaje + profundidad
        if not modelo.obtener_movimientos_disponibles():
            return self.PUNTAJE_EMPATE

        if maximizando:
            mejor = float("-inf")
            for fila, columna in modelo.obtener_movimientos_disponibles():
                modelo.hacer_movimiento(fila, columna)
                puntaje_hijo = self.minimax(modelo, profundidad + 1, False)
                modelo.deshacer_movimiento(fila, columna)
                mejor = max(puntaje_hijo, mejor)
            return mejor

        mejor = float("inf")
        for fila, columna in modelo.obtener_movimientos_disponibles():
            modelo.hacer_movimiento(fila, columna)
            puntaje_hijo = self.minimax(modelo, profundidad + 1, True)
            modelo.deshacer_movimiento(fila, columna)
            mejor = min(puntaje_hijo, mejor)
        return mejor

    def mejor_jugada(self, modelo):
        """Devuelve la casilla (fila, columna) optima para la IA.

        Explora cada movimiento disponible con Minimax y se queda con
        el de mayor puntaje. Reinicia el contador de nodos para que
        la interfaz muestre cuantos se visitaron en esta jugada.
        """
        self.nodos_evaluados = 0
        mejor_puntaje = float("-inf")
        mejor_movimiento = None
        for fila, columna in modelo.obtener_movimientos_disponibles():
            modelo.hacer_movimiento(fila, columna)
            puntaje = self.minimax(modelo, 0, False)
            modelo.deshacer_movimiento(fila, columna)
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_movimiento = (fila, columna)
        return mejor_movimiento
