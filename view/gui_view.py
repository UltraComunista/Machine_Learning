"""Interfaz gráfica del juego (tablero, menús y métricas)."""

import tkinter as tk


class GameView:
    """Ventana principal del juego.

    La vista solo renderiza el estado que recibe del controlador y le
    notifica cuando el usuario hace clic en una casilla o en un boton.
    No conoce las reglas del juego: toda la logica vive en el modelo.
    """

    MODO_HUMANO = "Humano vs. Humano"
    MODO_MINIMAX = "Humano vs. IA Minimax"
    MODO_ML = "Humano vs. IA Machine Learning"

    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Tres en Raya")
        self.ventana.resizable(False, False)

        # Callbacks que el controlador registra para reaccionar a la vista
        self.on_celda_click = None
        self.on_reiniciar = None
        self.on_cambio_modo = None

        self._construir_tablero()
        self._construir_panel_lateral()

    def _construir_tablero(self):
        marco = tk.Frame(self.ventana, padx=10, pady=10)
        marco.grid(row=0, column=0)

        fuente = ("Helvetica", 32, "bold")
        self.botones = []
        for fila in range(3):
            fila_botones = []
            for columna in range(3):
                boton = tk.Button(
                    marco,
                    text=" ",
                    font=fuente,
                    width=3,
                    height=1,
                    command=lambda f=fila, c=columna: self._celda_click(f, c),
                )
                boton.grid(row=fila, column=columna, padx=3, pady=3)
                fila_botones.append(boton)
            self.botones.append(fila_botones)

    def _construir_panel_lateral(self):
        panel = tk.Frame(self.ventana, padx=10, pady=10)
        panel.grid(row=0, column=1, sticky="n")

        self.etiqueta_estado = tk.Label(
            panel, text="Turno de X", font=("Helvetica", 14))
        self.etiqueta_estado.pack(pady=(0, 10))

        tk.Label(panel, text="Modo de juego:").pack(anchor="w")
        self.var_modo = tk.StringVar(value=self.MODO_HUMANO)
        selector = tk.OptionMenu(
            panel, self.var_modo,
            self.MODO_HUMANO, self.MODO_MINIMAX, self.MODO_ML,
            command=self._cambio_modo,
        )
        selector.pack(fill="x", pady=(0, 10))

        tk.Button(
            panel, text="Reiniciar partida",
            command=self._reiniciar_click,
        ).pack(fill="x", pady=(0, 15))

        # Las metricas se usan en las semanas 2 y 3 para comparar
        # el rendimiento de Minimax y del modelo de ML
        tk.Label(panel, text="Métricas").pack(anchor="w")
        self.etiqueta_nodos = tk.Label(panel, text="Nodos explorados: -")
        self.etiqueta_nodos.pack(anchor="w")
        self.etiqueta_tiempo = tk.Label(panel, text="Tiempo de respuesta: -")
        self.etiqueta_tiempo.pack(anchor="w")

    def _celda_click(self, fila, columna):
        if self.on_celda_click is not None:
            self.on_celda_click(fila, columna)

    def _reiniciar_click(self):
        if self.on_reiniciar is not None:
            self.on_reiniciar()

    def _cambio_modo(self, _modo):
        if self.on_cambio_modo is not None:
            self.on_cambio_modo()

    # Metodos que usa el controlador para actualizar la interfaz

    def actualizar_tablero(self, tablero):
        """Pinta las fichas segun la matriz que le pasa el modelo."""
        for fila in range(3):
            for columna in range(3):
                self.botones[fila][columna].config(text=tablero[fila][columna])

    def mostrar_turno(self, jugador):
        self.etiqueta_estado.config(text="Turno de " + jugador)

    def mostrar_ganador(self, jugador):
        self.etiqueta_estado.config(text="Gana " + jugador)

    def mostrar_empate(self):
        self.etiqueta_estado.config(text="Empate")

    def mostrar_metricas(self, nodos=None, tiempo_ms=None):
        if nodos is not None:
            self.etiqueta_nodos.config(
                text="Nodos explorados: " + str(nodos))
        if tiempo_ms is not None:
            self.etiqueta_tiempo.config(
                text="Tiempo de respuesta: {:.2f} ms".format(tiempo_ms))

    def limpiar_metricas(self):
        self.etiqueta_nodos.config(text="Nodos explorados: -")
        self.etiqueta_tiempo.config(text="Tiempo de respuesta: -")

    def obtener_modo(self):
        return self.var_modo.get()

    def ejecutar(self):
        self.ventana.mainloop()
