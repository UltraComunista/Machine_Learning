"""Controlador: sincroniza la interacción del usuario con el modelo
y la vista."""


class GameController:
    """Conecta la vista con el modelo siguiendo el patron MVC.

    Recibe los eventos de la interfaz (clics en casillas, reinicio,
    cambio de modo), los traduce en operaciones sobre el modelo y le
    devuelve a la vista el estado actualizado para que lo pinte.
    """

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista

        # La vista no conoce al controlador: solo le pasamos callbacks
        vista.on_celda_click = self.manejar_clic_celda
        vista.on_reiniciar = self.manejar_reinicio
        vista.on_cambio_modo = self.manejar_cambio_modo

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

    def manejar_reinicio(self):
        """Devuelve el juego al estado inicial."""
        self.modelo.reiniciar()
        self.vista.limpiar_metricas()
        self._actualizar_vista()

    def manejar_cambio_modo(self):
        """Cambia el modo de juego seleccionado en la interfaz.

        Los modos contra la IA (Minimax y ML) se conectan en las
        semanas 2 y 3; por ahora cualquier cambio reinicia la partida.
        """
        self.manejar_reinicio()

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
