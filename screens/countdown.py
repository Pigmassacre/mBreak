__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import gui.textitem as textitem
import settings.settings as settings
import objects.arrow_indicator as arrow_indicator
import random
import math
import objects.ball as ball

"""

This class displays a countdown when the update_and_draw method is called, if the countdown isn't already over.

This is used at the beginning of each round.

"""

class Countdown:

	def __init__(self, main_clock, function_to_call, initial_angle):
		# We use the main clock to keep track of the time passed.
		self.main_clock = main_clock

		# This is the function that is called when the countdown is over.
		self.function_to_call = function_to_call

		# When time passed reaches time to countdown, the countdown ends.
		self.time_passed = 0
		self.time_to_countdown = 1250

		# This is the amount of time that ready is displayed.
		self.countdown_ready_time = 2000

		# This is the amount of time that go is displayed.
		self.countdown_go_time = 1250

		# Create individual letters for "Ready"
		self.ready_letters = []
		base_size = 18
		word = "Ready"
		total_width = 0
		letter_spacing = 2  # Pixels between letters
        
		# First calculate total width (subtract one letter spacing since we don't need spacing after the last letter)
		for letter in word:
			letter_item = textitem.TextItem(letter, (255, 255, 255))
			letter_item.set_size(base_size)
			total_width += letter_item.get_width() + letter_spacing
		total_width -= letter_spacing  # Remove the extra spacing after last letter
		
		# Now create and position each letter
		x_pos = (settings.SCREEN_WIDTH - total_width) / 2
		for i, letter in enumerate(word):
			letter_item = textitem.TextItem(letter, (255, 255, 255))
			letter_item.set_size(base_size)
			letter_item.x = x_pos
			letter_item.y = (settings.SCREEN_HEIGHT - letter_item.get_height()) / 2
			x_pos += letter_item.get_width() + letter_spacing
			# Add sine wave offset data for each letter
			self.ready_letters.append({
				'text': letter_item,
				'phase_offset': i * math.pi / 3,  # Offset each letter's sine wave
				'base_y': letter_item.y,
				'base_x': letter_item.x  # Store the base x position for scaling
			})
		
		# Animation properties for Ready text
		self.ready_scale = 0.25
		self.ready_target_scale = 1.0
		self.ready_scale_speed = 1.5
		self.ready_alpha = 0
		self.ready_fade_in_speed = 400
		self.ready_fade_out_speed = 1020
		self.ready_display_time = 1000
		self.sine_frequency = 2.0  # Constant frequency in cycles per second
		self.initial_amplitude = 20.0  # Initial amplitude in pixels

		# Create, position and store the "GO" textitem.
		self.countdown_go = textitem.TextItem("GO!", (255, 255, 255))
		self.countdown_go.set_size(18)  # Base size
		# Center the GO text
		self.countdown_go.x = (settings.SCREEN_WIDTH - self.countdown_go.get_width()) / 2
		self.countdown_go.y = (settings.SCREEN_HEIGHT - self.countdown_go.get_height()) / 2
		
		# Animation properties for GO text
		self.go_scale = 0.5  # Start from half size
		self.go_target_scale = 2.0  # Maximum scale
		self.go_overshoot_scale = 2.4  # Scale to overshoot to (more overshoot)
		self.go_undershoot_scale = 1.8  # Scale to undershoot to (more undershoot)
		self.go_scale_speed = 1.5  # How fast it scales up
		self.go_alpha = 0  # Start fully transparent
		self.go_fade_in_speed = 400  # Increased to accommodate longer bounce animation
		self.go_fade_out_speed = 1020  # Fade out speed (faster than fade in)
		self.go_display_time = 500  # How long to stay at full opacity in milliseconds
		self.shadow_offset = 2  # Pixels offset for shadow
		
		# Timing for bounce effect phases (in milliseconds)
		self.scale_overshoot_time = 200  # More time to reach overshoot
		self.scale_undershoot_time = 300  # More time to reach undershoot
		self.scale_settle_time = 400  # More time to settle at final scale

		# Create the arrow indicator at the ball's starting position
		ball_x = settings.LEVEL_X + (settings.LEVEL_WIDTH + ball.Ball.width) / 2
		ball_y = settings.LEVEL_Y + (settings.LEVEL_HEIGHT + ball.Ball.height) / 2
		self.arrow = arrow_indicator.ArrowIndicator(ball_x, ball_y, initial_angle)

		# This is used to keep track of if the countdown is over or not.
		self.done = False

	def update(self):
		# If we're not done with the countdown...
		if not self.done:
			# Add the time passed.
			self.time_passed += self.main_clock.get_time()

			# If we've counted down enough...
			if self.time_passed >= self.time_to_countdown + self.countdown_ready_time + self.countdown_go_time:
				# Clean up the arrow before we're done
				self.arrow.destroy()
				# We're done! Call the function that was supplied.
				self.function_to_call()
				self.done = True
			else:
				if self.time_passed >= self.time_to_countdown:
					# If we've counted down enough to show "GO"...
					if self.time_passed >= self.time_to_countdown + self.countdown_ready_time:
						# Existing GO animation code...
						go_time = self.time_passed - (self.time_to_countdown + self.countdown_ready_time)
						
						# Fade in and scale up with bounce effect
						if go_time < self.go_fade_in_speed:
							self.go_alpha = min(255, go_time * 2.55)
							
							# Scale animation with bounce
							if go_time < self.scale_overshoot_time:
								progress = go_time / self.scale_overshoot_time
								self.go_scale = self.go_scale + (self.go_overshoot_scale - self.go_scale) * progress
							elif go_time < self.scale_undershoot_time:
								progress = (go_time - self.scale_overshoot_time) / (self.scale_undershoot_time - self.scale_overshoot_time)
								self.go_scale = self.go_overshoot_scale + (self.go_undershoot_scale - self.go_overshoot_scale) * progress
							elif go_time < self.scale_settle_time:
								progress = (go_time - self.scale_undershoot_time) / (self.scale_settle_time - self.scale_undershoot_time)
								self.go_scale = self.go_undershoot_scale + (self.go_target_scale - self.go_undershoot_scale) * progress
						
						# Stay at full opacity for a moment
						elif go_time < self.go_fade_in_speed + self.go_display_time:
							self.go_alpha = 255
							self.go_scale = self.go_target_scale
						
						# Fade out quickly
						else:
							fade_out_time = go_time - (self.go_fade_in_speed + self.go_display_time)
							self.go_alpha = max(0, 255 - (fade_out_time / 2))
							
						# Update GO text position
						scaled_width = self.countdown_go.get_width() * self.go_scale
						scaled_height = self.countdown_go.get_height() * self.go_scale
						self.countdown_go.x = (settings.SCREEN_WIDTH - scaled_width) / 2
						self.countdown_go.y = (settings.SCREEN_HEIGHT - scaled_height) / 2
						
					else:
						# Handle Ready text animation
						ready_time = self.time_passed - self.time_to_countdown
						
						# Calculate current amplitude based on animation progress, but complete earlier
						settle_duration = self.ready_fade_in_speed + (self.ready_display_time * 0.6)  # Complete at 60% of display time
						animation_progress = min(1.0, ready_time / settle_duration)
						current_amplitude = self.initial_amplitude * (1.0 - animation_progress)
						
						# Update each letter's position and properties
						for letter_data in self.ready_letters:
							# Fade in and scale up smoothly
							if ready_time < self.ready_fade_in_speed:
								self.ready_alpha = min(255, ready_time * 2.55)
								progress = ready_time / self.ready_fade_in_speed
								self.ready_scale = self.ready_scale + (self.ready_target_scale - self.ready_scale) * progress
							
							# Stay at full opacity
							elif ready_time < self.ready_fade_in_speed + self.ready_display_time:
								self.ready_alpha = 255
								self.ready_scale = self.ready_target_scale
							
							# Fade out quickly
							else:
								fade_out_time = ready_time - (self.ready_fade_in_speed + self.ready_display_time)
								self.ready_alpha = max(0, 255 - (fade_out_time / 2))
							
							# Calculate sine wave offset with scaled frequency
							time_factor = ready_time / 1000.0  # Convert to seconds
							sine_offset = current_amplitude * math.sin(2.0 * math.pi * self.sine_frequency * time_factor + letter_data['phase_offset'])
							
							# Update letter position
							letter_data['text'].y = letter_data['base_y'] + sine_offset
							
							# Update letter scale and x position
							letter = letter_data['text']
							original_width = letter.get_width()
							scaled_width = original_width * self.ready_scale
							# Calculate x offset from center point of the letter
							x_offset = (scaled_width - original_width) / 2
							letter.x = letter_data['base_x'] - x_offset

	def draw(self, surface):
		# If we're not done with the countdown...
		if not self.done:
			# Draw the arrow indicator during the entire countdown
			self.arrow.draw(surface)

			# If we've counted down enough to show text...
			if self.time_passed >= self.time_to_countdown:
				# If we've counted down enough to show "GO"...
				if self.time_passed >= self.time_to_countdown + self.countdown_ready_time:
					# Draw the "GO" text with current scale and alpha
					if self.go_alpha > 0:
						# Create temporary surfaces for the scaled text and shadow
						scaled_width = int(self.countdown_go.get_width() * self.go_scale)
						scaled_height = int(self.countdown_go.get_height() * self.go_scale)
						
						# Draw shadow first
						scaled_shadow = pygame.transform.scale(self.countdown_go.shadow_surface, (scaled_width, scaled_height))
						scaled_shadow.set_alpha(self.go_alpha)
						shadow_x = self.countdown_go.x
						shadow_y = self.countdown_go.y + (self.shadow_offset * self.go_scale)
						surface.blit(scaled_shadow, (shadow_x, shadow_y))
						
						# Draw main text
						scaled_surface = pygame.transform.scale(self.countdown_go.surface, (scaled_width, scaled_height))
						scaled_surface.set_alpha(self.go_alpha)
						surface.blit(scaled_surface, (self.countdown_go.x, self.countdown_go.y))
				else:
					# Draw each Ready letter with current scale and alpha
					if self.ready_alpha > 0:
						for letter_data in self.ready_letters:
							letter = letter_data['text']
							# Create temporary surfaces for the scaled text and shadow
							scaled_width = int(letter.get_width() * self.ready_scale)
							scaled_height = int(letter.get_height() * self.ready_scale)
							
							# Draw shadow first
							scaled_shadow = pygame.transform.scale(letter.shadow_surface, (scaled_width, scaled_height))
							scaled_shadow.set_alpha(self.ready_alpha)
							shadow_x = letter.x
							shadow_y = letter.y + (self.shadow_offset * self.ready_scale)
							surface.blit(scaled_shadow, (shadow_x, shadow_y))
							
							# Draw main text
							scaled_surface = pygame.transform.scale(letter.surface, (scaled_width, scaled_height))
							scaled_surface.set_alpha(self.ready_alpha)
							surface.blit(scaled_surface, (letter.x, letter.y))