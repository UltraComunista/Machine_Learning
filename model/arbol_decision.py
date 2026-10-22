"""Arbol de decision implementado desde cero, sin librerias de ML.

El proyecto no usa scikit-learn: esta es nuestra propia implementacion
del algoritmo de arbol de decision (variante CART con criterio Gini).

Como se construye el arbol (lo que hace ArbolDecision.ajustar):

1. En cada nodo se prueban todas las preguntas posibles: cada
   caracteristica (c0..c8) con cada umbral (0.5 y 1.5, porque los
   valores solo pueden ser 0, 1 o 2).
2. Para cada pregunta se parte el grupo de filas en dos y se mide que
   tan "mezcladas" quedan las etiquetas (jugadas) de cada lado con la
   impureza de Gini: 0 si todas las filas coinciden en la jugada,
   alta si estan repartidas.
3. Se elige la pregunta que mas baja la mezcla (mayor ganancia) y se
   repite lo mismo en cada hijo, recursivamente.
4. Se detiene en un nodo cuando sus filas ya coinciden en la jugada
   (es puro), cuando ninguna pregunta mejora, o cuando queda una sola
   fila. Cada hoja guarda la jugada mayoritaria de sus filas.

Predecir es bajar por el arbol respondiendo cada pregunta con los
valores de la fila, hasta llegar a una hoja.
"""

# Umbrales candidatos: los valores de las casillas solo pueden ser
# 0 (vacia), 1 (X) u 2 (O), asi que toda pregunta util es
# "c_i <= 0.5" (esta vacia) o "c_i <= 1.5" (no es O).
UMBRALES = (0.5, 1.5)


def gini(etiquetas):
    """Impureza de Gini de un grupo de etiquetas.

    1 - suma de p^2 por clase: vale 0 si todas las etiquetas son
    iguales (grupo puro) y se acerca a 1 - 1/k si hay k clases
    repartidas parejo. Es la medida de "mezcla" que el arbol intenta
    bajar en cada particion.
    """
    total = len(etiquetas)
    if total == 0:
        return 0.0
    conteos = {}
    for etiqueta in etiquetas:
        conteos[etiqueta] = conteos.get(etiqueta, 0) + 1
    return 1.0 - sum((c / total) ** 2 for c in conteos.values())


def _mayoritaria(etiquetas):
    """Devuelve la etiqueta mas frecuente del grupo (la jugada que
    Minimax hizo mas veces en ese estado)."""
    conteos = {}
    for etiqueta in etiquetas:
        conteos[etiqueta] = conteos.get(etiqueta, 0) + 1
    return max(conteos, key=conteos.get)


class NodoArbol:
    """Un nodo del arbol: o una pregunta (rama interna) o una hoja.

    En las ramas internas caracteristica es el indice de la casilla
    que se pregunta (0-8, es decir c0..c8) y umbral es 0.5 o 1.5.
    En las hojas prediccion es la jugada que el nodo devuelve. Todas
    las hojas Y ramas guardan su prediccion mayoritaria: si una fila
    llega a una rama interna por un estado no visto en entrenamiento,
    igual se puede responder con lo mas frecuente de ahi para abajo.
    """

    __slots__ = ("caracteristica", "umbral", "izquierda", "derecha",
                 "prediccion", "num_muestras")

    def __init__(self):
        self.caracteristica = None
        self.umbral = None
        self.izquierda = None
        self.derecha = None
        self.prediccion = None
        self.num_muestras = 0

    @property
    def es_hoja(self):
        return self.izquierda is None and self.derecha is None


