"""Punto de entrada de la aplicación."""

from model.game_model import GameModel
from view.gui_view import GameView
from controller.game_controller import GameController


def main():
    modelo = GameModel()
    vista = GameView()
    controlador = GameController(modelo, vista)
    # La vista usa al controlador para avisar cuando el usuario hace clic
    vista.controlador = controlador
    controlador.iniciar()


if __name__ == "__main__":
    main()
