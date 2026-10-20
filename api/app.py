"""API REST del Tres en Raya con agentes Minimax y Machine Learning.

Expone el mismo modelo y agentes del juego de escritorio (pygame) como
servicio web, para que el flujo MVC se vea como rutas HTTP:

- POST /api/partidas              crea una partida (modo hh, minimax o ml)
- POST /api/partidas/<id>/movimientos  juega una casilla; si el modo tiene
                                      IA, esta responde en la misma llamada
- GET  /api/partidas/<id>         consulta el estado de una partida
- GET  /api/arbol                 el arbol de decision del ML como JSON
- GET  /api/arbol/imagen          la imagen exportada con sklearn

Las partidas viven en memoria del servidor: un diccionario con el modelo
por ID. El humano siempre juega con X y empieza; la IA juega con O.

Uso:
    python3.13 api/app.py
    y abrir http://127.0.0.1:5000 en el navegador.
"""

import itertools
import os
import sys
import time

from flask import Flask, jsonify, request, send_from_directory

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from model.game_model import GameModel  # noqa: E402
from model.minimax_agent import MinimaxAgent  # noqa: E402
from model.ml_agent import (  # noqa: E402
    AgenteArbol,
    cargar_dataset,
    entrenar_arbol,
)

# static_url_path="" hace que Flask sirva index.html en la raiz.
app = Flask(__name__, static_url_path="")

MODOS = ("hh", "minimax", "ml")

# Estado en memoria: id de partida -> {"modelo": GameModel, "modo": str}.
PARTIDAS = {}
_IDS = itertools.count(1)

# El agente de Minimax es stateless entre llamadas (el contador de nodos
# se reinicia en cada mejor_jugada), asi que se comparte entre partidas.
AGENTE_MINIMAX = MinimaxAgent()

# El agente de ML se entrena la primera vez que se necesita: tarda unos
# segundos porque recorre todo el dataset.
_AGENTE_ML = {}


def obtener_agente_ml():
    """Entrena y guarda el agente de ML la primera vez que se pide."""
    if "agente" not in _AGENTE_ML:
        ruta = os.path.join(RAIZ, "data", "partidas.csv")
        tabla = cargar_dataset(ruta)
        arbol, precision = entrenar_arbol(tabla)
        _AGENTE_ML["agente"] = AgenteArbol(arbol)
        _AGENTE_ML["precision"] = precision
    return _AGENTE_ML["agente"]


def estado_a_json(identificador, partida):
    """Convierte el modelo en el diccionario de estado que viaja al cliente."""
    modelo = partida["modelo"]
    ganador = None
    linea = None
    for jugador in (GameModel.JUGADOR_X, GameModel.JUGADOR_O):
        if modelo.hay_ganador(jugador):
            ganador = jugador
            linea = modelo.linea_ganadora(jugador)
    return {
        "id": identificador,
        "modo": partida["modo"],
        "tablero": modelo.tablero,
        "turno": modelo.jugador_actual,
        "terminado": modelo.juego_terminado(),
        "ganador": ganador,
        "linea": [[f, c] for f, c in linea] if linea else None,
    }


def jugar_ia(partida):
    """Ejecuta el turno de la IA y devuelve la informacion del movimiento.

    Mide nodos y tiempo para las metricas, igual que el juego de pygame.
    En el modo ML tambien devuelve las reglas (preguntas del arbol) para
    poder explicar la decision en la interfaz.
    """
    modelo = partida["modelo"]
    if partida["modo"] == "minimax":
        agente = AGENTE_MINIMAX
    else:
        agente = obtener_agente_ml()
    reglas = None
    if partida["modo"] == "ml":
        _, reglas = agente.explicar_jugada(modelo.tablero)
    inicio = time.perf_counter()
    fila, columna = agente.mejor_jugada(modelo)
    milisegundos = (time.perf_counter() - inicio) * 1000
    if not modelo.es_movimiento_valido(fila, columna):
        # El arbol de ML puede proponer una casilla ya ocupada en estados
        # que vio pocas veces; se juega la primera libre como respaldo.
        fila, columna = modelo.obtener_movimientos_disponibles()[0]
    modelo.hacer_movimiento(fila, columna)
    info = {
        "jugada": {"fila": fila, "columna": columna},
        "nodos": agente.nodos_evaluados,
        "milisegundos": round(milisegundos, 2),
    }
    if reglas is not None:
        info["reglas"] = reglas
    return info