class ArbolDecision:
    """Arbol de decision binario para clasificar filas de numeros.

    Se entrena con ajustar(filas, etiquetas) y despues clasifica con
    predecir(fila) o predecir_con_ruta(fila), que ademas devuelve las
    preguntas respondidas para poder explicar la decision.
    """

    def __init__(self):
        self.raiz = None

    # ---------------- entrenamiento ----------------

    def ajustar(self, filas, etiquetas):
        """Construye el arbol a partir de las filas de entrenamiento.

        Cada fila es una lista de 9 numeros (el tablero codificado) y
        cada etiqueta es la jugada (0-8) que Minimax hizo en ese
        estado. Devuelve self para poder escribir
        ArbolDecision().ajustar(filas, etiquetas).
        """
        self.raiz = self._construir(filas, etiquetas)
        return self

    def _construir(self, filas, etiquetas):
        nodo = NodoArbol()
        nodo.num_muestras = len(filas)
        nodo.prediccion = _mayoritaria(etiquetas)

        # Casos base: grupo puro (todas las jugadas iguales) o con una
        # sola fila. No tiene sentido seguir preguntando.
        if len(set(etiquetas)) == 1 or len(filas) < 2:
            return nodo

        division = self._mejor_particion(filas, etiquetas)
        if division is None:
            # Ninguna pregunta mejora la mezcla: hoja con la jugada
            # mayoritaria (estados donde Minimax no fue consistente).
            return nodo

        caracteristica, umbral = division
        nodo.caracteristica = caracteristica
        nodo.umbral = umbral
        izquierda = ([], [])
        derecha = ([], [])
        for fila, etiqueta in zip(filas, etiquetas):
            destino = izquierda if fila[caracteristica] <= umbral \
                else derecha
            destino[0].append(fila)
            destino[1].append(etiqueta)
        nodo.izquierda = self._construir(*izquierda)
        nodo.derecha = self._construir(*derecha)
        return nodo

    def _mejor_particion(self, filas, etiquetas):
        """Busca la pregunta (caracteristica, umbral) que mas baja la
        impureza de Gini. Devuelve None si ninguna mejora.

        Se recorren todas las caracteristicas y los dos umbrales
        posibles; en empates gana la primera en orden de lectura, lo
        que hace el arbol determinista.
        """
        base = gini(etiquetas)
        total = len(filas)
        mejor = None
        for caracteristica in range(len(filas[0])):
            for umbral in UMBRALES:
                izquierda = ([], [])
                derecha = ([], [])
                for fila, etiqueta in zip(filas, etiquetas):
                    destino = izquierda \
                        if fila[caracteristica] <= umbral else derecha
                    destino[0].append(fila)
                    destino[1].append(etiqueta)
                if not izquierda[0] or not derecha[0]:
                    continue
                mezcla = (len(izquierda[1]) * gini(izquierda[1])
                          + len(derecha[1]) * gini(derecha[1])) / total
                ganancia = base - mezcla
                if ganancia > 1e-12 and (
                        mejor is None or ganancia > mejor[0]):
                    mejor = (ganancia, caracteristica, umbral)
        if mejor is None:
            return None
        return mejor[1], mejor[2]

    # ---------------- prediccion ----------------

    def predecir(self, fila):
        """Devuelve la jugada (clase) que el arbol asigna a una fila."""
        nodo = self.raiz
        while not nodo.es_hoja:
            if fila[nodo.caracteristica] <= nodo.umbral:
                nodo = nodo.izquierda
            else:
                nodo = nodo.derecha
        return nodo.prediccion

    def predecir_con_ruta(self, fila):
        """Devuelve (prediccion, ruta): la jugada y las preguntas que
        se respondieron para llegar a ella, como tuplas
        (caracteristica, umbral, "si"/"no"). Es lo que usa el agente
        para contar nodos y para explicar la decision."""
        nodo = self.raiz
        ruta = []
        while not nodo.es_hoja:
            if fila[nodo.caracteristica] <= nodo.umbral:
                ruta.append((nodo.caracteristica, nodo.umbral, "si"))
                nodo = nodo.izquierda
            else:
                ruta.append((nodo.caracteristica, nodo.umbral, "no"))
                nodo = nodo.derecha
        return nodo.prediccion, ruta

    # ---------------- informacion y exportacion ----------------

    def contar_nodos(self):
        """Cantidad total de nodos (ramas y hojas) del arbol."""
        return self._contar(self.raiz)

    def _contar(self, nodo):
        if nodo is None:
            return 0
        return 1 + self._contar(nodo.izquierda) + self._contar(nodo.derecha)

    def profundidad(self):
        """Profundidad maxima: cantidad de preguntas del camino mas
        largo de la raiz a una hoja."""
        return self._profundidad(self.raiz)

    def _profundidad(self, nodo):
        if nodo is None or nodo.es_hoja:
            return 0
        return 1 + max(self._profundidad(nodo.izquierda),
                       self._profundidad(nodo.derecha))

    def a_texto(self, nombres):
        """Exporta el arbol como texto: cada nivel con sangria, las
        ramas como preguntas y las hojas como 'class: N'. Permite leer
        las reglas que aprendio el modelo sin ninguna herramienta
        extra (formato tipo sklearn.tree.export_text, pero generado
        por nuestro propio codigo)."""
        lineas = []

        def recorrer(nodo, prefijo, ultimo):
            if nodo.es_hoja:
                lineas.append("{}|--- class: {}".format(
                    prefijo, nodo.prediccion))
                return
            lineas.append("{}|--- {} <= {:.2f}".format(
                prefijo, nombres[nodo.caracteristica],
                nodo.umbral))
            extension = "    " if ultimo else "|   "
            recorrer(nodo.izquierda, prefijo + extension, False)
            recorrer(nodo.derecha, prefijo + extension, True)

        recorrer(self.raiz, "", True)
        return "\n".join(lineas) + "\n"
