"""Interfaz grafica del juego construida con pygame.

Estilo pixel art: el fondo, las fichas y los botones se dibujan con
rectangulos, sin imagenes externas. La fuente Press Start 2P es de
Codeman38 y se distribuye bajo la licencia SIL OFL.

La vista solo renderiza el estado que recibe del controlador y le
notifica cuando el usuario hace clic en una casilla o en un boton.
No conoce las reglas del juego: toda la logica vive en el modelo.

Mapa de la clase, por bloques:

- Constantes: paleta de colores y geometria (ANCHO, MARGEN, etc.).
- __init__: crea la ventana, las fuentes y los grupos de botones.
- Construccion: _crear_botones_menu/_juego/_fin definen rect y accion
  de cada boton (accion es el identificador interno, texto lo visible).
- Eventos: ejecutar() es el bucle del juego (30 fps); _manejar_click
  decide si el clic cayó en un boton o en una casilla del tablero;
  _activar_boton ejecuta la accion correspondiente.
- Dibujo: _dibujar_* pintan cada cosa (escena, menu, tablero, panel,
  cartel final, botones). Se redibuja TODO en cada vuelta del bucle.
- API del controlador: actualizar_tablero, mostrar_turno/ganador/
  empate, mostrar_metricas, etc. Son los metodos que el controlador
  llama para que la vista refleje el estado del modelo.
"""

