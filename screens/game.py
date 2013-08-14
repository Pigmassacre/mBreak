__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import math
import random
import other.debug as debug
import objects.ball as ball
import objects.paddle as paddle
import objects.player as player
import objects.multiball as multiball
import objects.doublespeed as doublespeed
import objects.speed as speed
import objects.blocks.block as block
import objects.blocks.normal as block_normal
import objects.blocks.strong as block_strong
import objects.groups as groups
import gui.textitem as textitem
import settings.settings as settings
import settings.graphics as graphics
import screens.background as background
import screens.level as level

# Import any needed game screens here.
import screens.gameover as gameover
import screens.matchover as matchover
import screens.countdown as countdown
import screens.pausemenu as pausemenu

class Game:

	def __init__(self, window_surface, main_clock, player_one, player_two, number_of_rounds, score, number_of_rounds_done = 0):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# The next screen to be started when gameloop ends.
		self.next_screen = gameover.GameOver

		# Keep track of the number of rounds. Gameloop will "run-its-course" this many times.
		self.number_of_rounds = number_of_rounds

		# Keep track of the number of rounds we've done so far.
		self.number_of_rounds_done = number_of_rounds_done

		# The score is kept to be sent to the gameover screen and also to be kept for "best-of" matches.
		self.score = score

		# Convert all the objects to a more efficient format. We do this here as a "preloading" sort of measure.
		block_normal.convert()
		block_strong.convert()
		paddle.convert()
		ball.convert()
		multiball.convert()
		doublespeed.convert()

		# Create and store the background. For now, we only have one background so we load that. In the future, the system supports
		# drawing any sort of background as long as those graphics are setup in the same way as "planks" are.
		self.game_background = background.Background("planks")

		# Store player one.
		self.player_one = player_one
		
		# Store player two.
		self.player_two = player_two

		# Create and store the level.
		self.game_level = level.Level(self.player_one, self.player_two, 2, 2, 0)

		# Creat the score texts.
		item_side_padding = textitem.TextItem.font_size

		self.player_one_score_text = textitem.TextItem(str(self.score[self.player_one]), pygame.Color(255, 255, 255))
		self.player_one_score_text.set_size(27 * settings.GAME_SCALE)
		self.player_one_score_text.x = item_side_padding
		self.player_one_score_text.y = (settings.SCREEN_HEIGHT - self.player_one_score_text.get_height()) / 2

		self.player_two_score_text = textitem.TextItem(str(self.score[self.player_two]), pygame.Color(255, 255, 255))
		self.player_two_score_text.set_size(27 * settings.GAME_SCALE)
		self.player_two_score_text.x = settings.SCREEN_WIDTH - item_side_padding - self.player_two_score_text.get_width()
		self.player_two_score_text.y = (settings.SCREEN_HEIGHT - self.player_one_score_text.get_height()) / 2

		# And finally, start the gameloop!
		self.gameloop()

	def create_ball_left(self):
		for paddle in self.player_one.paddle_group:
			ball.Ball(paddle.x + paddle.width + 1, paddle.y + (paddle.height / 2), 0, self.player_one)

	def create_ball_right(self):
		for paddle in self.player_two.paddle_group:
			ball.Ball(paddle.x - paddle.width - 1, paddle.y + (paddle.height / 2), math.pi, self.player_two)

	def gameloop(self):
		# We start a countdown before the game starts. WHen the countdown finishes, it calls start_game().
		countdown_screen = countdown.Countdown(self.main_clock, self.start_game)

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

			# Win detection: for now just go back to previous screen if the game is over.
			if len(self.player_one.block_group) == 0:
				self.score[self.player_two] = self.score[self.player_two] + 1
				self.done = True
			elif len(self.player_two.block_group) == 0:
				self.score[self.player_one] = self.score[self.player_one] + 1
				self.done = True

			self.update(countdown_screen)

			self.draw()
			
			# Only update the countdown screen if it is not finished.
			if not countdown_screen.done:
				countdown_screen.update_and_draw(self.window_surface)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(settings.MAX_FPS)

		self.on_exit()

	def start_game(self):
		self.create_ball_left()
		self.create_ball_right()

	def update(self, countdown_screen):
		# If debug mode is enabled, allow certain commands. This is all done in the debug module.
		if settings.DEBUG_MODE and countdown_screen.done:
			debug.update(self.player_one, self.player_two)

		# Update the balls.
		groups.Groups.ball_group.update(self.main_clock)

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
		
		# Update the players.
		groups.Groups.player_group.update()
		
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

		# Draw the particles.
		if graphics.PARTICLES:
			for particle in groups.Groups.particle_group:
				self.window_surface.fill(particle.color, particle.rect)

		# Draw the traces.
		if graphics.TRACES:
			for trace in groups.Groups.trace_group:
				trace.blit_to(self.window_surface)

		# Draw the balls.
		groups.Groups.ball_group.draw(self.window_surface)

		# Draw the effects.
		for effect in groups.Groups.effect_group:
			effect.draw(self.window_surface)

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