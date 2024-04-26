import pygame

from pytune import Game, GameBoard
from pytune import WINDOW_HEIGHT, WINDOW_WIDTH


def main():
    pygame.init()

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # Initialize pygame display to handle events
    pygame.display.set_caption("PyTune 0.0.0dev")

    folder_path = "./assets/domki2024"  # Change this to your folder path
    game = Game(path=folder_path, random_order=True)
    board = GameBoard(window, game.players)

    game.show_intro(board)
    game.start_game(board)

if __name__ == "__main__":
    main()
