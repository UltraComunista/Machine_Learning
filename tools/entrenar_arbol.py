"""Entrena el arbol de decision y genera su visualizacion (Semana 3, Dia 3).

Carga el dataset del Dia 2, entrena un DecisionTreeClassifier de
scikit-learn, mide que porcentaje de jugadas acierta sobre datos que
no vio al entrenar y guarda dos vistas del arbol aprendido:

- data/arbol.txt: las reglas en texto (if c4 <= ... else ...).
- data/arbol.png: dibujo del arbol, recortado a los primeros niveles
  para que se lea; la estructura completa esta en el .txt.

Uso:
    python3.13 tools/entrenar_arbol.py
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from sklearn.tree import export_text, plot_tree  # noqa: E402

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


def main():
    tabla = cargar_dataset(RUTA_CSV)
    print("Filas del dataset: {}".format(len(tabla)))

    arbol, precision = entrenar_arbol(tabla)
    print("Precision sobre el 20% de prueba: {:.1%}".format(precision))
    print("Profundidad del arbol: {}".format(arbol.get_depth()))
    print("Nodos del arbol: {}".format(arbol.tree_.node_count))

    texto = export_text(arbol, feature_names=NOMBRES_CARACTERISTICAS)
    with open(RUTA_TEXTO, "w") as archivo:
        archivo.write(texto)
    print("Reglas del arbol guardadas en {}".format(RUTA_TEXTO))

    nombres_clases = [str(i) for i in range(9)]
    figura, eje = plt.subplots(figsize=(30, 14))
    plot_tree(arbol, feature_names=NOMBRES_CARACTERISTICAS,
              class_names=nombres_clases, filled=True,
              max_depth=PROFUNDIDAD_DIBUJO, fontsize=9, ax=eje)
    figura.savefig(RUTA_FIGURA, bbox_inches="tight")
    print("Figura del arbol guardada en {}".format(RUTA_FIGURA))


if __name__ == "__main__":
    main()
