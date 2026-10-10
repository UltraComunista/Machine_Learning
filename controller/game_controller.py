"""Controlador: sincroniza la interacción del usuario con el modelo
y la vista."""

import time

from model.minimax_agent import MinimaxAgent
from view.gui_view import GameView


class GameController:
    """Conecta la vista con el modelo siguiendo el patron MVC.

    Recibe los eventos de la interfaz (clics en casillas, reinicio,
    cambio de modo), los traduce en operaciones sobre el modelo y le
    devuelve a la vista el estado actualizado para que lo pinte.
    En el modo contra la IA, despues de cada jugada humana le pide
    la respuesta al agente Minimax y registra sus metricas.
    """

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self.agente_minimax = MinimaxAgent()
        # La vista avisa los clics llamando a los metodos de este
        # controlador; main.py le asigna la referencia (vista.controlador)

    def iniciar(self):
        """Pinta el estado inicial y arranca el ciclo de la interfaz."""
        self._actualizar_vista()
        self.vista.ejecutar()

    def manejar_clic_celda(self, fila, columna):
        """Procesa el click del usuario sobre una casilla del tablero."""
        if self.modelo.juego_terminado():
            return
        if self.modelo.hacer_movimiento(fila, columna):
            self._actualizar_vista()
            self._jugar_turno_ia()

    def manejar_reinicio(self):
        """Devuelve el juego al estado inicial."""
        self.modelo.reiniciar()
        self.vista.limpiar_metricas()
        self._actualizar_vista()

    def manejar_cambio_modo(self):
        """Cambia el modo de juego seleccionado en la interfaz.

        Cualquier cambio de modo reinicia la partida para empezar
        desde cero con las nuevas reglas.
        """
        self.manejar_reinicio()

    def _jugar_turno_ia(self):
        """Responde con el agente Minimax si el modo lo pide.

        Mide cuanto tarda y cuantos nodos explora para mostrarlo en
        las metricas de la interfaz.
        """
        if self.vista.obtener_modo() != GameView.MODO_MINIMAX:
            return
        if self.modelo.juego_terminado():
            return
        inicio = time.perf_counter()
        fila, columna = self.agente_minimax.mejor_jugada(self.modelo)
        self.modelo.hacer_movimiento(fila, columna)
        milisegundos = (time.perf_counter() - inicio) * 1000
        self.vista.mostrar_metricas(
            nodos=self.agente_minimax.nodos_evaluados,
            tiempo_ms=milisegundos)
        self._actualizar_vista()

    def _actualizar_vista(self):
        """Refleja el estado del modelo en la interfaz."""
        self.vista.actualizar_tablero(self.modelo.tablero)
        if self.modelo.hay_ganador(self.modelo.JUGADOR_X):
            self.vista.resaltar_celdas(
                self.modelo.linea_ganadora(self.modelo.JUGADOR_X))
            self.vista.mostrar_ganador(self.modelo.JUGADOR_X)
        elif self.modelo.hay_ganador(self.modelo.JUGADOR_O):
            self.vista.resaltar_celdas(
                self.modelo.linea_ganadora(self.modelo.JUGADOR_O))
            self.vista.mostrar_ganador(self.modelo.JUGADOR_O)
        elif self.modelo.hay_empate():
            self.vista.mostrar_empate()
        else:
            self.vista.mostrar_turno(self.modelo.jugador_actual)
