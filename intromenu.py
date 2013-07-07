__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

# Various needed imports.
import pygame, sys
from pygame.locals import *
from libs import pyganim
import useful
import textitem
import logo
import debug
import math
from settings import *

# Import any needed game screens here.
import game

def setup_logo():
	# Create the logo
	temp_logo = logo.Logo()

	# Set the logo so it displays in the middle of the screen.
	x = (SCREEN_WIDTH - temp_logo.get_width()) // 2
	y = ((SCREEN_HEIGHT - temp_logo.get_height()) // 2) - 30
	temp_logo.x = x
	temp_logo.y = y

	# At last, return the surface so we can blit it to the window_surface.
	return temp_logo

def setup_message(logo_x, logo_y):
	message_text = "Press ENTER to start"
	message_font_path = "fonts/8-BIT WONDER.TTF"
	message_font_size = 18
	message_font_color = (255, 255, 255)
	message_alpha_value = 255

	message = textitem.TextItem(message_text, message_font_path, message_font_size, message_font_color, message_alpha_value)

	message_x = (SCREEN_WIDTH - message.get_width()) // 2
	message_y = logo_y + 150
	message.x = message_x
	message.y = message_y

	return message

def setup_music():
	pygame.mixer.music.load(INTRO_MUSIC)
	pygame.mixer.music.play()

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

	# Setup and play music.
	setup_music()
		
	# Keeps track of how much time has passed.
	time_passed = 0

	current_angle = 0
	max_angle = 15
	min_angle = -15
	rotate_step = 0.40
	rotate_up = True
	current_scale = 8
	max_scale = 8.25
	min_scale = 7.75
	scale_by = 0.01
	scale_up = True

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

		# Increment the time passed.
		time_passed += main_clock.get_time()
		
		# Blinks the title message. Sets the time_passed value to either blink_rate // 3 or 0.
		time_passed = title_message.blink(time_passed, title_message_blink_rate)
		
		# Pyganim blits object to the given argument, pygame blits the given argument to object...
		temp_logo_width = int(title_logo_surface.getRect().width * current_scale)
		temp_logo_height = int(title_logo_surface.getRect().height * current_scale)
		temp_logo = pygame.transform.scale(title_logo_surface.getCurrentFrame(), (temp_logo_width, temp_logo_height))
		temp_logo = pygame.transform.rotate(temp_logo, current_angle)
		temp_logo_x = (SCREEN_WIDTH - temp_logo.get_width()) // 2
		temp_logo_y = ((SCREEN_HEIGHT - temp_logo.get_height()) // 2) - 30
		window_surface.blit(temp_logo, (temp_logo_x, temp_logo_y))
		
		if rotate_up:
			current_angle = current_angle + rotate_step
		else:
			current_angle = current_angle - rotate_step

		if current_angle > max_angle:
			current_angle = max_angle
			rotate_up = False
		elif current_angle < min_angle:
			current_angle = min_angle
			rotate_up = True

		if scale_up:
			current_scale = current_scale + scale_by
		else:
			current_scale = current_scale - scale_by

		if current_scale > max_scale:
			current_scale = max_scale
			scale_up = False
		elif current_scale < min_scale:
			current_scale = min_scale
			scale_up = True

		#title_logo_surface.blit(window_surface, (title_logo.x, title_logo.y))
		window_surface.blit(title_message_surface, (title_message.x, title_message.y))
		
		if DEBUG_MODE:
			# Display various debug information.
			debug.display(window_surface, main_clock, debug_font)
		
		pygame.display.update()
		
		# Finally, constrain the game to a set maximum amount of FPS.
		main_clock.tick(MAX_FPS)