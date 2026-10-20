"""Genera el dataset de jugadas de la IA y lo guarda en CSV (Semana 3, Dia 2).

Corre las simulaciones del Dia 1 a gran escala, valida que las filas
esten bien formadas y escribe el resultado en data/partidas.csv para
entrenar el arbol de decision del Dia 3.

El dataset se sube al repositorio porque es parte de la entrega del
proyecto, pero se puede regenerar en cualquier momento corriendo este
script (unos 13 minutos para 2000 partidas).

Uso:
    python3.13 tools/generar_dataset.py
"""

import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from model.ml_agent import (  # noqa: E402
    GeneradorDatos,
    construir_dataset,
    guardar_dataset,
    validar_dataset,
)

PARTIDAS = 2000
SEMILLA = 42
RUTA_CSV = os.path.join(RAIZ, "data", "partidas.csv")


def main():
    print("Simulando {} partidas (Minimax vs. aleatorio)...".format(
        PARTIDAS))
    inicio = time.perf_counter()

    generador = GeneradorDatos(semilla=SEMILLA)
    datos, resultados = generador.generar(PARTIDAS)

    duracion = time.perf_counter() - inicio
    print("Listo en {:.1f} minutos.".format(duracion / 60))
    print("Resultados de las partidas: {}".format(resultados))
    print("Filas de datos: {}".format(len(datos)))

    tabla = construir_dataset(datos)
    problemas = validar_dataset(tabla)
    if problemas:
        for problema in problemas:
            print("ERROR: {}".format(problema))
        sys.exit(1)

    guardar_dataset(tabla, RUTA_CSV)
    print("Dataset guardado en {}".format(RUTA_CSV))
    print("Distribucion de la etiqueta 'jugada':")
    print(tabla["jugada"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
