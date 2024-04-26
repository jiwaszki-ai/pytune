from enum import Enum

import pygame

from .player import Host, HostState, Player, PlayerState

# Window dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 500

# Number of rectangles
NUM_RECTANGLES = 5

# Calculate the height of each rectangle
RECTANGLE_WIDTH = WINDOW_WIDTH // NUM_RECTANGLES


class Colors(Enum):
    PURPLE = 0
    ORANGE = 1
    GREEN = 2
    BLUE = 3
    RED = 4
    BLACK = 5


class ColorModes(Enum):
    INACTIVE = 0
    DARK = 1
    LIGHT = 2


CARD_PALETTE = {
    Colors.PURPLE: {
        ColorModes.DARK: (128, 64, 255),
        ColorModes.LIGHT: (204, 179, 255),
        ColorModes.INACTIVE: (230, 230, 230),
    },
    Colors.ORANGE: {
        ColorModes.DARK: (255, 128, 64),
        ColorModes.LIGHT: (255, 224, 179),
        ColorModes.INACTIVE: (230, 230, 230),
    },
    Colors.GREEN: {
        ColorModes.DARK: (64, 255, 64),
        ColorModes.LIGHT: (179, 255, 179),
        ColorModes.INACTIVE: (230, 230, 230),
    },
    Colors.BLUE: {
        ColorModes.DARK: (64, 128, 255),
        ColorModes.LIGHT: (179, 217, 255),
        ColorModes.INACTIVE: (230, 230, 230),
    },
    Colors.RED: {
        ColorModes.DARK: (255, 64, 64),
        ColorModes.LIGHT: (255, 204, 204),
        ColorModes.INACTIVE: (230, 230, 230),
    },
}

# Font setup
pygame.font.init()  # Initialize the font module even if game is not initialized itself
font_big = pygame.font.Font(None, 36)
font_medium = pygame.font.Font(None, 24)
font_small = pygame.font.Font(None, 16)


FONT_PALETTE = {
    Colors.BLACK: {
        ColorModes.DARK: (0, 0, 0),
        ColorModes.LIGHT: (64, 64, 64),
        ColorModes.INACTIVE: (128, 128, 128),
    }
}


class BoardCard:
    def __init__(self, index, color, name="Inactive", device="-", player=None):
        self.index = index
        self.color = color
        self.name = name
        self.device = device
        self.mode = ColorModes.INACTIVE
        # Set stub player in place for every card
        self.player = Player() if player is None else player

    def _draw_background(self, window):
        pygame.draw.rect(
            window,
            CARD_PALETTE[self.color][self.mode],
            (self.index * RECTANGLE_WIDTH, 0, RECTANGLE_WIDTH, WINDOW_HEIGHT),
        )

    def _draw_name(self, window):
        # Get the surface and rectangle for the text
        text_surface = font_big.render(
            self.name, True, FONT_PALETTE[Colors.BLACK][self.mode]
        )
        text_rect = text_surface.get_rect(
            center=(
                self.index * RECTANGLE_WIDTH + RECTANGLE_WIDTH // 2,
                WINDOW_HEIGHT // 4,
            )
        )
        # Blit the text onto the window
        window.blit(text_surface, text_rect)

    def _draw_device(self, window):
        # Get the surface and rectangle for the text
        text_surface = font_small.render(
            self.device, True, FONT_PALETTE[Colors.BLACK][self.mode]
        )
        text_rect = text_surface.get_rect(
            center=(
                self.index * RECTANGLE_WIDTH + RECTANGLE_WIDTH // 2,
                WINDOW_HEIGHT // 3.3,
            )
        )
        # Blit the text onto the window
        window.blit(text_surface, text_rect)

    def draw(self, window):
        self._draw_background(window)
        self._draw_name(window)
        self._draw_device(window)

    def switch_color(self):
        """Switch colors between light and dark."""
        self.mode = (
            ColorModes.DARK if self.mode == ColorModes.LIGHT else ColorModes.LIGHT
        )

    def highlight(self, active, action):
        """
        Highlight or remove it from card.
        If active is True, set dark color -- highligth the card.
        If active is False, set light color -- deselect the card.
        Action is then performed on the player, modifing the state.
        """
        self.mode = ColorModes.DARK if active else ColorModes.LIGHT
        action(self.player)  # Use this card player as self for action!


class PlayerCard(BoardCard):
    def __init__(self, index, color, name, device, player):
        super().__init__(index, color, name, device, player)

    def _draw_score(self, window):
        text_surface = font_medium.render(
            "Score", True, FONT_PALETTE[Colors.BLACK][self.mode]
        )
        text_rect = text_surface.get_rect(
            center=(
                self.index * RECTANGLE_WIDTH + RECTANGLE_WIDTH // 2,
                WINDOW_HEIGHT // 2,
            )
        )
        window.blit(text_surface, text_rect)

        text_surface = font_big.render(
            str(self.player.points), True, FONT_PALETTE[Colors.BLACK][self.mode]
        )
        text_rect = text_surface.get_rect(
            center=(
                self.index * RECTANGLE_WIDTH + RECTANGLE_WIDTH // 2,
                WINDOW_HEIGHT // 1.8,
            )
        )
        window.blit(text_surface, text_rect)

    def _draw_message(self, window):
        match self.player.player_state:
            case PlayerState.IDLE:
                message = ""
            case PlayerState.INTRO:
                message = "Press something to say hi!"
            case PlayerState.ACTIVE:
                message = "Press anything!"
            case PlayerState.ANSWERING:
                message = "Give answer!"
            case PlayerState.ELIMINATED:
                message = "Eliminated!"
            case PlayerState.WIN:
                message = "WINNER!"
            case _:
                raise RuntimeError("Unknown player state!")

        text_surface = font_medium.render(
            message, True, FONT_PALETTE[Colors.BLACK][self.mode]
        )
        text_rect = text_surface.get_rect(
            center=(
                self.index * RECTANGLE_WIDTH + RECTANGLE_WIDTH // 2,
                WINDOW_HEIGHT // 1.2,
            )
        )
        window.blit(text_surface, text_rect)

    def draw(self, window):
        super().draw(window)
        self._draw_score(window)
        self._draw_message(window)


