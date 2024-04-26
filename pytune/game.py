import os
import time
from enum import Enum
import pygame

from .graphics import ColorModes
from .logger import init_logger
from .player import Host, Player
from .sound import Sound


logger = init_logger(__name__)

class GameState(Enum):
    ERROR = -1
    QUIT = 0
    IDLE = 1
    INTRO = 2
    MUSIC_ROUND = 3
    RANKING_ROUND = 4
    HOST_ROUND = 5
    PLAYER_ROUND = 6


class Actors(Enum):
    HOST = -1


class Game:
    def __init__(self, path, random_order):
        self.players = self._init_players()
        self.disabled_players = []  # Disabled joysticks
        self.current_state = GameState.IDLE
        self.who_stopped = Actors.HOST
        self.sound = Sound(path, random_order)

    def _init_players(self):
        # Initialize joystick(s) and Players
        players = []
        number_of_joysticks = pygame.joystick.get_count()
        if number_of_joysticks > 0:
            for joystick_id in range(0, number_of_joysticks):
                # Create a player
                players.append(Player(joystick_id, pygame.joystick.Joystick(joystick_id)))
                players[joystick_id].joystick.init()
                logger.debug(f"DEBUG: {players[joystick_id].number}")
                logger.debug(f"DEBUG: {players[joystick_id].joystick}")
                logger.debug(f"DEBUG: {players[joystick_id].joystick.get_init()}")
                logger.debug(f"DEBUG: {players[joystick_id].joystick.get_name()}")
        else:
            raise RuntimeError("No joysticks detected!")
        return players

    # TODO: to return somehow to main function and exit properly?
    # For example break from game loops and check if current state is QUIT?
    def quit(self):
        self.current_state = GameState.QUIT
        self.sound.pause_current_song()
        logger.game("Game exited.")
        pygame.quit()
        exit()

    def check_quit(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.quit()

    def show_intro(self, board):
        # Intro music queue:
        pygame.mixer.music.load(os.path.join("./assets", "intro_start.wav"))
        pygame.mixer.music.play()
        pygame.mixer.music.queue(os.path.join("./assets", "intro_middle.wav"), loops=-1)
        # Welcome as Host:
        logger.host(f"Press 'H' as HOST to say hi...")
        logger.host(f"Press spacebar as HOST to skip...")
        self.current_state = GameState.INTRO
        board.host_card.player.set_intro()
        while self.current_state == GameState.INTRO:
            for event in pygame.event.get():
                # Host actions:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.current_state = GameState.IDLE
                # Host can check the device - "say hi"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                    board.host_card.switch_color()  # Switch colors on action.
                # Check for 'Esc' key press to quit the game
                self.check_quit(event)
            # Update the graphics
            board.draw()
        # Set Host to active state and indicate that input is needed:
        board.host_card.highlight(active=True, action=Host.set_active)
        # Begin player introductions:
        for player in self.players:
            logger.game(f"Welcome Player #{player.number}")
            logger.debug(f"DEBUG: {player.joystick}")
            # Shake the joystick:
            player.joystick.rumble(low_frequency=0.5, high_frequency=1.0, duration=2)
            logger.host(f"Press spacebar as HOST to show next Player #{player.number}...")
            # Set game state:
            self.current_state = GameState.INTRO
            # Get player card:
            card = board.get_player_card(player.number)
            card.player.set_intro()
            # Start intro:
            while self.current_state == GameState.INTRO:
                for event in pygame.event.get():
                    # Host actions:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        player.joystick.rumble(low_frequency=0.5, high_frequency=1.0, duration=2)
                        # player.joystick.stop_rumble()
                        self.current_state = GameState.IDLE
                    # Continue song:
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                        self.host_continue_song(board)
                    # Stop song:
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                        self.host_pause_song(board)
                    # Player can check the device - "say hi"
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.instance_id == player.number:
                            card.switch_color()  # Switch colors on action.
                    # Check for 'Esc' key press to quit the game
                    self.check_quit(event)
                # Update the graphics
                board.draw()
            # Restore cards and players to original state:
            card.highlight(active=False, action=Player.set_idle)
        # Ends music with fade out effect
        pygame.mixer.music.fadeout(5000)  # time in ms, TODO: parametrize
        # Set Host to active state:
        board.host_card.player.set_active()
        # Set all player to ACTIVE to show message:
        for card in board.player_cards:
            card.player.set_active()
        # Shake all joysticks:
        for player in self.players:
            player.joystick.rumble(low_frequency=0.5, high_frequency=1.0, duration=2)
        # Set game state to IDLE to show message:
        self.current_state = GameState.IDLE

    def listen_to_players(self, event, board):
        # Players are only active during MUSIC_ROUND
        if self.current_state == GameState.MUSIC_ROUND:
            if event.type == pygame.JOYBUTTONDOWN:
                if event.instance_id not in self.disabled_players:
                    self.sound.pause_current_song()
                    self.who_stopped = event.instance_id
                    self.current_state = GameState.RANKING_ROUND
                    # Get card and update it to highlight:
                    board.get_player_card(self.who_stopped).highlight(active=True, action=Host.set_answering)
                    # Set Host to ranking state and indicate that input is needed:
                    board.host_card.highlight(active=True, action=Host.set_ranking)
                    logger.player(f"Song stopped by the Player #{self.who_stopped}!")
                    logger.host(f"Give points to the Player #{self.who_stopped}...")

    def host_continue_song(self, board):
        # Set Host to active state and remove highlight.
        # This indicates that host started the music again.
        board.host_card.highlight(active=False, action=Host.set_active)
        if self.sound.continue_current_song() == 1:
            self.quit()

    def host_pause_song(self, board):
        # Set Host to active state and keep highlighted.
        # This indicates that host needs to either skip
        # the round or resume music.
        board.host_card.highlight(active=True, action=Host.set_active)
        if self.sound.pause_current_song() == 1:
            self.quit()

    def host_next_song(self, board):
        # Set Host to active state and remove the highlight:
        board.host_card.highlight(active=False, action=Host.set_active)
        # Restore all players and cards:
        for card in board.player_cards:
            card.highlight(active=False, action=Player.set_active)
        # Play next song and check returned code.
        # If sound code equals to 1, there is no more songs,
        # the game ends here.
        if self.sound.play_next_song() == 1:
            self.quit()
        # Clear disabled players list:
        self.disabled_players = []
        self.current_state = GameState.MUSIC_ROUND
        logger.sound("Song started!")
        logger.game("Players, press anything to stop the song!")

    def host_skip_song(self, board):
        # Set Host to active state and keep highlighted.
        # This indicates that host needs to play next song.
        board.host_card.highlight(active=True, action=Host.set_active)
        # Restore all players and cards:
        for card in board.player_cards:
            card.highlight(active=False, action=Player.set_active)
        # Skip the song:
        self.sound.pause_current_song()
        self.who_stopped = Actors.HOST
        self.current_state = GameState.IDLE
        logger.host(f"Song skipped by the HOST! Play next song by pressing space!")

    def host_give_minus(self, board):
        for player in self.players:
            if self.who_stopped == player.number:
                player.points -= 1
                # Get card and update it to eliminated:
                board.get_player_card(self.who_stopped).highlight(active=False, action=Player.set_eliminated)
                # Set Host to active state and keep highlighted.
                # This indicates that host needs to either skip
                # the round or play again.
                board.host_card.highlight(active=True, action=Host.set_active)
                logger.game(f"Penalty points to the Player #{self.who_stopped}!")
        # Put the player on disabled players list:
        self.disabled_players += [self.who_stopped]
        # Change the who_stopped to HOST:
        self.who_stopped = Actors.HOST
        # Continue music round:
        # TODO: should music start automatically?
        self.current_state = GameState.MUSIC_ROUND  # GameState.IDLE
        logger.host(f"Now HOST is in control!")

    def host_give_plus(self, board):
        for player in self.players:
            if self.who_stopped == player.number:
                player.points += 1
                # Get card and update it to highlight:
                board.get_player_card(self.who_stopped).highlight(active=True, action=Player.set_win)
                # Set Host to active state and keep highlighted.
                # This indicates that host needs to skip or
                # play the song for the rest to check.
                board.host_card.highlight(active=True, action=Host.set_active)
                logger.game(f"Points awarded to the Player #{self.who_stopped}!")
        self.who_stopped = Actors.HOST
        self.current_state = GameState.IDLE
        logger.host(f"Now HOST is in control!")

    def listen_to_host(self, event, board):
        # Start the music
        if self.current_state == GameState.IDLE:
            # Start next song:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.host_next_song(board)
            # Continue song:
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                self.host_continue_song(board)
            # Stop song:
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self.host_pause_song(board)
        # Stop the music
        elif self.current_state == GameState.MUSIC_ROUND:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.host_skip_song(board)
            # Continue song:
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                self.host_continue_song(board)
            # Stop song:
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self.host_pause_song(board)
        elif self.current_state == GameState.RANKING_ROUND:
            # Give points to the player who stopped.
            # If player who stopped is the HOST, this is disabled.                        
            if self.who_stopped != Actors.HOST:
                # Check for "0" key press (-1 points)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_0:
                    self.host_give_minus(board)
                # Check for "1" key press (1 point)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                    self.host_give_plus(board)

    def start_game(self, board):
        logger.host("Press '0' for no points, '1' for points, and 'Esc' to quit.")
        logger.host("Press spacebar to start the song.")
        while True:
            # Music Round -- Player/Host
            for event in pygame.event.get():
                # Listen to player inputs
                self.listen_to_players(event, board)
                # Listen to host inputs
                self.listen_to_host(event, board)
                # Game Quit, can exit at any point
                # Check for 'Esc' key press to quit the game
                self.check_quit(event)
                # If is changing the GameState
                # exit this loop and go into another one
                if self.current_state == GameState.IDLE:
                    break

            # Ranking Round -- Host Round
            for event in pygame.event.get():
                self.listen_to_host(event, board)
                self.check_quit(event)
                if self.current_state != GameState.IDLE:
                    break

            # Update the graphics
            board.draw()
            time.sleep(0.1)
