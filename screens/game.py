__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import math
import random
import other.debug as debug
import objects.ball as ball
import objects.paddle as paddle
import objects.player as player
import objects.powerups.powerup as powerup
import objects.powerups.multiball as multiball
import objects.powerups.doublespeed as doublespeed
import objects.powerups.electricity as electricity
import objects.powerups.fire as fire
import objects.powerups.frost as frost
import objects.effects.speed as speed
import objects.effects.flash as flash
import objects.blocks.block as block
import objects.blocks.normal as block_normal
import objects.blocks.strong as block_strong
import objects.blocks.weak as block_weak
import objects.groups as groups
import gui.textitem as textitem
import settings.settings as settings
import settings.graphics as graphics
import screens.background as background
import screens.level as level

# We import any needed game screens here.
import screens.gameover as gameover
import screens.matchover as matchover
import screens.countdown as countdown
import screens.pausemenu as pausemenu

"""

This is the screen where the actual gameplay takes place. It uses the background module to draw the background, and the
level module to create the blocks and paddles.

It takes care of updating and drawing all the objects in the game, checking for the winner, spawning powerups and stuff like that.
It also check for the ESCAPE key (for the pause menu) and the debug keys (for the debug functions).

For each player, a list of all their currently active powerups are displayed in the top-left and bottom-right corner of the game, respectively.
(The player class handles this, however.)

"""

