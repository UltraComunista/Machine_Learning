"""Interfaz grafica del juego construida con pygame.

La vista solo renderiza el estado que recibe del controlador y le
notifica cuando el usuario hace clic en una casilla o en un boton.
No conoce las reglas del juego: toda la logica vive en el modelo.
"""

import pygame


class GameView:
    """Ventana principal del juego.

    Tiene dos pantallas: un menu principal para elegir el modo de
    juego y la pantalla de partida con el tablero, el turno actual,
    las metricas y un cartel de resultado al terminar.
    """

    MODO_HUMANO = "Humano vs. Humano"
    MODO_MINIMAX = "Humano vs. IA Minimax"
    MODO_ML = "Humano vs. IA Machine Learning"

    # Paleta de colores
    FONDO_ARRIBA = (15, 17, 27)
    FONDO_ABAJO = (29, 33, 53)
    PANEL = (32, 36, 54)
    CELDA = (37, 42, 63)
    CELDA_HOVER = (52, 59, 88)
    LINEAS = (64, 71, 100)
    TEXTO = (235, 237, 245)
    TEXTO_APAGADO = (125, 130, 148)
    TEXTO_ACENTO = (130, 200, 255)
    FICHA_X = (96, 165, 250)
    FICHA_O = (244, 114, 122)
    RESALTE = (250, 204, 100)
    BOTON = (54, 60, 88)
    BOTON_HOVER = (72, 80, 116)
    BOTON_BORDE = (96, 106, 148)
    CARTEL = (38, 42, 62)
    AVISO = (250, 204, 100)

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
        self.fuente_pequena = pygame.font.SysFont("arial", 16)
        self.fuente_boton = pygame.font.SysFont("arial", 21, bold=True)
        self.fuente_grande = pygame.font.SysFont("arial", 26, bold=True)
        self.fuente_titulo = pygame.font.SysFont("arial", 64, bold=True)

        self.ejecutando = True
        self.pantalla = "menu"
        self.partida_terminada = False
        self.modo = self.MODO_HUMANO
        self.tablero = [[" " for _ in range(3)] for _ in range(3)]
        self.celdas_resaltadas = []
        self.texto_estado = "Turno del jugador X"
        self.nodos = None
        self.tiempo_ms = None
        self.aviso = None
        self._aviso_hasta = 0

        # Callbacks que registra el controlador
        self.on_celda_click = None
        self.on_reiniciar = None
        self.on_cambio_modo = None

        self.botones_menu = self._crear_botones_menu()
        self.botones_juego = self._crear_botones_juego()
        self.botones_fin = self._crear_botones_fin()

    # Construccion de la interfaz

    def _crear_botones_menu(self):
        ancho, alto = 360, 54
        x = (self.ANCHO - ancho) // 2
        return [
            {"rect": pygame.Rect(x, 240, ancho, alto),
             "texto": "Humano vs. Humano",
             "accion": "jugar_humano", "habilitado": True},
            {"rect": pygame.Rect(x, 310, ancho, alto),
             "texto": "Humano vs. IA Minimax",
             "accion": "aviso_minimax", "habilitado": False},
            {"rect": pygame.Rect(x, 380, ancho, alto),
             "texto": "Humano vs. IA Machine Learning",
             "accion": "aviso_ml", "habilitado": False},
            {"rect": pygame.Rect(x, 470, ancho, alto),
             "texto": "Salir",
             "accion": "salir", "habilitado": True},
        ]

    def _crear_botones_juego(self):
        ancho, alto = 150, 40
        x = self.PANEL_X + 15
        return [
            {"rect": pygame.Rect(x, 410, ancho, alto),
             "texto": "Reiniciar",
             "accion": "reiniciar", "habilitado": True},
            {"rect": pygame.Rect(x, 460, ancho, alto),
             "texto": "Menú",
             "accion": "volver_menu", "habilitado": True},
        ]

    def _crear_botones_fin(self):
        ancho, alto = 210, 46
        y = 330
        return [
            {"rect": pygame.Rect(130, y, ancho, alto),
             "texto": "Jugar de nuevo",
             "accion": "otra_vez", "habilitado": True},
            {"rect": pygame.Rect(380, y, ancho, alto),
             "texto": "Menú",
             "accion": "volver_menu", "habilitado": True},
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
        if self.pantalla == "menu":
            self._click_en_botones(self.botones_menu, pos)
            return
        if self.partida_terminada:
            self._click_en_botones(self.botones_fin, pos)
            return
        if self._click_en_botones(self.botones_juego, pos):
            return
        celda = self._celda_en_posicion(pos)
        if celda is not None and self.on_celda_click is not None:
            self.on_celda_click(*celda)

    def _click_en_botones(self, botones, pos):
        for boton in botones:
            if boton["rect"].collidepoint(pos):
                self._activar_boton(boton)
                return True
        return False

    def _activar_boton(self, boton):
        if not boton["habilitado"]:
            self._mostrar_aviso(boton["accion"])
            return
        accion = boton["accion"]
        if accion == "salir":
            self.ejecutando = False
        elif accion == "volver_menu":
            self.pantalla = "menu"
        elif accion == "reiniciar" or accion == "otra_vez":
            if self.on_reiniciar is not None:
                self.on_reiniciar()
        elif accion == "jugar_humano":
            self.pantalla = "juego"
            self.modo = self.MODO_HUMANO
            if self.on_cambio_modo is not None:
                self.on_cambio_modo()

    def _mostrar_aviso(self, accion):
        if accion == "aviso_minimax":
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
        self._dibujar_fondo()
        if self.pantalla == "menu":
            self._dibujar_menu()
        else:
            self._dibujar_juego()
            if self.partida_terminada:
                self._dibujar_cartel_final()

    def _dibujar_fondo(self):
        """Degradado vertical de arriba hacia abajo."""
        for y in range(self.ALTO):
            mezcla = y / self.ALTO
            color = tuple(
                int(a + (b - a) * mezcla)
                for a, b in zip(self.FONDO_ARRIBA, self.FONDO_ABAJO)
            )
            pygame.draw.line(self.ventana, color, (0, y), (self.ANCHO, y))

    def _dibujar_menu(self):
        # Decoracion: una X y una O gigantes y tenues a los lados
        self._dibujar_ficha_gigante("X", 90, 340, 60)
        self._dibujar_ficha_gigante("O", 630, 120, 60)

        parte1 = self.fuente_titulo.render("Tres en ", True, self.TEXTO)
        parte2 = self.fuente_titulo.render("Raya", True, self.TEXTO_ACENTO)
        ancho_total = parte1.get_width() + parte2.get_width()
        x = (self.ANCHO - ancho_total) // 2
        self.ventana.blit(parte1, (x, 95))
        self.ventana.blit(parte2, (x + parte1.get_width(), 95))

        subtitulo = self.fuente.render(
            "El clásico juego de estrategia", True, self.TEXTO_APAGADO)
        self.ventana.blit(
            subtitulo, ((self.ANCHO - subtitulo.get_width()) // 2, 175))

        for boton in self.botones_menu:
            self._dibujar_boton(boton)

        if self.aviso is not None:
            if pygame.time.get_ticks() > self._aviso_hasta:
                self.aviso = None
            else:
                superficie = self.fuente.render(self.aviso, True, self.AVISO)
                pos_x = (self.ANCHO - superficie.get_width()) // 2
                self.ventana.blit(superficie, (pos_x, 445))

    def _dibujar_ficha_gigante(self, valor, centro_x, centro_y, radio):
        capa = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        color = self.FICHA_X if valor == "X" else self.FICHA_O
        color = color + (28,)  # muy transparente
        if valor == "X":
            pygame.draw.line(capa, color,
                             (centro_x - radio, centro_y - radio),
                             (centro_x + radio, centro_y + radio), 22)
            pygame.draw.line(capa, color,
                             (centro_x - radio, centro_y + radio),
                             (centro_x + radio, centro_y - radio), 22)
        else:
            pygame.draw.circle(capa, color, (centro_x, centro_y),
                               radio, 20)
        self.ventana.blit(capa, (0, 0))

    def _dibujar_juego(self):
        self._dibujar_tablero()
        self._dibujar_panel()

    def _dibujar_tablero(self):
        raton = pygame.mouse.get_pos()
        for fila in range(3):
            for columna in range(3):
                x = self.MARGEN + columna * self.TAM_CELDA
                y = self.MARGEN + fila * self.TAM_CELDA
                rect = pygame.Rect(x, y, self.TAM_CELDA, self.TAM_CELDA)

                resaltada = (fila, columna) in self.celdas_resaltadas
                if resaltada:
                    color = self.RESALTE
                elif (not self.partida_terminada
                      and self.tablero[fila][columna] == " "
                      and rect.inflate(-6, -6).collidepoint(raton)):
                    color = self.CELDA_HOVER
                else:
                    color = self.CELDA
                pygame.draw.rect(self.ventana, color, rect.inflate(-6, -6),
                                 border_radius=10)

                self._dibujar_ficha(fila, columna)

    def _dibujar_ficha(self, fila, columna):
        valor = self.tablero[fila][columna]
        if valor == " ":
            return
        centro_x = self.MARGEN + columna * self.TAM_CELDA \
            + self.TAM_CELDA // 2
        centro_y = self.MARGEN + fila * self.TAM_CELDA \
            + self.TAM_CELDA // 2
        radio = self.TAM_CELDA // 2 - 34
        if valor == "X":
            color = self.FICHA_X
            pygame.draw.line(self.ventana, color,
                             (centro_x - radio, centro_y - radio),
                             (centro_x + radio, centro_y + radio), 12)
            pygame.draw.line(self.ventana, color,
                             (centro_x - radio, centro_y + radio),
                             (centro_x + radio, centro_y - radio), 12)
        else:
            pygame.draw.circle(self.ventana, self.FICHA_O,
                               (centro_x, centro_y), radio, 10)

    def _dibujar_panel(self):
        pygame.draw.rect(self.ventana, self.PANEL,
                         (self.PANEL_X, 0, self.ANCHO - self.PANEL_X,
                          self.ALTO))

        modo = self.fuente_pequena.render(self.modo, True,
                                          self.TEXTO_APAGADO)
        self.ventana.blit(modo, (self.PANEL_X + 15, 20))

        estado = self.fuente_grande.render(self.texto_estado, True,
                                           self.TEXTO)
        self.ventana.blit(estado, (self.PANEL_X + 15, 55))

        self._dibujar_metricas()

        for boton in self.botones_juego:
            self._dibujar_boton(boton)

    def _dibujar_metricas(self):
        y = 160
        pygame.draw.line(self.ventana, self.LINEAS,
                         (self.PANEL_X + 15, y - 15),
                         (self.ANCHO - 15, y - 15), 1)
        nodos = "-" if self.nodos is None else str(self.nodos)
        tiempo = "-" if self.tiempo_ms is None \
            else "{:.2f} ms".format(self.tiempo_ms)
        for etiqueta in ("Nodos explorados: " + nodos,
                         "Tiempo: " + tiempo):
            superficie = self.fuente.render(etiqueta, True, self.TEXTO)
            self.ventana.blit(superficie, (self.PANEL_X + 15, y))
            y += 30

    def _dibujar_cartel_final(self):
        # Oscurece la partida detras del cartel
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill((10, 12, 20, 170))
        self.ventana.blit(velo, (0, 0))

        cartel = pygame.Rect(110, 140, 500, 260)
        pygame.draw.rect(self.ventana, self.CARTEL, cartel, border_radius=14)
        pygame.draw.rect(self.ventana, self.BOTON_BORDE, cartel, 2,
                         border_radius=14)

        resultado = self.fuente_titulo.render(self.texto_estado, True,
                                              self.TEXTO)
        pos_x = cartel.x + (cartel.width - resultado.get_width()) // 2
        self.ventana.blit(resultado, (pos_x, 195))

        for boton in self.botones_fin:
            self._dibujar_boton(boton)

    def _dibujar_boton(self, boton):
        rect = boton["rect"]
        raton = pygame.mouse.get_pos()
        en_hover = boton["habilitado"] and rect.collidepoint(raton)

        if not boton["habilitado"]:
            color, color_texto = self.BOTON, self.TEXTO_APAGADO
        elif en_hover:
            color, color_texto = self.BOTON_HOVER, self.TEXTO
        else:
            color, color_texto = self.BOTON, self.TEXTO

        # Sombra debajo del boton
        sombra = rect.copy()
        sombra.y += 3
        pygame.draw.rect(self.ventana, (18, 20, 32), sombra,
                         border_radius=10)
        pygame.draw.rect(self.ventana, color, rect, border_radius=10)
        pygame.draw.rect(self.ventana, self.BOTON_BORDE, rect, 1,
                         border_radius=10)

        texto = self.fuente_boton.render(boton["texto"], True, color_texto)
        pos_x = rect.x + (rect.width - texto.get_width()) // 2
        pos_y = rect.y + (rect.height - texto.get_height()) // 2
        self.ventana.blit(texto, (pos_x, pos_y))

    # Metodos que usa el controlador para actualizar la interfaz

    def actualizar_tablero(self, tablero):
        """Guarda el estado del tablero para dibujarlo en el proximo
        frame."""
        self.tablero = [fila[:] for fila in tablero]

    def resaltar_celdas(self, celdas):
        """Marca las casillas de la linea ganadora."""
        self.celdas_resaltadas = list(celdas)

    def mostrar_turno(self, jugador):
        self.partida_terminada = False
        self.celdas_resaltadas = []
        self.texto_estado = "Turno del jugador " + jugador

    def mostrar_ganador(self, jugador):
        self.partida_terminada = True
        self.texto_estado = "¡Gana " + jugador + "!"

    def mostrar_empate(self):
        self.partida_terminada = True
        self.texto_estado = "¡Empate!"

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
