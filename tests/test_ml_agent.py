"""Pruebas del generador de datos para el agente de ML."""

import os
import tempfile
import unittest

from model.ml_agent import (
    AgenteArbol,
    GeneradorDatos,
    casilla_a_numero,
    construir_dataset,
    cargar_dataset,
    codificar_tablero,
    entrenar_arbol,
    guardar_dataset,
    validar_dataset,
)
from model.game_model import GameModel

RUTA_DATASET = os.path.join("data", "partidas.csv")


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


class TestDataset(unittest.TestCase):
    """Verifica la estructura, validacion y guardado del CSV."""

    def setUp(self):
        self.generador = GeneradorDatos(semilla=7)
        self.datos, _ = self.generador.generar(3)

    def test_el_dataset_tiene_10_columnas_con_nombre(self):
        tabla = construir_dataset(self.datos)
        self.assertEqual(list(tabla.columns),
                         ["c0", "c1", "c2", "c3", "c4",
                          "c5", "c6", "c7", "c8", "jugada"])

    def test_el_dataset_generado_no_tiene_problemas(self):
        tabla = construir_dataset(self.datos)
        self.assertEqual(validar_dataset(tabla), [])

    def test_detecta_valores_invalidos(self):
        tabla = construir_dataset([[9] * 9 + [0]])
        self.assertTrue(validar_dataset(tabla))

    def test_detecta_etiquetas_fuera_de_rango(self):
        tabla = construir_dataset([[0] * 9 + [12]])
        self.assertTrue(validar_dataset(tabla))

    def test_detecta_dataset_vacio(self):
        tabla = construir_dataset([])
        self.assertTrue(validar_dataset(tabla))

    def test_guardar_dataset_escribe_el_csv_con_encabezado(self):
        tabla = construir_dataset(self.datos)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "prueba.csv")
            guardar_dataset(tabla, ruta)
            with open(ruta) as archivo:
                lineas = archivo.read().splitlines()
        self.assertEqual(lineas[0],
                         "c0,c1,c2,c3,c4,c5,c6,c7,c8,jugada")
        self.assertEqual(len(lineas), len(self.datos) + 1)


class TestArbolDecision(unittest.TestCase):
    """Verifica el entrenamiento y las predicciones del arbol."""

    @classmethod
    def setUpClass(cls):
        # Se entrena una sola vez para toda la clase: el entrenamiento
        # es rapido, pero no hace falta repetirlo en cada prueba.
        cls.tabla = cargar_dataset(RUTA_DATASET)
        cls.arbol, cls.precision = entrenar_arbol(cls.tabla)
        cls.agente = AgenteArbol(cls.arbol)

    def test_cargar_dataset_lee_el_csv_del_proyecto(self):
        self.assertEqual(len(self.tabla), 6844)
        self.assertEqual(list(self.tabla.columns),
                         ["c0", "c1", "c2", "c3", "c4",
                          "c5", "c6", "c7", "c8", "jugada"])

    def test_la_precision_es_alta(self):
        # El arbol debe acertar la gran mayoria de las jugadas de
        # Minimax que no vio durante el entrenamiento.
        self.assertGreater(self.precision, 0.75)

    def test_la_prediccion_devuelve_una_casilla_valida(self):
        modelo = GameModel()
        modelo.hacer_movimiento(0, 0)  # mueve X, turno de la IA
        jugada = self.agente.predecir_jugada(modelo.tablero)
        self.assertTrue(0 <= jugada <= 8)

    def test_mejor_jugada_devuelve_una_casilla_libre(self):
        # Misma interfaz que MinimaxAgent: recibe el modelo y
        # devuelve (fila, columna) de una casilla disponible.
        modelo = GameModel()
        modelo.hacer_movimiento(1, 1)
        fila, columna = self.agente.mejor_jugada(modelo)
        self.assertTrue(modelo.es_movimiento_valido(fila, columna))


if __name__ == "__main__":
    unittest.main()
