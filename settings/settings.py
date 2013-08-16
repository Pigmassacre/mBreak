import pygame.locals
import os
import shutil

# Game scale will scale the graphics of the game, but will keep the smoothness of the movement.
GAME_SCALE = 3

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
MAX_FPS = 60

# Music settings
TITLE_MUSIC = "res/music/title_screen.ogg"

# Player One settings.
PLAYER_ONE_NAME = "One"
PLAYER_ONE_KEY_UP = pygame.locals.K_w
PLAYER_ONE_KEY_DOWN = pygame.locals.K_s

# Player Two settings.
PLAYER_TWO_NAME = "Two"
PLAYER_TWO_KEY_UP = pygame.locals.K_UP
PLAYER_TWO_KEY_DOWN = pygame.locals.K_DOWN

# Enables various debug information.
DEBUG_MODE = True
DEBUG_FONT = "fonts/8-BIT WONDER.TTF"

def load():
	# Tries to load the player names from settings.txt.
	global PLAYER_ONE_NAME
	global PLAYER_TWO_NAME

	try:
		# This will raise an OSError if the file doesn't exist.
		if os.path.getsize("settings.txt") == 0:
			raise OSError
	except OSError:
		# If the file doesn't exist, fill it with the default values.
		file = open("settings.txt", "w")
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
		file.write("background 	1")
		file.close()

	# We open and read the settings file line by line.
	file = open("settings.txt", "r")
	try:
		# If the settings.txt file isn't empty, try to load the values.
		for line in file:
			if "p1name" in line:
				PLAYER_ONE_NAME = line.strip("p1name").strip()
			elif "p2name" in line:
				PLAYER_TWO_NAME = line.strip("p2name").strip()
	finally:
		file.close()
			
def save():
	# Tries to save the player names to settings.txt.
	global PLAYER_ONE_NAME
	global PLAYER_TWO_NAME

	# We use a temporary file to write to, so we don't corrupt our old file if the process fails.
	temp_file = open("settings.txt.tmp", "w")
	
	# Open and read the settings file line by line.
	file = open("settings.txt", "r+")
	try:
		for line in file:
			if "p1name" in line:
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
		