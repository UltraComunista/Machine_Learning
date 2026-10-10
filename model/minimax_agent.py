"""Agente de IA basado en el algoritmo Minimax con backtracking.

Plan de la semana 2:
- Dia 2: funcion de evaluacion para estados terminales.
- Dia 3: algoritmo Minimax recursivo con contador de nodos.

La IA maximiza su propio puntaje y asume que el humano jugara
siempre lo mejor para el, es decir, lo peor para la IA (minimiza
el puntaje de la IA). De ahi el nombre Minimax.
"""


class MinimaxAgent:
    """Evalua estados del tablero y (en el dia 3) elige jugadas."""

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