def error(mensaje, codigo):
    """Respuesta de error en JSON con su codigo HTTP."""
    return jsonify({"error": mensaje}), codigo


@app.route("/")
def pagina_principal():
    """Sirve la pagina del juego (index.html con el tablero y el arbol)."""
    return app.send_static_file("index.html")


@app.route("/api/partidas", methods=["POST"])
def crear_partida():
    """Crea una partida nueva en el modo pedido y devuelve su estado."""
    datos = request.get_json(silent=True) or {}
    modo = datos.get("modo", "hh")
    if modo not in MODOS:
        return error("modo invalido: usa hh, minimax o ml", 400)
    identificador = next(_IDS)
    PARTIDAS[identificador] = {"modelo": GameModel(), "modo": modo}
    return jsonify(estado_a_json(identificador, PARTIDAS[identificador]))


def buscar_partida(identificador):
    """Devuelve la partida o una respuesta de error lista para retornar."""
    partida = PARTIDAS.get(identificador)
    if partida is None:
        return None, error("partida no encontrada", 404)
    return partida, None


@app.route("/api/partidas/<int:identificador>", methods=["GET"])
def consultar_partida(identificador):
    """Devuelve el estado actual de la partida."""
    partida, fallo = buscar_partida(identificador)
    if fallo:
        return fallo
    return jsonify(estado_a_json(identificador, partida))


@app.route("/api/partidas/<int:identificador>/movimientos",
           methods=["POST"])
def hacer_movimiento(identificador):
    """Aplica la jugada del cliente y, si toca, la respuesta de la IA.

    El cuerpo del pedido es {"fila": 0-2, "columna": 0-2}. En los modos
    con IA el humano es siempre X: si llega un movimiento cuando no es
    turno de X, se rechaza.
    """
    partida, fallo = buscar_partida(identificador)
    if fallo:
        return fallo
    modelo = partida["modelo"]
    if modelo.juego_terminado():
        return error("la partida ya termino", 400)
    datos = request.get_json(silent=True) or {}
    try:
        fila, columna = int(datos["fila"]), int(datos["columna"])
    except (KeyError, TypeError, ValueError):
        return error("envia fila y columna como numeros 0-2", 400)
    if partida["modo"] != "hh" and \
            modelo.jugador_actual != GameModel.JUGADOR_X:
        return error("no es turno del humano", 400)
    if not modelo.hacer_movimiento(fila, columna):
        return error("casilla ocupada o fuera del tablero", 400)
    respuesta = {"estado": estado_a_json(identificador, partida)}
    if partida["modo"] != "hh" and not modelo.juego_terminado():
        respuesta["ia"] = jugar_ia(partida)
        respuesta["estado"] = estado_a_json(identificador, partida)
    return jsonify(respuesta)


def arbol_a_json(arbol):
    """Convierte el DecisionTreeClassifier de sklearn en JSON anidado.

    Cada nodo tiene nombre (la pregunta o la jugada de la hoja), cantidad
    de muestras de entrenamiento que pasaron por ahi y, si no es hoja,
    sus dos hijos. La pagina web lo dibuja con D3.
    """
    estructura = arbol.tree_

    def nodo(indice):
        muestras = int(estructura.n_node_samples[indice])
        hijo_izq = estructura.children_left[indice]
        hijo_der = estructura.children_right[indice]
        if hijo_izq == hijo_der:
            valores = estructura.value[indice].ravel()
            jugada = int(arbol.classes_[int(valores.argmax())])
            return {"nombre": "jugada {}".format(jugada), "hoja": True,
                    "jugada": jugada, "muestras": muestras}
        return {
            "nombre": "c{} <= {:.1f}".format(
                int(estructura.feature[indice]),
                estructura.threshold[indice]),
            "hoja": False, "muestras": muestras,
            "children": [nodo(hijo_izq), nodo(hijo_der)],
        }

    return nodo(0)


@app.route("/api/arbol", methods=["GET"])
def consultar_arbol():
    """Devuelve el arbol de decision entrenado y su precision de prueba."""
    agente = obtener_agente_ml()
    return jsonify({
        "precision": _AGENTE_ML["precision"],
        "raiz": arbol_a_json(agente.arbol),
    })


@app.route("/api/arbol/imagen")
def imagen_arbol():
    """Sirve la imagen del arbol exportada con sklearn (data/arbol.png)."""
    return send_from_directory(os.path.join(RAIZ, "data"), "arbol.png")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True)
