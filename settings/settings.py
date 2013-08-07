from pygame.locals import *

# Screen width and height is the game window width and height.
SCREEN_WIDTH = 285#854
SCREEN_HEIGHT = 160#480

# Game scale will scale the graphics of the game, but will keep the smoothness of the movement.
GAME_SCALE = 2

# Level width and height is the actual level width and height. Level x and y is the position in the base area that the level is placed in.
LEVEL_WIDTH = 176 * GAME_SCALE
LEVEL_HEIGHT = 120 * GAME_SCALE
LEVEL_X = (SCREEN_WIDTH - LEVEL_WIDTH) / 2 
LEVEL_Y = (SCREEN_HEIGHT - LEVEL_HEIGHT) / 2
LEVEL_MAX_X = LEVEL_X + LEVEL_WIDTH
LEVEL_MAX_Y = LEVEL_Y + LEVEL_HEIGHT

WINDOW_CAPTION = "mBreak"
BACKGROUND_COLOR = (0, 0, 0)
MAX_FPS = 60

# Music settings
TITLE_MUSIC = "res/music/title_screen.ogg"

# Player Left settings.
PLAYER_LEFT_NAME = "Player Left"
PLAYER_LEFT_KEY_UP = K_w
PLAYER_LEFT_KEY_DOWN = K_s

# Player Right settings.
PLAYER_RIGHT_NAME = "Player Right"
PLAYER_RIGHT_KEY_UP = K_UP
PLAYER_RIGHT_KEY_DOWN = K_DOWN

# Enables various debug information.
DEBUG_MODE = True
DEBUG_FONT = "fonts/8-BIT WONDER.TTF"