class HostCard(BoardCard):
    def __init__(self, index, color, name, device):
        super().__init__(index, color, name, device, Host(index))

    def _draw_message(self, window):
        match self.player.host_state:
            case HostState.IDLE:
                message = ""
                text_surface = font_medium.render(
                    message, True, FONT_PALETTE[Colors.BLACK][self.mode]
                )
                text_rect = text_surface.get_rect(
                    center=(
                        self.index * RECTANGLE_WIDTH + RECTANGLE_WIDTH // 2,
                        WINDOW_HEIGHT // 1.2,
                    )
                )
                window.blit(text_surface, text_rect)
            case HostState.INTRO:
                lines = []
                lines += ["H - say hi!"]
                lines += ["SPACE - skip/introduce player"]
                # Render each line separately
                for line_num, line in enumerate(lines):
                    text_surface = font_small.render(
                        line, True, (FONT_PALETTE[Colors.BLACK][self.mode])
                    )
                    text_rect = text_surface.get_rect(
                        center=(
                            self.index * RECTANGLE_WIDTH + RECTANGLE_WIDTH // 2,
                            WINDOW_HEIGHT // 1.3
                            + (line_num - len(lines) // 2) * font_small.get_height(),
                        )
                    )
                    window.blit(text_surface, text_rect)
            case HostState.ACTIVE:
                lines = []
                lines += ["SPACE - skip/next"]
                lines += ["S - pause"]
                lines += ["C - play"]
                # Render each line separately
                for line_num, line in enumerate(lines):
                    text_surface = font_small.render(
                        line, True, (FONT_PALETTE[Colors.BLACK][self.mode])
                    )
                    text_rect = text_surface.get_rect(
                        center=(
                            self.index * RECTANGLE_WIDTH + RECTANGLE_WIDTH // 2,
                            WINDOW_HEIGHT // 1.3
                            + (line_num - len(lines) // 2) * font_small.get_height(),
                        )
                    )
                    window.blit(text_surface, text_rect)
            case HostState.RANKING:
                lines = []
                # lines += ["SPACE - skip/next"]
                # lines += ["S - pause"]
                # lines += ["C - play"]
                lines += ["1 - give points"]
                lines += ["0 - give penalty"]
                # Render each line separately
                for line_num, line in enumerate(lines):
                    text_surface = font_small.render(
                        line, True, (FONT_PALETTE[Colors.BLACK][self.mode])
                    )
                    text_rect = text_surface.get_rect(
                        center=(
                            self.index * RECTANGLE_WIDTH + RECTANGLE_WIDTH // 2,
                            WINDOW_HEIGHT // 1.3
                            + (line_num - len(lines) // 2) * font_small.get_height(),
                        )
                    )
                    window.blit(text_surface, text_rect)
            case _:
                raise RuntimeError("Unknown host state!")

    def draw(self, window):
        super().draw(window)
        self._draw_message(window)


class GameBoard:
    def __init__(self, window, players):
        self.window = window
        self.host_card = None
        self.player_cards = []
        self.placeholder_cards = []
        self._init_cards(players)

    def _init_cards(self, players):
        # Create players cards:
        for player in players:
            card = PlayerCard(
                index=player.number,
                color=Colors(player.number),
                name=f"Player {player.number}",
                device="joystick",
                player=player,
            )
            card.mode = ColorModes.LIGHT
            self.player_cards += [card]
        # Make the rest of players inactive:
        active_players = len(self.player_cards)
        for i in range(0, NUM_RECTANGLES - len(self.player_cards) - 1):
            number = active_players + i
            card = BoardCard(index=number, color=Colors(number))
            card.mode = ColorModes.INACTIVE
            self.placeholder_cards += [card]
        # Create host card:
        self.host_card = HostCard(
            index=NUM_RECTANGLES - 1,
            color=Colors.RED,
            name="The Host",
            device="keyboard",
        )
        self.host_card.mode = ColorModes.LIGHT

    def get_player_card(self, index):
        for card in self.player_cards:
            if index == card.player.number:
                return card

    # Draw gameboard
    def draw(self):
        # Draw Player cards from left:
        for card in self.player_cards:
            card.draw(self.window)
        # Draw placeholder cards:
        for card in self.placeholder_cards:
            card.draw(self.window)
        # Draw Host on the right:
        self.host_card.draw(self.window)
        # Update display
        pygame.display.update()