import math
import os

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
    CIELO_ARRIBA = (110, 190, 245)
    CIELO_ABAJO = (205, 235, 250)
    NUBE = (255, 255, 255)
    NUBE_SOMBRA = (225, 235, 245)
    COLINA = (152, 228, 160)
    ARBUSTO = (96, 198, 110)
    PASTO = (86, 208, 96)
    PASTO_OSCURO = (58, 178, 82)
    LADRILLO = (150, 150, 162)
    MORTERO = (105, 105, 118)
    CASILLA = (255, 250, 230)
    CASILLA_HOVER = (255, 243, 170)
    CASILLA_GANADA = (255, 205, 60)
    REJA = (110, 75, 40)
    PANEL = (255, 243, 200)
    PANEL_BORDE = (120, 80, 40)
    TEXTO = (92, 60, 30)
    TEXTO_APAGADO = (170, 150, 125)
    FICHA_X = (56, 105, 220)
    FICHA_O = (238, 92, 60)
    CORAZON = (228, 52, 52)
    BOTON = (104, 190, 100)
    BOTON_HOVER = (128, 216, 120)
    BOTON_APAGADO = (172, 172, 172)
    BOTON_CLARO = (190, 240, 180)
    BOTON_OSCURO = (60, 130, 62)
    BOTON_SALIR = (222, 104, 88)
    BOTON_SALIR_HOVER = (238, 128, 110)
    BOTON_SALIR_OSCURO = (150, 60, 50)
    CARTEL = (255, 248, 222)

    # Geometria de la ventana: aqui se ajusta el espaciado general.
    # El tablero ocupa desde MARGEN hasta MARGEN + 3 * TAM_CELDA, y el
    # marco de ladrillos se dibuja 14 px mas alla. Si el panel queda
    # muy pegado al tablero, sube PANEL_X (y ANCHO para que quepa).
    ANCHO = 960      # ancho total de la ventana
    ALTO = 600       # alto total de la ventana
    MARGEN = 40      # separacion del tablero con el borde izq. y sup.
    TAM_CELDA = 160  # tamano de cada casilla del tablero
    PANEL_X = 560    # posicion X donde empieza el panel lateral

    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RUTA_FUENTE = os.path.join(
        _BASE, "assets", "fonts", "PressStart2P-Regular.ttf")

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tres en Raya")
        self.ventana = pygame.display.set_mode((self.ANCHO, self.ALTO))
        self.reloj = pygame.time.Clock()

        self.fuente_titulo = pygame.font.Font(self.RUTA_FUENTE, 34)
        self.fuente_grande = pygame.font.Font(self.RUTA_FUENTE, 15)
        self.fuente = pygame.font.Font(self.RUTA_FUENTE, 12)
        self.fuente_pequena = pygame.font.Font(self.RUTA_FUENTE, 10)

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

        # Referencia al controlador: main.py se la asigna despues de
        # crear ambos. Con ella la vista le avisa directo cuando el
        # usuario hace clic, sin conocer la logica del juego.
        self.controlador = None

        self.botones_menu = self._crear_botones_menu()
        self.botones_juego = self._crear_botones_juego()
        self.botones_fin = self._crear_botones_fin()

    # Construccion de la interfaz

    def _crear_botones_menu(self):
        ancho, alto = 430, 50
        x = (self.ANCHO - ancho) // 2
        return [
            {"rect": pygame.Rect(x, 230, ancho, alto),
             "texto": "Humano vs. Humano",
             "accion": "jugar_humano", "habilitado": True},
            {"rect": pygame.Rect(x, 295, ancho, alto),
             "texto": "Humano vs. IA Minimax",
             "accion": "jugar_minimax", "habilitado": True},
            {"rect": pygame.Rect(x, 360, ancho, alto),
             "texto": "Humano vs. IA Machine Learning",
             "accion": "aviso_ml", "habilitado": False},
            {"rect": pygame.Rect(x, 445, ancho, alto),
             "texto": "Salir",
             "accion": "salir", "habilitado": True, "salir": True},
        ]

    def _crear_botones_juego(self):
        ancho, alto = 160, 42
        x = self.PANEL_X + 15
        return [
            {"rect": pygame.Rect(x, 415, ancho, alto),
             "texto": "Reiniciar",
             "accion": "reiniciar", "habilitado": True},
            {"rect": pygame.Rect(x + 180, 415, ancho, alto),
             "texto": "Menú",
             "accion": "volver_menu", "habilitado": True},
        ]

    def _crear_botones_fin(self):
        ancho, alto = 220, 46
        y = 330
        return [
            {"rect": pygame.Rect(200, y, ancho, alto),
             "texto": "Jugar de nuevo",
             "accion": "otra_vez", "habilitado": True},
            {"rect": pygame.Rect(480, y, ancho, alto),
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
        if celda is not None and self.controlador is not None:
            self.controlador.manejar_clic_celda(*celda)

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
            if self.controlador is not None:
                self.controlador.manejar_reinicio()
        elif accion == "jugar_humano":
            self.pantalla = "juego"
            self.modo = self.MODO_HUMANO
            if self.controlador is not None:
                self.controlador.manejar_cambio_modo()
        elif accion == "jugar_minimax":
            self.pantalla = "juego"
            self.modo = self.MODO_MINIMAX
            if self.controlador is not None:
                self.controlador.manejar_cambio_modo()

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
        self._dibujar_escena()
        if self.pantalla == "menu":
            self._dibujar_menu()
        else:
            self._dibujar_juego()
            if self.partida_terminada:
                self._dibujar_cartel_final()

    def _dibujar_escena(self):
        """Cielo, nubes, colinas, pasto y corazones de decoracion."""
        for y in range(self.ALTO):
            mezcla = y / self.ALTO
            color = tuple(
                int(a + (b - a) * mezcla)
                for a, b in zip(self.CIELO_ARRIBA, self.CIELO_ABAJO)
            )
            pygame.draw.line(self.ventana, color, (0, y), (self.ANCHO, y))

        self._dibujar_nube(70, 70, 2)
        self._dibujar_nube(330, 40, 1)
        self._dibujar_nube(660, 90, 2)

        # Colinas y arbustos del fondo
        pygame.draw.circle(self.ventana, self.COLINA, (80, 520), 130)
        pygame.draw.circle(self.ventana, self.COLINA, (280, 540), 110)
        pygame.draw.circle(self.ventana, self.ARBUSTO, (160, 530), 55)
        pygame.draw.circle(self.ventana, self.ARBUSTO, (380, 535), 45)

        # Franja de pasto con mechones
        pygame.draw.rect(self.ventana, self.PASTO,
                         (0, self.ALTO - 40, self.ANCHO, 40))
        for x in range(0, self.ANCHO, 26):
            alto_mecho = 8 if (x // 26) % 2 == 0 else 5
            pygame.draw.rect(self.ventana, self.PASTO_OSCURO,
                             (x, self.ALTO - 40, 14, alto_mecho))

    def _dibujar_nube(self, x, y, escala):
        sombra = (x + 4 * escala, y + 5 * escala, 90 * escala, 24 * escala)
        pygame.draw.rect(self.ventana, self.NUBE_SOMBRA, sombra)
        pygame.draw.rect(self.ventana, self.NUBE,
                         (x, y + 8 * escala, 90 * escala, 22 * escala))
        pygame.draw.rect(self.ventana, self.NUBE,
                         (x + 12 * escala, y, 34 * escala, 20 * escala))
        pygame.draw.rect(self.ventana, self.NUBE,
                         (x + 44 * escala, y - 6 * escala, 38 * escala,
                          26 * escala))
        pygame.draw.rect(self.ventana, self.NUBE,
                         (x + 66 * escala, y + 2 * escala, 26 * escala,
                          16 * escala))

    def _dibujar_menu(self):
        titulo = self.fuente_titulo.render("Tres en Raya", True,
                                           self.TEXTO)

        x = (self.ANCHO - titulo.get_width()) // 2
        # self.ventana.blit(sombra, (x + 4, 108))
        self.ventana.blit(titulo, (x, 100))

        for boton in self.botones_menu:
            self._dibujar_boton(boton)

        if self.aviso is not None:
            if pygame.time.get_ticks() > self._aviso_hasta:
                self.aviso = None
            else:
                superficie = self.fuente.render(self.aviso, True,
                                                self.FICHA_O)
                pos_x = (self.ANCHO - superficie.get_width()) // 2
                self.ventana.blit(superficie, (pos_x, 425))

    def _dibujar_juego(self):
        self._dibujar_marco_tablero()
        self._dibujar_tablero()
        self._dibujar_panel()

    def _dibujar_marco_tablero(self):
        """Marco de ladrillos alrededor del tablero."""
        x0 = self.MARGEN - 14
        y0 = self.MARGEN - 14
        lado = 3 * self.TAM_CELDA + 28
        pygame.draw.rect(self.ventana, self.LADRILLO, (x0, y0, lado, lado))
        # Juntas horizontales del muro
        for y in range(y0 + 8, y0 + lado, 16):
            pygame.draw.line(self.ventana, self.MORTERO, (x0, y),
                             (x0 + lado, y), 2)
        # Juntas verticales, corridas en cada hilada
        hilada = 0
        for y in range(y0, y0 + lado, 16):
            desfase = 10 if hilada % 2 == 0 else 22
            for x in range(x0 + desfase, x0 + lado, 24):
                pygame.draw.line(self.ventana, self.MORTERO, (x, y),
                                 (x, min(y + 16, y0 + lado)), 2)
            hilada += 1

    def _dibujar_tablero(self):
        raton = pygame.mouse.get_pos()
        for fila in range(3):
            for columna in range(3):
                x = self.MARGEN + columna * self.TAM_CELDA
                y = self.MARGEN + fila * self.TAM_CELDA
                rect = pygame.Rect(x, y, self.TAM_CELDA, self.TAM_CELDA)

                if (fila, columna) in self.celdas_resaltadas:
                    color = self.CASILLA_GANADA
                elif (not self.partida_terminada
                      and self.tablero[fila][columna] == " "
                      and rect.inflate(-8, -8).collidepoint(raton)):
                    color = self.CASILLA_HOVER
                else:
                    color = self.CASILLA
                pygame.draw.rect(self.ventana, color,
                                 rect.inflate(-8, -8))
                pygame.draw.rect(self.ventana, self.REJA,
                                 rect.inflate(-8, -8), 3)

                self._dibujar_ficha(fila, columna)

    def _dibujar_ficha(self, fila, columna):
        valor = self.tablero[fila][columna]
        if valor == " ":
            return
        centro_x = self.MARGEN + columna * self.TAM_CELDA \
            + self.TAM_CELDA // 2
        centro_y = self.MARGEN + fila * self.TAM_CELDA \
            + self.TAM_CELDA // 2
        radio = self.TAM_CELDA // 2 - 40
        if valor == "X":
            color = self.FICHA_X
            grosor = 16
            pygame.draw.line(self.ventana, color,
                             (centro_x - radio, centro_y - radio),
                             (centro_x + radio, centro_y + radio), grosor)
            pygame.draw.line(self.ventana, color,
                             (centro_x - radio, centro_y + radio),
                             (centro_x + radio, centro_y - radio), grosor)
            # Taponcitos cuadrados en las puntas, aire pixel
            for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                px = centro_x + dx * radio - 8
                py = centro_y + dy * radio - 8
                pygame.draw.rect(self.ventana, color, (px, py, 16, 16))
        else:
            # O hecha de bloques alrededor de un circulo
            color = self.FICHA_O
            bloque = 18
            for i in range(12):
                angulo = 2 * math.pi * i / 12
                px = centro_x + int(radio * math.cos(angulo)) - bloque // 2
                py = centro_y + int(radio * math.sin(angulo)) - bloque // 2
                pygame.draw.rect(self.ventana, color,
                                 (px, py, bloque, bloque))

    def _dibujar_panel(self):
        pygame.draw.rect(self.ventana, self.PANEL,
                         (self.PANEL_X, 0, self.ANCHO - self.PANEL_X,
                          self.ALTO))
        pygame.draw.rect(self.ventana, self.PANEL_BORDE,
                         (self.PANEL_X, 0, self.ANCHO - self.PANEL_X,
                          self.ALTO), 4)
        pygame.draw.line(self.ventana, self.PANEL_BORDE,
                         (self.PANEL_X + 8, self.ALTO - 12),
                         (self.ANCHO - 8, self.ALTO - 12), 2)

        modo = self.fuente_pequena.render(self.modo, True,
                                          self.TEXTO_APAGADO)
        self.ventana.blit(modo, (self.PANEL_X + 20, 24))

        estado = self.fuente_grande.render(self.texto_estado, True,
                                           self.TEXTO)
        self.ventana.blit(estado, (self.PANEL_X + 20, 60))

        self._dibujar_metricas()

        for boton in self.botones_juego:
            self._dibujar_boton(boton)

    def _formatear_tiempo(self, milisegundos):
        """Muestra el tiempo en segundos si tardo mas de un segundo."""
        if milisegundos >= 1000:
            return "{:.2f} s".format(milisegundos / 1000)
        return "{:.2f} ms".format(milisegundos)

    def _dibujar_metricas(self):
        y = 150
        pygame.draw.line(self.ventana, self.PANEL_BORDE,
                         (self.PANEL_X + 20, y - 12),
                         (self.ANCHO - 20, y - 12), 2)
        nodos = "-" if self.nodos is None else str(self.nodos)
        tiempo = "-" if self.tiempo_ms is None \
            else self._formatear_tiempo(self.tiempo_ms)
        for etiqueta in ("Nodos: " + nodos, "Tiempo: " + tiempo):
            superficie = self.fuente.render(etiqueta, True, self.TEXTO)
            self.ventana.blit(superficie, (self.PANEL_X + 20, y))
            y += 28

    def _dibujar_cartel_final(self):
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill((40, 60, 40, 130))
        self.ventana.blit(velo, (0, 0))

        cartel = pygame.Rect(170, 140, 560, 260)
        pygame.draw.rect(self.ventana, self.CARTEL, cartel)
        pygame.draw.rect(self.ventana, self.PANEL_BORDE, cartel, 4)

        resultado = self.fuente_titulo.render(self.texto_estado, True,
                                              self.TEXTO)
        pos_x = cartel.x + (cartel.width - resultado.get_width()) // 2
        self.ventana.blit(resultado, (pos_x, 205))

        for boton in self.botones_fin:
            self._dibujar_boton(boton)

    def _dibujar_boton(self, boton):
        rect = boton["rect"]
        raton = pygame.mouse.get_pos()
        en_hover = boton["habilitado"] and rect.collidepoint(raton)

        if not boton["habilitado"]:
            base, texto = self.BOTON_APAGADO, (235, 235, 235)
        elif boton.get("salir"):
            base = self.BOTON_SALIR_HOVER if en_hover else self.BOTON_SALIR
            texto = (255, 255, 255)
        else:
            base = self.BOTON_HOVER if en_hover else self.BOTON
            texto = self.TEXTO

        pygame.draw.rect(self.ventana, base, rect)
        # Relieve pixel: claro arriba/izquierda, oscuro abajo/derecha
        if boton["habilitado"]:
            claro = (self.BOTON_CLARO if not boton.get("salir")
                     else (250, 170, 155))
            oscuro = (self.BOTON_OSCURO if not boton.get("salir")
                      else self.BOTON_SALIR_OSCURO)
        else:
            claro, oscuro = (200, 200, 200), (140, 140, 140)
        pygame.draw.line(self.ventana, claro, rect.topleft,
                         (rect.right - 1, rect.top), 3)
        pygame.draw.line(self.ventana, claro, rect.topleft,
                         (rect.left, rect.bottom - 1), 3)
        pygame.draw.line(self.ventana, oscuro, (rect.left, rect.bottom - 1),
                         (rect.right - 1, rect.bottom - 1), 3)
        pygame.draw.line(self.ventana, oscuro, (rect.right - 1, rect.top),
                         (rect.right - 1, rect.bottom - 1), 3)

        fuente = self.fuente_grande if rect.width <= 180 else self.fuente
        superficie = fuente.render(boton["texto"], True, texto)
        pos_x = rect.x + (rect.width - superficie.get_width()) // 2
        pos_y = rect.y + (rect.height - superficie.get_height()) // 2
        self.ventana.blit(superficie, (pos_x, pos_y))

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
