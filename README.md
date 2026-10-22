# Tres en Raya: de Minimax a Machine Learning

Proyecto educativo de tres semanas que implementa el juego de Tres en Raya
(Tic-Tac-Toe) con tres modos de juego: Humano vs. Humano, Humano vs. IA
Minimax y Humano vs. IA entrenada con Machine Learning.

La idea central del proyecto es mostrar la transición entre la IA simbólica
tradicional, basada en búsqueda exhaustiva en el árbol de jugadas
(backtracking + Minimax), y el Machine Learning supervisado, donde un
árbol de decisión aprende a imitar las decisiones óptimas a partir de un
dataset generado con las propias simulaciones del juego.

## Modos de juego

1. **Humano vs. Humano**: dos jugadores en la misma interfaz.
2. **Humano vs. IA Minimax**: la IA explora recursivamente el árbol de
   jugadas posibles y elige el movimiento óptimo.
3. **Humano vs. IA Machine Learning**: un árbol de decisión
   implementado desde cero (`model/arbol_decision.py`) y entrenado con
   miles de partidas simuladas predice la mejor jugada sin explorar
   el árbol en tiempo real.

## Arquitectura (patrón MVC)

| Componente | Archivo | Responsabilidad |
|---|---|---|
| Modelo | `model/game_model.py` | Estado del tablero, reglas, validación de victorias y empates |
| Modelo | `model/minimax_agent.py` | Algoritmo Minimax con backtracking |
| Modelo | `model/arbol_decision.py` | Árbol de decisión propio: Gini, particiones y predicción |
| Modelo | `model/ml_agent.py` | Generación del dataset y entrenamiento del árbol de decisión |
| Vista | `view/gui_view.py` | Interfaz gráfica: tablero, menús y métricas |
| Controlador | `controller/game_controller.py` | Sincroniza la interacción del usuario con el modelo y la vista |

El modelo no depende de la interfaz y la vista no contiene lógica de
juego: toda la comunicación pasa por el controlador.

## Tecnologías

- Python 3 (incluidos los módulos estándar `csv` y `random`)
- Pygame (interfaz gráfica)
- Matplotlib (dibujo del árbol de decisión en `tools/entrenar_arbol.py`)

El árbol de decisión **no** usa scikit-learn: la selección de
preguntas con el criterio de Gini, la separación entrenamiento/prueba
y la predicción son implementación propia en `model/arbol_decision.py`.

Fuente pixel art: Press Start 2P de Codeman38, licencia SIL Open Font
License 1.1.

## Plan de trabajo

**Semana 1 — Lógica del juego, MVC e interfaz gráfica**
- Día 1: estructura del repositorio y carpetas MVC ✔
- Día 2: implementación del tablero y las reglas (`game_model.py`) ✔
- Día 3: interfaz gráfica (`gui_view.py`) ✔
- Día 4: controlador y eventos (`game_controller.py`) ✔
- Día 5: pruebas del modo Humano vs. Humano ✔

**Semana 2 — Árboles, backtracking y Minimax**
- Día 1: espacios de estados y mecanismo de backtracking ✔
- Día 2: función de evaluación heurística ✔
- Día 3: algoritmo Minimax recursivo con contador de nodos ✔
- Día 4: integración del agente Minimax al controlador ✔
- Día 5: métricas en la interfaz (nodos explorados y tiempo de respuesta) ✔

**Semana 3 — Dataset y Machine Learning**
- Día 1: simulación de partidas para generar el dataset ✔
- Día 2: limpieza y estructuración del dataset (CSV) ✔
- Día 3: entrenamiento y visualización del árbol de decisión ✔
- Día 4: integración del agente ML a la interfaz ✔
- Día 5: comparativa final (velocidad y precisión) y presentación ✔

## Comparativa final: Minimax vs. Machine Learning

Medición real sobre 50 posiciones de juego generadas al azar
(`python3.13 tools/comparar_agentes.py`, semilla 7):

| Métrica | Minimax | Árbol de decisión |
|---|---|---|
| Jugadas idénticas | 45/50 (90%) | 45/50 (90%) |
| Tiempo por jugada | ~284 ms | ~1.2 ms |
| Nodos revisados por jugada | ~42,000 | ~6.5 |

El árbol de decisión es unas **230 veces más rápido** y revisa miles
de veces menos nodos, a cambio de no coincidir exactamente en el 10%
de las posiciones. Ese 10% se da casi siempre cuando varias jugadas
son igual de buenas (empatan en puntaje) y cada agente elige una
distinta: la calidad de juego es equivalente, aunque la casilla no
sea la misma.

Herramientas de análisis del repositorio:

- `tools/sesion_debug.py` — **sesión de debugging interactiva**: juegas
  contra Minimax desde una posición con pocas casillas libres y su
  razonamiento se imprime **paso a paso con pausas** (parámetro
  `demora`), viendo el backtracking en tiempo real; al final compara
  con las reglas que usaría el árbol de ML para el mismo tablero.
- `tools/comparar_agentes.py` — imprime la **traza de backtracking**
  de Minimax en una posición pequeña, las **reglas que el árbol se
  pregunta** para decidir y la comparativa de tiempos y nodos.
- `tools/entrenar_arbol.py` — entrena el árbol y exporta su
  estructura completa en `data/arbol.txt` (reglas en texto, generadas
  por `ArbolDecision.a_texto`) y `data/arbol.png`.
- `MinimaxAgent.mejor_jugada(modelo, traza=True, demora=0.5)` —
  activa la traza de llamadas recursivas con pausa entre pasos.

## ¿Se le puede ganar a la IA?

- **Minimax: no.** Juega perfecto; lo mejor que se puede lograr
  contra ella es un empate.
- **Machine Learning: en la práctica, tampoco.** La IA de ML solo
  juega con O (segunda ficha), y el mejor resultado posible con O
  contra un X perfecto es el empate. En la prueba del proyecto,
  Minimax jugando X perfecto no logró ganarle ni una de las 65
  partidas: todas terminaron en empate. El 10% de jugadas distintas
  que observamos en la comparativa eran casi siempre entre movidas
  igual de buenas, no errores que se puedan aprovechar.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar el juego

```bash
python3 main.py
```

## Ejecutar las pruebas

```bash
python3 -m unittest discover tests -v
```