class Game:

	def __init__(self, window_surface, main_clock, player_one, player_two, number_of_rounds, score, number_of_rounds_done = 0):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# The next screen to be started when gameloop ends.
		self.next_screen = gameover.GameOver

		# Keep track of the number of rounds.
		self.number_of_rounds = number_of_rounds

		# Keep track of the number of rounds we've done so far.
		self.number_of_rounds_done = number_of_rounds_done

		# The score is kept to be sent to the gameover screen and also to be kept for "best-of" matches.
		self.score = score

		# Convert all the objects to a more efficient format. We do this here as a "preloading" sort of measure.
		block_normal.convert()
		block_strong.convert()
		block_weak.convert()
		paddle.convert()
		ball.convert()
		multiball.convert()
		doublespeed.convert()
		fire.convert()
		frost.convert()
		electricity.convert()

		# Create and store the background. For now, we only have one background so we load that. In the future, the system supports
		# drawing any sort of background as long as those graphics are setup in the same way as "planks" are.
		self.game_background = background.Background("planks")

		# Store player one.
		self.player_one = player_one
		
		# Store player two.
		self.player_two = player_two

		# Create and store the level.
		self.game_level = level.Level(self.player_one, self.player_two, 1, 1, 2)

		# The list of available powerups to spawn.
		self.powerup_list = [multiball.Multiball, doublespeed.DoubleSpeed, fire.Fire, frost.Frost, electricity.Electricity]

		# The rate at which powerups will perhaps be spawned.
		self.powerup_spawn_rate = 6000

		# After this amount of time has passed, the powerup spawn chance will be increased.
		self.powerup_increase_spawn_rate = 4000

		# This is the amount that all the spawn chances will increase by every powerup_increase_spawn_rate.
		self.powerup_spawn_chance_increase = 0.03

		# The chance that a powerup will spawn when it should spawn.
		self.powerup_spawn_chance = 0.3

		# The chance that another powerup will spawn if a powerup actually spawns.
		self.powerup_second_spawn_chance = 0.2

		# The chance that a THIRD powerup will spawn if a second powerup actually spawns.
		self.powerup_third_spawn_chance = 0.1

		# If there is already a doublespeed powerup on the gamefield, this is the chance that any further will spawn.
		self.powerup_second_speed_spawn_chance = 0.1

		# Create the score texts. These are only displayed when the amount of rounds is greater than 0.
		item_side_padding = textitem.TextItem.font_size

		# This is to more correctly align the two textitems so they are all equally far away from their respective sides.
		# Magic value, I know, but without this the textitems look misaligned.
		left_side_extra_padding = 3 * settings.GAME_SCALE

		self.player_one_score_text = textitem.TextItem(str(self.score[self.player_one]), pygame.Color(255, 255, 255))
		self.player_one_score_text.set_size(27 * settings.GAME_SCALE)
		self.player_one_score_text.x = item_side_padding + left_side_extra_padding
		self.player_one_score_text.y = (settings.SCREEN_HEIGHT - self.player_one_score_text.get_height()) / 2

		self.player_two_score_text = textitem.TextItem(str(self.score[self.player_two]), pygame.Color(255, 255, 255))
		self.player_two_score_text.set_size(27 * settings.GAME_SCALE)
		self.player_two_score_text.x = settings.SCREEN_WIDTH - item_side_padding - self.player_two_score_text.get_width()
		self.player_two_score_text.y = (settings.SCREEN_HEIGHT - self.player_two_score_text.get_height()) / 2

		# We setup and play music.
		self.setup_music()

		# And finally, start the gameloop!
		self.gameloop()

	def setup_music(self):
		if not pygame.mixer.music.get_busy():
			# We only care about loading and playing the music if it isn't already playing.
			pygame.mixer.music.load(settings.GAME_MUSIC)
			pygame.mixer.music.play(-1)

	def gameloop(self):
		# We start a countdown before the game starts. When the countdown finishes, it calls start_game.
		countdown_screen = countdown.Countdown(self.main_clock, self.start_game)

		# When this reaches powerup_spawn_rate, a powerup has a chance to spawn.
		self.powerup_spawn_time = 0

		# When this reaches powerup_increase_spawn_rate, the chance for powerups to spawn will be increased.
		self.powerup_increase_spawn_time = 0

		self.done = False
		while not self.done:
			for event in pygame.event.get():
				if event.type == QUIT:
					# If the window is closed, the game is shut down.
					sys.exit()
					pygame.quit()
				if countdown_screen.done:
					if event.type == KEYDOWN and event.key == K_ESCAPE:
						pausemenu.PauseMenu(self.window_surface, self.main_clock)
					if settings.DEBUG_MODE:
						if event.type == KEYDOWN and event.key == K_l:
							debug.create_ball_left(self.player_one)
						elif event.type == KEYDOWN and event.key == K_r:
							debug.create_ball_right(self.player_two)
						elif event.type == KEYDOWN and event.key == K_p:
							debug.create_powerup()

			self.check_for_winner()

			self.try_to_spawn_powerups()

			self.update(countdown_screen)

			self.draw()
			
			# Only update the countdown screen if it is not finished.
			if not countdown_screen.done:
				countdown_screen.update_and_draw(self.window_surface)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(graphics.MAX_FPS)

		# The gameloop is over, so call the exit method.
		self.on_exit()

	def check_for_winner(self):
		# Detect if a player has won or not.
		if len(self.player_one.block_group) == 0:
			self.score[self.player_two] = self.score[self.player_two] + 1
			self.done = True
		elif len(self.player_two.block_group) == 0:
			self.score[self.player_one] = self.score[self.player_one] + 1
			self.done = True

	def try_to_spawn_powerups(self):
		# If it's time, all powerup spawn chances will increase by a certain amount.
		self.powerup_increase_spawn_time += self.main_clock.get_time()
		if self.powerup_increase_spawn_time >= self.powerup_increase_spawn_rate:
			# It's time, so increase all spawn chances.
			self.powerup_spawn_chance += self.powerup_spawn_chance_increase
			self.powerup_second_spawn_chance += self.powerup_spawn_chance_increase
			self.powerup_third_spawn_chance += self.powerup_spawn_chance_increase

			# The second speed chance increases slighty slower.
			self.powerup_second_speed_spawn_chance += self.powerup_spawn_chance_increase / 3.0

			# Finally, reset the timer.
			self.powerup_increase_spawn_time = 0

		# Check if it's time to try to spawn a powerup.
		self.powerup_spawn_time += self.main_clock.get_time()
		if self.powerup_spawn_time >= self.powerup_spawn_rate:
			# Check if the spawn will be successful.
			if random.uniform(0, 1) <= self.powerup_spawn_chance:
				self.create_powerup()

				# Check if a second powerup should spawn.
				if random.uniform(0, 1) <= self.powerup_second_spawn_chance:
					self.create_powerup()

					# Check if a third powerup should spawn.
					if random.uniform(0, 1) <= self.powerup_third_spawn_chance:
						self.create_powerup()

				# Finally, reset the powerup spawn timer.
				self.powerup_spawn_time = 0

	def create_powerup(self):
		# Pick a random position in the middle of the level.
		x = random.uniform(settings.LEVEL_X + (settings.LEVEL_WIDTH / 4), settings.LEVEL_X + (3 * (settings.LEVEL_WIDTH / 4)))
		y = random.uniform(settings.LEVEL_Y, settings.LEVEL_MAX_Y - powerup.Powerup.height)

		# Store what should spawn temporarily.
		powerup_to_spawn = random.choice(self.powerup_list)

		# If what should've spawned is doublespeed, check if we're allowed to spawn that.
		if powerup_to_spawn == doublespeed.DoubleSpeed:
			# Go through all the powerups in the level and...
			for a_powerup in groups.Groups.powerup_group:
				# Check if there is already a speed powerup on the field.
				if a_powerup.__class__ == doublespeed.DoubleSpeed:
					# If there is, check if we should allow it to spawn.
					if random.uniform(0, 1) <= self.powerup_second_speed_spawn_chance:
						# Ok, it should spawn, so spawn it.
						return powerup_to_spawn(x, y)
					else:
						# It shouldn't spawn, so let's generate another powerup_to_spawn that isn't doublespeed and then break the loop.
						powerup_to_spawn = random.choice(filter(lambda x: x != doublespeed.DoubleSpeed, self.powerup_list))
						break
		
		# If we got this far, we just spawn that powerup.
		return powerup_to_spawn(x, y)

	def start_game(self):
		# When the game starts, we spawn balls for both players.
		self.create_ball_left()
		self.create_ball_right()

	def create_ball_left(self):
		# Creates a ball for the left player.
		for paddle in self.player_one.paddle_group:
			ball.Ball(paddle.x + paddle.width + 1, paddle.y + (paddle.height / 2), -math.pi / 8, self.player_one)

	def create_ball_right(self):
		# Creates a ball for the right player.
		for paddle in self.player_two.paddle_group:
			ball.Ball(paddle.x - paddle.width - 1, paddle.y + (paddle.height / 2), math.pi / 8, self.player_two)

	def update(self, countdown_screen):
		# If debug mode is enabled, allow certain commands. This is all done in the debug module.
		if settings.DEBUG_MODE and countdown_screen.done:
			debug.update(self.player_one, self.player_two)

		# Update the players.
		groups.Groups.player_group.update()

		# Update the balls.
		groups.Groups.ball_group.update(self.main_clock)

		# Update the blocks.
		groups.Groups.block_group.update()

		# Update the dummy objects.
		groups.Groups.dummy_group.update(self.main_clock)

		# Update the powerups.
		groups.Groups.powerup_group.update(self.main_clock)

		# Update the effects.
		# First, we update the speed effects.
		for effect in groups.Groups.effect_group:
			if effect.__class__ == speed.Speed:
				effect.update(self.main_clock)
		
		# Then, we update every other effect. Because the speed effect moves the ball, if we update speed after any other effect we might get
		# some wrong looking graphics (things will not line up with the balls with the speed effect).
		for effect in groups.Groups.effect_group:
			if not effect.__class__ == speed.Speed:
				effect.update(self.main_clock)
		
		# Update the particles.
		if graphics.PARTICLES:
			groups.Groups.particle_group.update()

		# Update the traces.
		if graphics.TRACES:
			groups.Groups.trace_group.update()
		
		# Update the shadows.
		if graphics.SHADOWS:
			groups.Groups.shadow_group.update(self.main_clock)

	def draw(self):
		# Begin a frame by blitting the background to the window_surface.
		self.window_surface.fill(settings.BACKGROUND_COLOR)
		if graphics.BACKGROUND:
			self.window_surface.blit(self.game_background.floor_surface, (settings.LEVEL_X, settings.LEVEL_Y))

		# Draw the shadows.
		if graphics.SHADOWS:
			for shadow in groups.Groups.shadow_group:
				shadow.blit_to(self.window_surface)

		# Draw the blocks.
		groups.Groups.block_group.draw(self.window_surface)

		# Draw the paddles.
		groups.Groups.paddle_group.draw(self.window_surface)

		# Draw the powerups.
		groups.Groups.powerup_group.draw(self.window_surface)

		# Draw the traces.
		if graphics.TRACES:
			for trace in groups.Groups.trace_group:
				trace.blit_to(self.window_surface)

		# Draw the balls.
		groups.Groups.ball_group.draw(self.window_surface)

		# Draw the effects for which we don't care which order they are drawn in.
		for effect in groups.Groups.effect_group:
			if not effect.__class__ == flash.Flash:
				effect.draw(self.window_surface)

		# Draw the flash effects.
		for effect in groups.Groups.effect_group:
			if effect.__class__ == flash.Flash:
				effect.draw(self.window_surface)

		# Draw the particles.
		if graphics.PARTICLES:
			for particle in groups.Groups.particle_group:
				self.window_surface.fill(particle.color, particle.rect)

		# Draw the background walls and overlying area.	
		self.game_background.draw(self.window_surface)

		# Draw the scores if we're playing more than one round.
		if self.number_of_rounds > 1:
			self.player_one_score_text.draw(self.window_surface)
			self.player_two_score_text.draw(self.window_surface)

		if settings.DEBUG_MODE:
			# Display various debug information.
			debug.Debug.display(self.window_surface, self.main_clock)

	def on_exit(self):
		# We have to make sure to empty the players own groups, because their groups are not emptied by groups.empty_after_round().
		self.player_one.empty_groups()
		self.player_two.empty_groups()

		# We decrement the number of rounds by 1 because we've just played one round.
		self.number_of_rounds_done += 1

		if (self.score[self.player_one] > self.number_of_rounds / 2 or 
			self.score[self.player_two] > self.number_of_rounds / 2 or 
			self.number_of_rounds_done == self.number_of_rounds):
			# If we've played the correct amount of rounds, or there's no point in continuing further, we set next screen to GameOver.
			self.next_screen = gameover.GameOver
		else:
			# Else, continue to MatchOver screen.
			self.next_screen = matchover.MatchOver

		if self.next_screen == None:
			pygame.quit()
			sys.exit()
		elif self.next_screen == matchover.MatchOver:
			# The game is over, but we're restarting Game so we empty all the groups but the groups that contain the players.
			groups.empty_after_round()
			self.next_screen(self.window_surface, self.main_clock, self.player_one, self.player_two, self.number_of_rounds, self.score, self.number_of_rounds_done)
		elif self.next_screen == gameover.GameOver:
			# The game is over, but we're allowing for a rematch so we empty all the groups but the groups that contain the players.
			groups.empty_after_round()
			self.next_screen(self.window_surface, self.main_clock, self.player_one, self.player_two, self.number_of_rounds, self.score)
		else:
			# The game is over so we empty all the groups.
			groups.empty_all()
			self.next_screen(self.window_surface, self.main_clock)