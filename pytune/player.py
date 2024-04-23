from enum import Enum


class PlayerState(Enum):
    IDLE = 0
    INTRO = 1
    ACTIVE = 2
    ANSWERING = 3
    ELIMINATED = 4
    WIN = 5


class Player:
    def __init__(self, number=None, joystick=None):
        self.number = number
        self.joystick = joystick
        self.points = 0
        self.player_state = PlayerState.IDLE

    def set_idle(self):
        self.player_state = PlayerState.IDLE

    def set_intro(self):
        self.player_state = PlayerState.INTRO

    def set_active(self):
        self.player_state = PlayerState.ACTIVE

    def set_answering(self):
        self.player_state = PlayerState.ANSWERING

    def set_eliminated(self):
        self.player_state = PlayerState.ELIMINATED

    def set_win(self):
        self.player_state = PlayerState.WIN


class HostState(Enum):
    IDLE = 0
    INTRO = 1
    ACTIVE = 2
    RANKING = 3


class Host(Player):
    def __init__(self, number=None):
        self.number = number
        self.host_state = HostState.IDLE

    def set_idle(self):
        self.host_state = HostState.IDLE

    def set_intro(self):
        self.host_state = HostState.INTRO

    def set_active(self):
        self.host_state = HostState.ACTIVE

    def set_ranking(self):
        self.host_state = HostState.RANKING
