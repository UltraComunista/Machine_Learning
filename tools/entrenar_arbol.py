"""Entrena el arbol de decision y genera su visualizacion (Semana 3, Dia 3).

Carga el dataset del Dia 2, entrena el arbol de decision implementado
en model/arbol_decision.py (sin scikit-learn), mide que porcentaje de
jugadas acierta sobre datos que no vio al entrenar y guarda dos vistas
del arbol aprendido:

- data/arbol.txt: las reglas en texto (if c4 <= ... else ...),
  generadas por ArbolDecision.a_texto.
- data/arbol.png: dibujo propio del arbol con matplotlib, recortado a
  los primeros niveles para que se lea; la estructura completa esta
  en el .txt.

Uso:
    python3.13 tools/entrenar_arbol.py
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from model.ml_agent import (  # noqa: E402
    NOMBRES_CARACTERISTICAS,
    cargar_dataset,
    entrenar_arbol,
)

RUTA_CSV = os.path.join(RAIZ, "data", "partidas.csv")
RUTA_TEXTO = os.path.join(RAIZ, "data", "arbol.txt")
RUTA_FIGURA = os.path.join(RAIZ, "data", "arbol.png")

# Niveles del arbol que se dibujan en la figura. El arbol completo
# tiene muchas ramas y en una imagen seria ilegible.
PROFUNDIDAD_DIBUJO = 5


def dibujar_arbol(arbol, ruta, profundidad_max):
    """Dibuja el arbol con matplotlib, nodo por nodo.

    Primero se asigna a cada nodo una posicion: las hojas visibles
    quedan en columnas sucesivas y cada rama interna se centra entre
    sus hijos. Despues se dibujan las lineas de padre a hijo y una
    caja de texto por nodo: la pregunta (o la jugada en las hojas) y
    cuantas filas de entrenamiento pasaron por ahi.
    """
    posiciones = {}
    contador = [0]

    def asignar(nodo, profundidad):
        corte = nodo.es_hoja or profundidad >= profundidad_max
        if corte:
            posiciones[id(nodo)] = (float(contador[0]), -profundidad)
            contador[0] += 1
            return
        asignar(nodo.izquierda, profundidad + 1)
        asignar(nodo.derecha, profundidad + 1)
        x_izq, _ = posiciones[id(nodo.izquierda)]
        x_der, _ = posiciones[id(nodo.derecha)]
        posiciones[id(nodo)] = ((x_izq + x_der) / 2.0, -profundidad)

    asignar(arbol.raiz, 0)

    ancho = max(12, contador[0] * 0.9)
    figura, eje = plt.subplots(figsize=(ancho, 12))
    eje.axis("off")

    def dibujar(nodo):
        x, y = posiciones[id(nodo)]
        # Si el nodo se corto por la profundidad maxima de dibujo, sus
        # hijos no tienen posicion asignada y se dibuja como hoja.
        hijos = []
        if not nodo.es_hoja:
            for hijo in (nodo.izquierda, nodo.derecha):
                if id(hijo) in posiciones:
                    hijos.append(hijo)
        for hijo in hijos:
            xh, yh = posiciones[id(hijo)]
            eje.plot([x, xh], [y, yh], color="#8a93ad", linewidth=1,
                     zorder=1)
        if nodo.es_hoja:
            texto = "juega c{}\n({} filas)".format(
                nodo.prediccion, nodo.num_muestras)
            color = "#dfe6ff"
        else:
            texto = "{} <= {:.1f}\n({} filas)".format(
                NOMBRES_CARACTERISTICAS[nodo.caracteristica],
                nodo.umbral, nodo.num_muestras)
            color = "#ffe9c7"
        eje.text(x, y, texto, ha="center", va="center", fontsize=8,
                 zorder=2,
                 bbox=dict(boxstyle="round,pad=0.35", fc=color,
                           ec="#5a6280", linewidth=0.8))
        for hijo in hijos:
            dibujar(hijo)

    dibujar(arbol.raiz)
    eje.set_xlim(-1, contador[0])
    eje.set_ylim(-profundidad_max - 1, 1)
    figura.savefig(ruta, bbox_inches="tight", dpi=110)
    plt.close(figura)


def main():
    tabla = cargar_dataset(RUTA_CSV)
    print("Filas del dataset: {}".format(len(tabla)))

    arbol, precision = entrenar_arbol(tabla)
    print("Precision sobre el 20% de prueba: {:.1%}".format(precision))
    print("Profundidad del arbol: {}".format(arbol.profundidad()))
    print("Nodos del arbol: {}".format(arbol.contar_nodos()))

    with open(RUTA_TEXTO, "w") as archivo:
        archivo.write(arbol.a_texto(NOMBRES_CARACTERISTICAS))
    print("Reglas del arbol guardadas en {}".format(RUTA_TEXTO))

    dibujar_arbol(arbol, RUTA_FIGURA, PROFUNDIDAD_DIBUJO)
    print("Figura del arbol guardada en {}".format(RUTA_FIGURA))


if __name__ == "__main__":
    main()
