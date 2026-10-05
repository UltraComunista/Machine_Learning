"""Estado del tablero, reglas del juego y validación de victorias/empates."""


class GameModel:
    """Representa el estado de una partida de Tres en Raya.

    El tablero es una matriz de 3x3 donde cada casilla puede estar
    vacia o ocupada por la ficha de un jugador ('X' u 'O').
    """

    VACIO = " "
    JUGADOR_X = "X"
    JUGADOR_O = "O"

    def __init__(self):
        self.tablero = [[self.VACIO for _ in range(3)] for _ in range(3)]
        self.jugador_actual = self.JUGADOR_X

    def reiniciar(self):
        """Devuelve el tablero al estado inicial de una partida nueva."""
        self.tablero = [[self.VACIO for _ in range(3)] for _ in range(3)]
        self.jugador_actual = self.JUGADOR_X

    def es_movimiento_valido(self, fila, columna):
        """Verifica que la casilla exista y este libre."""
        if not (0 <= fila < 3 and 0 <= columna < 3):
            return False
        return self.tablero[fila][columna] == self.VACIO

    def hacer_movimiento(self, fila, columna):
        """Coloca la ficha del jugador actual si el movimiento es valido.

        Devuelve True si se pudo jugar y cambia el turno al otro jugador.
        """
        if not self.es_movimiento_valido(fila, columna):
            return False
        self.tablero[fila][columna] = self.jugador_actual
        self.jugador_actual = self._oponente(self.jugador_actual)
        return True

    def deshacer_movimiento(self, fila, columna):
        """Libera una casilla y devuelve el turno al jugador anterior.

        Se usa en el backtracking de Minimax para restaurar el estado
        del tablero despues de explorar una rama del arbol de jugadas.
        """
        self.tablero[fila][columna] = self.VACIO
        self.jugador_actual = self._oponente(self.jugador_actual)

    def obtener_movimientos_disponibles(self):
        """Devuelve la lista de casillas vacias como tuplas (fila, columna)."""
        movimientos = []
        for fila in range(3):
            for columna in range(3):
                if self.tablero[fila][columna] == self.VACIO:
                    movimientos.append((fila, columna))
        return movimientos

    def linea_ganadora(self, jugador):
        """Devuelve las tres casillas que forman la linea ganadora del
        jugador, o None si no hay ninguna."""
        lineas = []

        # Filas y columnas
        for i in range(3):
            lineas.append([(i, c) for c in range(3)])
            lineas.append([(f, i) for f in range(3)])

        # Diagonales
        lineas.append([(i, i) for i in range(3)])
        lineas.append([(i, 2 - i) for i in range(3)])

        for linea in lineas:
            if all(self.tablero[f][c] == jugador for f, c in linea):
                return linea
        return None

    def hay_ganador(self, jugador):
        """Verifica si el jugador tiene tres fichas en linea."""
        return self.linea_ganadora(jugador) is not None

    def tablero_lleno(self):
        """Verifica si ya no quedan casillas vacias."""
        return all(self.tablero[f][c] != self.VACIO
                   for f in range(3) for c in range(3))

    def hay_empate(self):
        """Hay empate cuando el tablero esta lleno y nadie gano."""
        return self.tablero_lleno() and not self.hay_ganador(self.JUGADOR_X) \
            and not self.hay_ganador(self.JUGADOR_O)

    def juego_terminado(self):
        """La partida termina si alguien gano o si hay empate."""
        return self.hay_ganador(self.JUGADOR_X) \
            or self.hay_ganador(self.JUGADOR_O) or self.hay_empate()

    @staticmethod
    def _oponente(jugador):
        """Devuelve el jugador contrario al dado."""
        return GameModel.JUGADOR_O if jugador == GameModel.JUGADOR_X \
            else GameModel.JUGADOR_X
