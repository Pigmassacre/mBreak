import pygame.locals
import os
import shutil

"""

Contains various settings for the game. Some of these can be changed in settings.txt.

Load, when called, will try to load the settings.txt file and read the settings from it and save those so the game
can use them.

Save on the other hand, will take the current values of the variables and try to save them to settings.txt

"""

# Game scale will scale the graphics of the game, but will keep the smoothness of the movement.
# I recommend a value of 3. This performs well on my machine while still keeping a relatively high resolution. You can change it to
# whatever you want, of course.
GAME_SCALE = 4

# This is the amount of ticks that the game will be designed to work with. When the game runs at any other FPS than this, delta time calculations
# will make sure that the game still plays as if the game ran at 60 FPS.
GAME_FPS = 60

# Screen width and height is the game window width and height.
SCREEN_WIDTH = int(285 * GAME_SCALE)
SCREEN_HEIGHT = int(160 * GAME_SCALE)

# Level width and height is the actual level width and height. Level x and y is the position in the base area that the level is placed in.
LEVEL_WIDTH = 176 * GAME_SCALE
LEVEL_HEIGHT = 120 * GAME_SCALE
LEVEL_X = (SCREEN_WIDTH - LEVEL_WIDTH) / 2 
LEVEL_Y = (SCREEN_HEIGHT - LEVEL_HEIGHT) / 2
LEVEL_MAX_X = LEVEL_X + LEVEL_WIDTH
LEVEL_MAX_Y = LEVEL_Y + LEVEL_HEIGHT

WINDOW_CAPTION = "mBreak"
BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (200, 200, 200)

# Music settings
TITLE_MUSIC = "res/music/sexxxy_bit_3!!!.xm"
GAME_MUSIC = "res/music/stardstm.mod"
AFTER_GAME_MUSIC = "res/music/october_chip.xm"

# Player One settings.
PLAYER_ONE_NAME = "One"
PLAYER_ONE_KEY_UP = pygame.locals.K_w
PLAYER_ONE_KEY_DOWN = pygame.locals.K_s
PLAYER_ONE_KEY_UNLEASH_CHARGE = pygame.locals.K_r
PLAYER_ONE_JOY_UNLEASH_CHARGE = 2

# Player Two settings.
PLAYER_TWO_NAME = "Two"
PLAYER_TWO_KEY_UP = pygame.locals.K_UP
PLAYER_TWO_KEY_DOWN = pygame.locals.K_DOWN
PLAYER_TWO_KEY_UNLEASH_CHARGE = pygame.locals.K_RSHIFT
PLAYER_TWO_JOY_UNLEASH_CHARGE = 2

# Enables various debug information.
DEBUG_MODE = True
DEBUG_FONT = "fonts/ADDLG___.TTF"

def load():
	# Tries to load the settings from settings.txt.
	global DEBUG_MODE
	global PLAYER_ONE_NAME
	global PLAYER_TWO_NAME
	global SCREEN_WIDTH
	global SCREEN_HEIGHT
	global LEVEL_X
	global LEVEL_Y
	global LEVEL_MAX_X
	global LEVEL_MAX_Y

	try:
		# This will raise an OSError if the file doesn't exist.
		if os.path.getsize("settings.txt") == 0:
			raise OSError
	except OSError:
		# If the file doesn't exist, fill it with the default values.
		file = open("settings.txt", "w")
		file.write("debugmode 	0\n")
		file.write("\n")
		file.write("# PLAYER 1 SETTINGS\n")
		file.write("p1name		" + PLAYER_ONE_NAME + "\n")
		file.write("\n")
		file.write("# PLAYER 2 SETTINGS\n")
		file.write("p2name		" + PLAYER_TWO_NAME + "\n")
		file.write("\n")
		file.write("# GRAPHICS\n")
		file.write("shadows 	1\n")
		file.write("particles 	1\n")
		file.write("traces 		1\n")
		file.write("background 	1\n")
		file.write("resolution	855x480")
		file.close()

	# We open and read the settings file line by line.
	file = open("settings.txt", "r")
	try:
		# If the settings.txt file isn't empty, try to load the values.
		for line in file:
			if "debugmode" in line:
				DEBUG_MODE = bool(int(line.strip("debugmode").strip()))
			elif "p1name" in line:
				PLAYER_ONE_NAME = line.strip("p1name").strip()
			elif "p2name" in line:
				PLAYER_TWO_NAME = line.strip("p2name").strip()
			elif "resolution" in line:
				resolution = line.strip("resolution").strip().split("x")
				SCREEN_WIDTH = int(resolution[0])
				SCREEN_HEIGHT = int(resolution[1])
	finally:
		file.close()
			
	# Now, set values that depend on values loaded here.
	LEVEL_X = (SCREEN_WIDTH - LEVEL_WIDTH) / 2 
	LEVEL_Y = (SCREEN_HEIGHT - LEVEL_HEIGHT) / 2
	LEVEL_MAX_X = LEVEL_X + LEVEL_WIDTH
	LEVEL_MAX_Y = LEVEL_Y + LEVEL_HEIGHT

def save():
	# Tries to save the settings to settings.txt.
	global DEBUG_MODE
	global PLAYER_ONE_NAME
	global PLAYER_TWO_NAME

	# We use a temporary file to write to, so we don't corrupt our old file if the process fails.
	temp_file = open("settings.txt.tmp", "w")
	
	# Open and read the settings file line by line.
	file = open("settings.txt", "r+")
	try:
		for line in file:
			if "debugmode" in line:
				temp_file.write(line.replace(line.strip("debugmode").strip(), str(int(DEBUG_MODE))))
			elif "p1name" in line:
				temp_file.write(line.replace(line.strip("p1name").strip(), PLAYER_ONE_NAME))
			elif "p2name" in line:
				temp_file.write(line.replace(line.strip("p2name").strip(), PLAYER_TWO_NAME))
			else:
				temp_file.write(line)
	finally:
		# We must remember to close both files since we're done.
		temp_file.close()
		file.close()
	
	# We're done, so we rename the temp file.
	try:
		shutil.copy("settings.txt", "settings.txt.backup")
		os.remove("settings.txt")
		os.rename("settings.txt.tmp", "settings.txt")
		os.remove("settings.txt.backup")
	except OSError:
		print("Error renaming and removing temporary file at end of the procedure.")
		