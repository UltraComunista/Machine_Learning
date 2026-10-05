"""Interfaz grafica del juego construida con pygame.

La vista solo renderiza el estado que recibe del controlador y le
notifica cuando el usuario hace clic en una casilla o en un boton.
No conoce las reglas del juego: toda la logica vive en el modelo.
"""

import pygame


class GameView:
    """Ventana principal del juego.

    Muestra el tablero, el estado de la partida, el selector de modo
    y las metricas de rendimiento de las IA.
    """

    MODO_HUMANO = "Humano vs. Humano"
    MODO_MINIMAX = "Humano vs. IA Minimax"
    MODO_ML = "Humano vs. IA Machine Learning"

    # Paleta de colores
    FONDO = (24, 26, 32)
    PANEL = (38, 41, 50)
    LINEAS = (90, 95, 110)
    TEXTO = (230, 230, 235)
    TEXTO_APAGADO = (120, 124, 135)
    FICHA_X = (86, 156, 214)
    FICHA_O = (224, 108, 117)
    BOTON = (55, 60, 72)
    BOTON_SEL = (70, 100, 150)
    AVISO = (220, 180, 90)

    ANCHO = 720
    ALTO = 540
    MARGEN = 30
    TAM_CELDA = 160
    PANEL_X = 540

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tres en Raya")
        self.ventana = pygame.display.set_mode((self.ANCHO, self.ALTO))
        self.reloj = pygame.time.Clock()

        self.fuente = pygame.font.SysFont("arial", 20)
        self.fuente_grande = pygame.font.SysFont("arial", 26, bold=True)

        self.ejecutando = True
        self.modo = self.MODO_HUMANO
        self.tablero = [[" " for _ in range(3)] for _ in range(3)]
        self.texto_estado = "Turno de X"
        self.nodos = None
        self.tiempo_ms = None
        self.aviso = None
        self._aviso_hasta = 0

        # Callbacks que registra el controlador
        self.on_celda_click = None
        self.on_reiniciar = None
        self.on_cambio_modo = None

        self.botones = self._crear_botones()

    # Construccion de la interfaz

    def _crear_botones(self):
        ancho = 150
        alto = 40
        x = self.PANEL_X + 15
        return [
            {"rect": pygame.Rect(x, 150, ancho, alto),
             "texto": "Humano vs. Humano",
             "accion": "modo_humano", "habilitado": True},
            {"rect": pygame.Rect(x, 200, ancho, alto),
             "texto": "vs. IA Minimax",
             "accion": "modo_minimax", "habilitado": False},
            {"rect": pygame.Rect(x, 250, ancho, alto),
             "texto": "vs. IA ML",
             "accion": "modo_ml", "habilitado": False},
            {"rect": pygame.Rect(x, 420, ancho, alto),
             "texto": "Reiniciar",
             "accion": "reiniciar", "habilitado": True},
        ]

    # Bucle principal y manejo de eventos

    def ejecutar(self):
        while self.ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.ejecutando = False
                elif (evento.type == pygame.MOUSEBUTTONDOWN
                      and evento.button == 1):
                    self._manejar_click(evento.pos)
            self._dibujar()
            pygame.display.flip()
            self.reloj.tick(30)

    def cerrar(self):
        self.ejecutando = False

    def _manejar_click(self, pos):
        for boton in self.botones:
            if boton["rect"].collidepoint(pos):
                self._activar_boton(boton)
                return
        celda = self._celda_en_posicion(pos)
        if celda is not None and self.on_celda_click is not None:
            self.on_celda_click(*celda)

    def _activar_boton(self, boton):
        if not boton["habilitado"]:
            self._mostrar_aviso(boton["accion"])
            return
        if boton["accion"] == "reiniciar":
            if self.on_reiniciar is not None:
                self.on_reiniciar()
        elif self.on_cambio_modo is not None:
            self.modo = self.MODO_HUMANO
            self.on_cambio_modo()

    def _mostrar_aviso(self, accion):
        if accion == "modo_minimax":
            self.aviso = "Disponible en la semana 2"
        else:
            self.aviso = "Disponible en la semana 3"
        self._aviso_hasta = pygame.time.get_ticks() + 3000

    def _celda_en_posicion(self, pos):
        x, y = pos
        limite = self.MARGEN + 3 * self.TAM_CELDA
        if not (self.MARGEN <= x < limite and self.MARGEN <= y < limite):
            return None
        fila = (y - self.MARGEN) // self.TAM_CELDA
        columna = (x - self.MARGEN) // self.TAM_CELDA
        return fila, columna

    # Dibujo de la interfaz

    def _dibujar(self):
        self.ventana.fill(self.FONDO)
        self._dibujar_tablero()
        self._dibujar_panel()

    def _dibujar_tablero(self):
        for i in range(4):
            pos = self.MARGEN + i * self.TAM_CELDA
            fin = self.MARGEN + 3 * self.TAM_CELDA
            pygame.draw.line(self.ventana, self.LINEAS,
                             (pos, self.MARGEN), (pos, fin), 3)
            pygame.draw.line(self.ventana, self.LINEAS,
                             (self.MARGEN, pos), (fin, pos), 3)
        for fila in range(3):
            for columna in range(3):
                self._dibujar_ficha(fila, columna)

    def _dibujar_ficha(self, fila, columna):
        valor = self.tablero[fila][columna]
        if valor == " ":
            return
        centro_x = self.MARGEN + columna * self.TAM_CELDA + self.TAM_CELDA // 2
        centro_y = self.MARGEN + fila * self.TAM_CELDA + self.TAM_CELDA // 2
        radio = self.TAM_CELDA // 2 - 30
        if valor == "X":
            color = self.FICHA_X
            pygame.draw.line(self.ventana, color,
                             (centro_x - radio, centro_y - radio),
                             (centro_x + radio, centro_y + radio), 10)
            pygame.draw.line(self.ventana, color,
                             (centro_x - radio, centro_y + radio),
                             (centro_x + radio, centro_y - radio), 10)
        else:
            pygame.draw.circle(self.ventana, self.FICHA_O,
                               (centro_x, centro_y), radio, 8)

    def _dibujar_panel(self):
        pygame.draw.rect(self.ventana, self.PANEL,
                         (self.PANEL_X, 0, self.ANCHO - self.PANEL_X,
                          self.ALTO))

        titulo = self.fuente_grande.render("Tres en Raya", True, self.TEXTO)
        self.ventana.blit(titulo, (self.PANEL_X + 15, 20))

        estado = self.fuente.render(self.texto_estado, True, self.TEXTO)
        self.ventana.blit(estado, (self.PANEL_X + 15, 70))

        for boton in self.botones:
            self._dibujar_boton(boton)

        self._dibujar_metricas()
        self._dibujar_aviso()

    def _dibujar_boton(self, boton):
        rect = boton["rect"]
        seleccionado = (boton["accion"] == "modo_humano"
                        and self.modo == self.MODO_HUMANO)
        if not boton["habilitado"]:
            color, color_texto = self.BOTON, self.TEXTO_APAGADO
        elif seleccionado:
            color, color_texto = self.BOTON_SEL, self.TEXTO
        else:
            color, color_texto = self.BOTON, self.TEXTO

        pygame.draw.rect(self.ventana, color, rect, border_radius=6)
        texto = self.fuente.render(boton["texto"], True, color_texto)
        pos_x = rect.x + (rect.width - texto.get_width()) // 2
        pos_y = rect.y + (rect.height - texto.get_height()) // 2
        self.ventana.blit(texto, (pos_x, pos_y))

    def _dibujar_metricas(self):
        y = 330
        pygame.draw.line(self.ventana, self.LINEAS,
                         (self.PANEL_X + 15, y - 15),
                         (self.ANCHO - 15, y - 15), 1)
        nodos = "-" if self.nodos is None else str(self.nodos)
        tiempo = "-" if self.tiempo_ms is None \
            else "{:.2f} ms".format(self.tiempo_ms)
        for etiqueta in ("Nodos: " + nodos, "Tiempo: " + tiempo):
            superficie = self.fuente.render(etiqueta, True, self.TEXTO)
            self.ventana.blit(superficie, (self.PANEL_X + 15, y))
            y += 30

    def _dibujar_aviso(self):
        if self.aviso is None:
            return
        if pygame.time.get_ticks() > self._aviso_hasta:
            self.aviso = None
            return
        superficie = self.fuente.render(self.aviso, True, self.AVISO)
        self.ventana.blit(superficie, (self.PANEL_X + 15, 480))

    # Metodos que usa el controlador para actualizar la interfaz

    def actualizar_tablero(self, tablero):
        """Guarda el estado del tablero para dibujarlo en el proximo
        frame."""
        self.tablero = [fila[:] for fila in tablero]

    def mostrar_turno(self, jugador):
        self.texto_estado = "Turno de " + jugador

    def mostrar_ganador(self, jugador):
        self.texto_estado = "Gana " + jugador

    def mostrar_empate(self):
        self.texto_estado = "Empate"

    def mostrar_metricas(self, nodos=None, tiempo_ms=None):
        if nodos is not None:
            self.nodos = nodos
        if tiempo_ms is not None:
            self.tiempo_ms = tiempo_ms

    def limpiar_metricas(self):
        self.nodos = None
        self.tiempo_ms = None

    def obtener_modo(self):
        return self.modo
