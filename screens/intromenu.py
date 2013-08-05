__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
from libs import pyganim
import math
import other.debug as debug
import other.useful as useful
import gui.textitem as textitem
import gui.logo as logo
from settings.settings import *

# Import any needed game screens here.
import screens.game as game

def setup_logo():
	# Create the logo
	title_logo = logo.Logo()

	# Set the logo so it displays in the middle of the screen.
	x = (SCREEN_WIDTH - title_logo.get_width()) / 2
	y = ((SCREEN_HEIGHT - title_logo.get_height()) / 2) - 30
	title_logo.x = x
	title_logo.y = y

	# At last, return the surface so we can blit it to the window_surface.
	return title_logo

def setup_message(title_logo):
	text = "Press ENTER to start"
	font_color = (255, 255, 255)
	alpha_value = 255
	offset = 50

	text = textitem.TextItem(text, font_color, alpha_value)

	text.x = (SCREEN_WIDTH - text.get_width()) / 2
	text.y = title_logo.y + title_logo.get_height() + offset

	return text

def setup_music():
	pygame.mixer.music.load(TITLE_MUSIC)
	pygame.mixer.music.play()

def main(window_surface, main_clock, debug_font):
	# Setup the logo and store the surface of the logo.
	title_logo = setup_logo()
	title_logo.play()

	# Setup the message beneath the logo and store the surface of the message.
	title_message = setup_message(title_logo)
	# Sets the blink rate of the message.
	title_message_blink_rate = 750

	# Setup and play music.
	setup_music()
		
	# Keeps track of how much time has passed.
	time_passed = 0

	while True:
		# Every frame begins by filling the whole screen with the background color.
		window_surface.fill(BACKGROUND_COLOR)
		
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				# If the ESCAPE key is pressed or the window is closed, the game is shut down.
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN and event.key == K_RETURN:
				# If ENTER is pressed, proceed to the next screen, and end this loop.
				pygame.mixer.music.stop()
				game.main(window_surface, main_clock, debug_font)
		
		# If the music isn't playing, start it.
		if not pygame.mixer.music.get_busy():
			pygame.mixer.music.play()

		# Draw the logo.
		title_logo.draw(window_surface)

		# Increment the time passed.
		time_passed += main_clock.get_time()
		# Blinks the title message.
		time_passed = title_message.blink(time_passed, title_message_blink_rate)

		# Draw the title message.
		title_message.draw(window_surface)
		
		if DEBUG_MODE:
			# Display various debug information.
			debug.display(window_surface, main_clock, debug_font)

		pygame.display.update()
		
		# Finally, constrain the game to a set maximum amount of FPS.
		main_clock.tick(MAX_FPS)