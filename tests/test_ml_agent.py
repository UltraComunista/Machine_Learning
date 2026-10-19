"""Pruebas del generador de datos para el agente de ML."""

import unittest

from model.ml_agent import (
    GeneradorDatos,
    casilla_a_numero,
    codificar_tablero,
)
from model.game_model import GameModel


class TestCodificacion(unittest.TestCase):
    """Verifica la conversion del tablero a numeros."""

    def test_tablero_vacio_se_codifica_con_ceros(self):
        modelo = GameModel()
        self.assertEqual(codificar_tablero(modelo.tablero),
                         [0, 0, 0, 0, 0, 0, 0, 0, 0])

    def test_las_fichas_usan_sus_codigos(self):
        modelo = GameModel()
        modelo.hacer_movimiento(0, 0)  # X
        modelo.hacer_movimiento(1, 1)  # O
        self.assertEqual(codificar_tablero(modelo.tablero),
                         [1, 0, 0, 0, 2, 0, 0, 0, 0])

    def test_casilla_a_numero_recorre_por_filas(self):
        self.assertEqual(casilla_a_numero(0, 0), 0)
        self.assertEqual(casilla_a_numero(0, 2), 2)
        self.assertEqual(casilla_a_numero(1, 0), 3)
        self.assertEqual(casilla_a_numero(2, 2), 8)


class TestGeneradorDatos(unittest.TestCase):
    """Verifica la simulacion de partidas y el registro de jugadas."""

    def setUp(self):
        self.generador = GeneradorDatos(semilla=42)

    def test_cada_fila_tiene_9_casillas_mas_la_etiqueta(self):
        filas, _ = self.generador.simular_partida()
        self.assertTrue(filas)
        for fila in filas:
            self.assertEqual(len(fila), 10)

    def test_la_etiqueta_apunta_a_una_casilla_vacia(self):
        # Si la casilla elegida ya estuviera ocupada, el ejemplo
        # estaria mal: la IA solo puede jugar en casillas libres.
        filas, _ = self.generador.simular_partida()
        for fila in filas:
            casilla = fila[9]
            self.assertEqual(fila[casilla], 0)

    def test_la_etiqueta_esta_en_rango(self):
        filas, _ = self.generador.simular_partida()
        for fila in filas:
            self.assertTrue(0 <= fila[9] <= 8)

    def test_la_ia_nunca_pierde_contra_el_aleatorio(self):
        # Minimax juega perfecto: el resultado no puede ser victoria
        # de X. Si pasa, el generador esta registrando mal los datos.
        _, resultados = self.generador.generar(10)
        self.assertEqual(resultados["X"], 0)
        self.assertEqual(sum(resultados.values()), 10)

    def test_misma_semilla_genera_mismos_datos(self):
        otro = GeneradorDatos(semilla=42)
        datos_a, _ = self.generador.generar(5)
        datos_b, _ = otro.generar(5)
        self.assertEqual(datos_a, datos_b)

    def test_se_registran_las_jugadas_de_la_ia(self):
        # En cada partida la IA mueve como maximo 5 veces (O es
        # segundo) y como minimo 1.
        filas, _ = self.generador.simular_partida()
        self.assertTrue(1 <= len(filas) <= 5)


if __name__ == "__main__":
    unittest.main()
