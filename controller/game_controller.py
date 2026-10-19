"""Controlador: sincroniza la interacción del usuario con el modelo
y la vista."""

import os
import time

from model.minimax_agent import MinimaxAgent
from model.ml_agent import AgenteArbol, cargar_dataset, entrenar_arbol
from view.gui_view import GameView

# Ruta al dataset, calculada desde la ubicacion de este archivo para
# que funcione aunque se ejecute desde otra carpeta.
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DATASET = os.path.join(RAIZ, "data", "partidas.csv")


class GameController:
    """Conecta la vista con el modelo siguiendo el patron MVC.

    Recibe los eventos de la interfaz (clics en casillas, reinicio,
    cambio de modo), los traduce en operaciones sobre el modelo y le
    devuelve a la vista el estado actualizado para que lo pinte.
    En los modos contra la IA, despues de cada jugada humana le pide
    la respuesta al agente del modo (Minimax o ML) y registra sus
    metricas.
    """

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self.agente_minimax = MinimaxAgent()
        # El agente de ML se crea perezoso: entrenar el arbol tarda
        # un par de segundos, asi que se hace la primera vez que el
        # usuario elige el modo ML, no al arrancar el juego.
        self._agente_ml = None
        # La vista avisa los clics llamando a los metodos de este
        # controlador; main.py le asigna la referencia (vista.controlador)

    def _obtener_agente_ml(self):
        """Carga el dataset y entrena el arbol la primera vez que se
        necesita; despues reutiliza el mismo agente entrenado."""
        if self._agente_ml is None:
            tabla = cargar_dataset(RUTA_DATASET)
            arbol, _ = entrenar_arbol(tabla)
            self._agente_ml = AgenteArbol(arbol)
        return self._agente_ml

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
        """Responde con el agente del modo actual (Minimax o ML).

        Ambos agentes entienden el mismo mensaje mejor_jugada(modelo)
        y guardan sus nodos en nodos_evaluados, asi que el codigo de
        medicion es comun. Mide cuanto tarda y cuantos nodos revisa
        para mostrarlo en las metricas de la interfaz.
        """
        modo = self.vista.obtener_modo()
        if modo == GameView.MODO_MINIMAX:
            agente = self.agente_minimax
        elif modo == GameView.MODO_ML:
            agente = self._obtener_agente_ml()
        else:
            return
        if self.modelo.juego_terminado():
            return
        inicio = time.perf_counter()
        fila, columna = agente.mejor_jugada(self.modelo)
        milisegundos = (time.perf_counter() - inicio) * 1000
        if not self.modelo.es_movimiento_valido(fila, columna):
            # El arbol de ML puede proponer una casilla ya ocupada en
            # estados que vio pocas veces; se juega la primera libre.
            fila, columna = self.modelo.obtener_movimientos_disponibles()[0]
        self.modelo.hacer_movimiento(fila, columna)
        self.vista.mostrar_metricas(
            nodos=agente.nodos_evaluados,
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
