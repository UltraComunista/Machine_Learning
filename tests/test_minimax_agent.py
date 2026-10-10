"""Pruebas de la funcion de evaluacion y del algoritmo Minimax."""

import random
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


class TestMinimaxRecursivo(unittest.TestCase):
    """Verifica que el agente elige jugadas optimas."""

    def setUp(self):
        self.agente = MinimaxAgent(jugador_ia="O", jugador_humano="X")

    def jugar(self, modelo, movimientos):
        for fila, columna in movimientos:
            modelo.hacer_movimiento(fila, columna)

    def test_elige_la_victoria_inmediata(self):
        # Es turno de O y tiene (1,0) y (1,1): debe completar la fila
        # 1 en (1,2), aunque X tambien amenace en (0,2); ganar va
        # antes que bloquear
        modelo = GameModel()
        self.jugar(modelo, [(0, 0), (1, 1), (0, 1), (1, 0), (2, 2)])
        self.assertEqual(self.agente.mejor_jugada(modelo), (1, 2))

    def test_bloquea_la_victoria_del_humano(self):
        # X tiene (0,0) y (0,1): O debe jugar en (0,2) para tapar
        modelo = GameModel()
        self.jugar(modelo, [(0, 0), (1, 1), (0, 1)])
        self.assertEqual(self.agente.mejor_jugada(modelo), (0, 2))

    def test_desde_el_inicio_el_mejor_resultado_es_empate(self):
        # Con juego perfecto por ambos lados nadie puede ganar
        modelo = GameModel()
        modelo.hacer_movimiento(1, 1)  # mueve X (el humano)
        puntaje = self.agente.minimax(modelo, 0, True)
        self.assertEqual(puntaje, 0)

    def test_cuenta_los_nodos_evaluados(self):
        modelo = GameModel()
        self.jugar(modelo, [(1, 1)])  # X en el centro
        self.agente.mejor_jugada(modelo)
        self.assertGreater(self.agente.nodos_evaluados, 0)

    def test_el_agente_es_imbatible(self):
        # Contra un jugador aleatorio, la IA nunca pierde
        aleatorio = random.Random(42)
        for _ in range(30):
            modelo = GameModel()
            agente = MinimaxAgent()
            while not modelo.juego_terminado():
                if modelo.jugador_actual == agente.jugador_ia:
                    fila, columna = agente.mejor_jugada(modelo)
                else:
                    fila, columna = aleatorio.choice(
                        modelo.obtener_movimientos_disponibles())
                modelo.hacer_movimiento(fila, columna)
            self.assertFalse(modelo.hay_ganador(agente.jugador_humano))


if __name__ == "__main__":
    unittest.main()
