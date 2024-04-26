import coloredlogs, logging


def create_level(logger, constant, name, color):
    logging.addLevelName(constant, name)
    coloredlogs.DEFAULT_LEVEL_STYLES[name.lower()] = {"color": color}

    def level_function(msg, *args, **kwargs):
        # Capture logger from here
        if logger.isEnabledFor(constant):
            logger.log(constant, msg)
        else:
            raise RuntimeError("Unknown logger!")

    return level_function


def init_logger(name):
    # Initialize logger
    logger = logging.getLogger(name)
    coloredlogs.install(level="DEBUG")

    # Add custom commands to logger
    logger.game = create_level(logger, logging.INFO + 5, "GAME", "white")
    logger.host = create_level(logger, logging.INFO + 6, "HOST", "red")
    logger.player = create_level(logger, logging.INFO + 7, "PLAYER", "yellow")
    logger.sound = create_level(logger, logging.INFO + 8, "SOUND", "cyan")
    logger.song = create_level(logger, logging.INFO + 9, "SONG", "green")

    return logger
