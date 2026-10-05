"""Pruebas de integracion del modo Humano vs. Humano.

Verifican el flujo completo MVC: clics en la vista -> controlador ->
modelo -> vista actualizada.
"""

import unittest

from model.game_model import GameModel
from view.gui_view import GameView
from controller.game_controller import GameController


class TestIntegracionHumanoVsHumano(unittest.TestCase):
    """Simula partidas completas a traves de la interfaz."""

    def setUp(self):
        self.vista = GameView()
        self.vista.ventana.withdraw()
        self.modelo = GameModel()
        self.controlador = GameController(self.modelo, self.vista)

    def tearDown(self):
        self.vista.ventana.destroy()

    def jugar(self, movimientos):
        for fila, columna in movimientos:
            self.controlador.manejar_clic_celda(fila, columna)

    def test_victoria_de_x_en_fila(self):
        self.jugar([(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
        self.assertTrue(self.modelo.hay_ganador("X"))
        self.assertIn("Gana X", self.vista.etiqueta_estado.cget("text"))
        self.assertEqual(self.vista.botones[0][0].cget("text"), "X")
        self.assertEqual(self.vista.botones[0][2].cget("text"), "X")

    def test_victoria_de_o_en_columna(self):
        self.jugar([(0, 0), (1, 1), (0, 2), (0, 1), (2, 0), (2, 1)])
        self.assertTrue(self.modelo.hay_ganador("O"))
        self.assertIn("Gana O", self.vista.etiqueta_estado.cget("text"))

    def test_victoria_en_diagonal(self):
        self.jugar([(0, 0), (0, 1), (1, 1), (0, 2), (2, 2)])
        self.assertTrue(self.modelo.hay_ganador("X"))

    def test_empate(self):
        self.jugar([(0, 0), (0, 1), (0, 2),
                    (1, 1), (1, 0), (2, 0),
                    (1, 2), (2, 2), (2, 1)])
        self.assertTrue(self.modelo.hay_empate())
        self.assertIn("Empate", self.vista.etiqueta_estado.cget("text"))

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
                self.assertEqual(
                    self.vista.botones[fila][columna].cget("text"), " ")
        self.assertIn("Turno de X",
                      self.vista.etiqueta_estado.cget("text"))
        self.assertEqual(self.modelo.jugador_actual, "X")

    def test_cambio_de_modo_reinicia_la_partida(self):
        self.jugar([(1, 1)])
        self.controlador.manejar_cambio_modo()
        self.assertEqual(self.modelo.tablero[1][1], " ")


if __name__ == "__main__":
    unittest.main()
