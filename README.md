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
3. **Humano vs. IA Machine Learning**: un `DecisionTreeClassifier`
   entrenado con miles de partidas simuladas predice la mejor jugada sin
   explorar el árbol en tiempo real.

## Arquitectura (patrón MVC)

| Componente | Archivo | Responsabilidad |
|---|---|---|
| Modelo | `model/game_model.py` | Estado del tablero, reglas, validación de victorias y empates |
| Modelo | `model/minimax_agent.py` | Algoritmo Minimax con backtracking |
| Modelo | `model/ml_agent.py` | Generación del dataset y entrenamiento del árbol de decisión |
| Vista | `view/gui_view.py` | Interfaz gráfica: tablero, menús y métricas |
| Controlador | `controller/game_controller.py` | Sincroniza la interacción del usuario con el modelo y la vista |

El modelo no depende de la interfaz y la vista no contiene lógica de
juego: toda la comunicación pasa por el controlador.

## Tecnologías

- Python 3
- Tkinter (interfaz gráfica)
- Scikit-Learn (árbol de decisión)
- Pandas (manejo del dataset)

## Plan de trabajo

**Semana 1 — Lógica del juego, MVC e interfaz gráfica**
- Día 1: estructura del repositorio y carpetas MVC
- Día 2: implementación del tablero y las reglas (`game_model.py`)
- Día 3: interfaz gráfica (`gui_view.py`)
- Día 4: controlador y eventos (`game_controller.py`)
- Día 5: pruebas del modo Humano vs. Humano

**Semana 2 — Árboles, backtracking y Minimax**
- Día 1: espacios de estados y mecanismo de backtracking
- Día 2: función de evaluación heurística
- Día 3: algoritmo Minimax recursivo con contador de nodos
- Día 4: integración del agente Minimax al controlador
- Día 5: métricas en la interfaz (nodos explorados y tiempo de respuesta)

**Semana 3 — Dataset y Machine Learning**
- Día 1: simulación de partidas para generar el dataset
- Día 2: limpieza y estructuración del dataset (CSV)
- Día 3: entrenamiento y visualización del árbol de decisión
- Día 4: integración del agente ML a la interfaz
- Día 5: comparativa final (velocidad y precisión) y presentación

## Instalación

```bash
pip install -r requirements.txt
```
