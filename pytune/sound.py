import os
from random import shuffle
import pygame

from .logger import init_logger


logger = init_logger(__name__)


class Sound:
    def __init__(self, path, random_order=True):
        self.path = path
        self.songs = self._load_songs(self.path, random_order)
        self.current_song = None

    def _load_songs(self, path, random_order):
        # Check if the folder exists
        if not os.path.exists(path):
            raise OSError(f"Folder '{path}' does not exist!")
        files = os.listdir(path)
        # Filter out music files
        songs = [file for file in files if file.endswith((".mp3", ".wav"))]
        if random_order:
            shuffle(songs)
        return songs

    def play_next_song(self):
        # Free resources if possible:
        try:
            pygame.mixer.music.unload()
        except:
            pass
        # Get the next song from the list:
        try:
            self.current_song = self.songs.pop(0)
        except IndexError:
            logger.game("No more songs! The game ends here!")
            return 1
        # Play song and log info:
        logger.song(f"Playing: {self.current_song}")
        pygame.mixer.music.load(os.path.join(self.path, self.current_song))
        pygame.mixer.music.play()
        return 0

    def continue_current_song(self):
        logger.sound(f"Continuing: {self.current_song}")
        pygame.mixer.music.unpause()
        return 0

    def pause_current_song(self):
        logger.sound(f"Stopping: {self.current_song}")
        pygame.mixer.music.pause()
        return 0
