from pygame.locals import *

# Game scale will scale the graphics of the game, but will keep the smoothness of the movement.
GAME_SCALE = 2

# Base width and height is the actual game width and height.
BASE_WIDTH = 244 * GAME_SCALE
BASE_HEIGHT = 140 * GAME_SCALE

# Level width and height is the actual level width and height. Level x and y is the position in the base area that the level is placed in.
LEVEL_WIDTH = 176 * GAME_SCALE
LEVEL_HEIGHT = 120 * GAME_SCALE
LEVEL_X = 34 * GAME_SCALE
LEVEL_Y = 10 * GAME_SCALE
LEVEL_MAX_X = LEVEL_X + LEVEL_WIDTH
LEVEL_MAX_Y = LEVEL_Y + LEVEL_HEIGHT

# Screen width and height is the game window width and height.
SCREEN_WIDTH = 976
SCREEN_HEIGHT = 560

WINDOW_CAPTION = "mBreak"
BACKGROUND_COLOR = (64, 64, 64)
MAX_FPS = 60

""" Graphical settings """
# Ball settings
BALL_TRAILS = False

# Shadow settings
SHADOWS = True

# Text shadow settings
TEXT_SHADOWS = True
TEXT_SHADOW_OFFSET = 3
TEXT_SHADOW_COLOR = (0, 0, 0, 255)

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