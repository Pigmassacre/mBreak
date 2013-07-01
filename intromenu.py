__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

# Various needed imports.
import pygame
from pygame.locals import *
from libs import pyganim
import useful
import debug
from settings import *

# Import any needed game screens here.
import game

def setup_logo():
	# Create the logo
	logo = useful.Logo()

	# Set the logo so it displays in the middle of the screen.
	logo_x = (SCREEN_WIDTH - logo.get_width()) // 2
	logo_y = ((SCREEN_HEIGHT - logo.get_height()) // 2) - 30
	logo.x = logo_x
	logo.y = logo_y

	# At last, return the surface so we can blit it to the window_surface.
	return logo

def setup_message(logo_x, logo_y):
	message_text = "Press ENTER to start"
	message_font_path = "fonts/8-BIT WONDER.TTF"
	message_font_size = 18
	message_font_color = (255, 255, 255)
	message_alpha_value = 255

	message = useful.TextItem(message_text, message_font_path, message_font_size, message_font_color, message_alpha_value)

	message_x = (SCREEN_WIDTH - message.get_width()) // 2
	message_y = logo_y + 150
	message.x = message_x
	message.y = message_y

	return message

def main(window_surface, main_clock, debug_font):
	# Setup the logo and store the surface of the logo.
	title_logo = setup_logo()
	title_logo.play()
	title_logo_surface = title_logo.logo

	# Setup the message beneath the logo and store the surface of the message.
	title_message = setup_message(title_logo.x, title_logo.y)
	title_message_surface = title_message.surface
	# Sets the blink rate of the message.
	title_message_blink_rate = 750
		
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
				game.main(window_surface, main_clock, debug_font)
				break
		
		# Increment the time passed.
		time_passed += main_clock.get_time()
		
		# Blinks the title message. Sets the time_passed value to either blink_rate // 3 or 0.
		time_passed = title_message.blink(time_passed, title_message_blink_rate)
		
		# Pyganim blits object to the given argument, pygame blits the given argument to object...
		title_logo_surface.blit(window_surface, (title_logo.x, title_logo.y))
		window_surface.blit(title_message_surface, (title_message.x, title_message.y))
		
		if DEBUG_MODE:
			# Display various debug information.
			debug.display(window_surface, main_clock, debug_font)
		
		pygame.display.update()
		
		# Finally, constrain the game to a set maximum amount of FPS.
		main_clock.tick(MAX_FPS)