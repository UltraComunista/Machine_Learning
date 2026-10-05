"""Pruebas de integracion del modo Humano vs. Humano.

Verifican el flujo completo MVC: clics en la vista -> controlador ->
modelo -> vista actualizada. Usan el driver de video "dummy" de pygame
para no abrir ventanas durante las pruebas.
"""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from model.game_model import GameModel  # noqa: E402
from view.gui_view import GameView  # noqa: E402
from controller.game_controller import GameController  # noqa: E402


class TestIntegracionHumanoVsHumano(unittest.TestCase):
    """Simula partidas completas a traves de la interfaz."""

    def setUp(self):
        self.vista = GameView()
        self.modelo = GameModel()
        self.controlador = GameController(self.modelo, self.vista)

    def tearDown(self):
        pygame.display.quit()

    def jugar(self, movimientos):
        for fila, columna in movimientos:
            self.controlador.manejar_clic_celda(fila, columna)

    def test_victoria_de_x_en_fila(self):
        self.jugar([(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
        self.assertTrue(self.modelo.hay_ganador("X"))
        self.assertEqual(self.vista.texto_estado, "Gana X")
        self.assertEqual(self.vista.tablero[0][0], "X")
        self.assertEqual(self.vista.tablero[0][2], "X")

    def test_victoria_de_o_en_columna(self):
        self.jugar([(0, 0), (1, 1), (0, 2), (0, 1), (2, 0), (2, 1)])
        self.assertTrue(self.modelo.hay_ganador("O"))
        self.assertEqual(self.vista.texto_estado, "Gana O")

    def test_victoria_en_diagonal(self):
        self.jugar([(0, 0), (0, 1), (1, 1), (0, 2), (2, 2)])
        self.assertTrue(self.modelo.hay_ganador("X"))

    def test_empate(self):
        self.jugar([(0, 0), (0, 1), (0, 2),
                    (1, 1), (1, 0), (2, 0),
                    (1, 2), (2, 2), (2, 1)])
        self.assertTrue(self.modelo.hay_empate())
        self.assertEqual(self.vista.texto_estado, "Empate")

    def test_clic_en_casilla_ocupada_se_ignora(self):
        self.controlador.manejar_clic_celda(1, 1)
        self.controlador.manejar_clic_celda(1, 1)
        self.assertEqual(self.modelo.tablero[1][1], "X")
        # El turno no avanza: sigue siendo O
        self.assertEqual(self.modelo.jugador_actual, "O")

    def test_clics_despues_de_terminar_no_cambian_nada(self):
        self.jugar([(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
        self.controlador.manejar_clic_celda(2, 2)
        self.assertEqual(self.modelo.tablero[2][2], " ")

    def test_reinicio_desde_la_vista(self):
        self.jugar([(0, 0), (1, 1)])
        self.controlador.manejar_reinicio()
        for fila in range(3):
            for columna in range(3):
                self.assertEqual(self.modelo.tablero[fila][columna], " ")
                self.assertEqual(self.vista.tablero[fila][columna], " ")
        self.assertEqual(self.vista.texto_estado, "Turno de X")
        self.assertEqual(self.modelo.jugador_actual, "X")

    def test_cambio_de_modo_reinicia_la_partida(self):
        self.jugar([(1, 1)])
        self.controlador.manejar_cambio_modo()
        self.assertEqual(self.modelo.tablero[1][1], " ")

    def test_modo_minimax_bloqueado_muestra_aviso(self):
        boton = next(b for b in self.vista.botones
                     if b["accion"] == "modo_minimax")
        centro = boton["rect"].center
        self.vista._manejar_click(centro)
        self.assertEqual(self.vista.aviso, "Disponible en la semana 2")
        self.assertEqual(self.vista.obtener_modo(), GameView.MODO_HUMANO)

    def test_modo_ml_bloqueado_muestra_aviso(self):
        boton = next(b for b in self.vista.botones
                     if b["accion"] == "modo_ml")
        centro = boton["rect"].center
        self.vista._manejar_click(centro)
        self.assertEqual(self.vista.aviso, "Disponible en la semana 3")
        self.assertEqual(self.vista.obtener_modo(), GameView.MODO_HUMANO)


if __name__ == "__main__":
    unittest.main()
