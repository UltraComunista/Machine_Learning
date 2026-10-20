"""Pruebas de la API REST (api/app.py) con el cliente de prueba de Flask."""

import unittest

from api.app import app


class TestApiRest(unittest.TestCase):
    """Verifica las rutas de partidas y la del arbol de decision."""

    def setUp(self):
        self.cliente = app.test_client()

    def crear_partida(self, modo="hh"):
        respuesta = self.cliente.post(
            "/api/partidas", json={"modo": modo})
        self.assertEqual(respuesta.status_code, 200)
        return respuesta.get_json()

    def jugar(self, identificador, fila, columna):
        return self.cliente.post(
            "/api/partidas/{}/movimientos".format(identificador),
            json={"fila": fila, "columna": columna})

    def test_estado_inicial(self):
        estado = self.crear_partida("hh")
        self.assertEqual(estado["turno"], "X")
        self.assertFalse(estado["terminado"])
        self.assertEqual(
            estado["tablero"], [[" "] * 3, [" "] * 3, [" "] * 3])

    def test_modo_invalido_rechazado(self):
        respuesta = self.cliente.post("/api/partidas", json={"modo": "ia"})
        self.assertEqual(respuesta.status_code, 400)

    def test_movimiento_alterna_turno_en_hh(self):
        estado = self.crear_partida("hh")
        self.jugar(estado["id"], 0, 0)
        respuesta = self.jugar(estado["id"], 1, 1)
        estado = respuesta.get_json()["estado"]
        self.assertEqual(estado["tablero"][0][0], "X")
        self.assertEqual(estado["tablero"][1][1], "O")
        self.assertEqual(estado["turno"], "X")

    def test_casilla_ocupada_rechazada(self):
        estado = self.crear_partida("hh")
        self.jugar(estado["id"], 0, 0)
        respuesta = self.jugar(estado["id"], 0, 0)
        self.assertEqual(respuesta.status_code, 400)

    def test_minimax_responde_con_metricas(self):
        estado = self.crear_partida("minimax")
        respuesta = self.jugar(estado["id"], 1, 1)
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.get_json()
        self.assertIn("ia", datos)
        jugada = datos["ia"]["jugada"]
        self.assertEqual(datos["estado"]["tablero"][jugada["fila"]]
                         [jugada["columna"]], "O")
        self.assertGreater(datos["ia"]["nodos"], 0)
        self.assertEqual(datos["estado"]["turno"], "X")

    def test_ml_responde_con_reglas(self):
        estado = self.crear_partida("ml")
        respuesta = self.jugar(estado["id"], 0, 0)
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.get_json()
        self.assertIn("reglas", datos["ia"])
        self.assertTrue(datos["ia"]["reglas"])
        jugada = datos["ia"]["jugada"]
        self.assertEqual(datos["estado"]["tablero"][jugada["fila"]]
                         [jugada["columna"]], "O")

    def test_movimiento_tras_terminar_rechazado(self):
        estado = self.crear_partida("hh")
        for fila, columna in [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]:
            respuesta = self.jugar(estado["id"], fila, columna)
        estado = respuesta.get_json()["estado"]
        self.assertTrue(estado["terminado"])
        self.assertEqual(estado["ganador"], "X")
        self.assertEqual(self.jugar(estado["id"], 2, 2).status_code, 400)

    def test_partida_inexistente_404(self):
        respuesta = self.cliente.get("/api/partidas/9999")
        self.assertEqual(respuesta.status_code, 404)

    def test_arbol_devuelve_precision_y_nodos(self):
        respuesta = self.cliente.get("/api/arbol")
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.get_json()
        self.assertGreater(datos["precision"], 0.9)
        self.assertIn("c", datos["raiz"]["nombre"])


if __name__ == "__main__":
    unittest.main()
