"""Pruebas de la funcion de evaluacion del agente Minimax."""

import unittest

from model.game_model import GameModel
from model.minimax_agent import MinimaxAgent


class TestEvaluacionMinimax(unittest.TestCase):
    """Verifica los puntajes +10, -10 y 0 en estados terminales."""

    def setUp(self):
        self.agente = MinimaxAgent(jugador_ia="O", jugador_humano="X")
        self.modelo = GameModel()

    def jugar(self, movimientos):
        for fila, columna in movimientos:
            self.modelo.hacer_movimiento(fila, columna)

    def test_victoria_de_la_ia_puntua_10(self):
        # Gana O en la columna 1: O juega segundo
        self.jugar([(0, 0), (0, 1), (1, 0), (1, 1), (2, 2), (2, 1)])
        self.assertEqual(self.agente.evaluar(self.modelo), 10)

    def test_victoria_del_humano_puntua_menos_10(self):
        # Gana X en la fila 0
        self.jugar([(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
        self.assertEqual(self.agente.evaluar(self.modelo), -10)

    def test_empate_puntua_0(self):
        self.jugar([(0, 0), (0, 1), (0, 2),
                    (1, 1), (1, 0), (2, 0),
                    (1, 2), (2, 2), (2, 1)])
        self.assertEqual(self.agente.evaluar(self.modelo), 0)

    def test_partida_abierta_puntua_0(self):
        self.jugar([(1, 1)])
        self.assertEqual(self.agente.evaluar(self.modelo), 0)

    def test_tablero_vacio_puntua_0(self):
        self.assertEqual(self.agente.evaluar(self.modelo), 0)


if __name__ == "__main__":
    unittest.main()
