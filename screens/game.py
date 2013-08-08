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
import objects.blocks.block as block
import objects.blocks.normal as block_normal
import objects.blocks.strong as block_strong
import objects.groups as groups
import gui.textitem as textitem
from settings.settings import *
import settings.graphics as graphics

# Import any needed game screens here.
import screens.gameover as gameover
import screens.countdown as countdown
import screens.pausemenu as pausemenu

class Game:

	# Setup the background images.
	floor_surface = pygame.image.load("res/background/planks/planks_floor.png")
	floor_surface = pygame.transform.scale(floor_surface, (floor_surface.get_width() * GAME_SCALE, floor_surface.get_height() * GAME_SCALE))
	wall_vertical = pygame.image.load("res/background/planks/planks_wall_vertical.png")
	wall_vertical = pygame.transform.scale(wall_vertical, (wall_vertical.get_width() * GAME_SCALE, wall_vertical.get_height() * GAME_SCALE))
	wall_horizontal = pygame.image.load("res/background/planks/planks_wall_horizontal.png")
	wall_horizontal = pygame.transform.scale(wall_horizontal, (wall_horizontal.get_width() * GAME_SCALE, wall_horizontal.get_height() * GAME_SCALE))
	corner_top_left = pygame.image.load("res/background/planks/planks_corner_top_left.png")
	corner_top_left = pygame.transform.scale(corner_top_left, (corner_top_left.get_width() * GAME_SCALE, corner_top_left.get_height() * GAME_SCALE))
	corner_top_right = pygame.image.load("res/background/planks/planks_corner_top_right.png")
	corner_top_right = pygame.transform.scale(corner_top_right, (corner_top_right.get_width() * GAME_SCALE, corner_top_right.get_height() * GAME_SCALE))

	def __init__(self, window_surface, main_clock, player_one_color, player_two_color):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# The next screen to be started when gameloop ends.
		self.next_screen = gameover.GameOver

		# The winner is sent to the gameover screen for display.
		self.winner = None

		# The score is kept to be sent to the gameover screen and also to be kept for "best-of" matches.
		self.score = {}

		# Setup the objects.
		block_normal.convert()
		block_strong.convert()
		paddle.convert()
		ball.convert()
		multiball.convert()

		# Make sure that the background images are converted.
		self.convert_background()

		# Create the left player.
		self.player_left = self.create_player_left(player_one_color)
		
		# Create the right player.
		self.player_right = self.create_player_right(player_two_color)

		# Setup the game world.
		self.setup_gamefield(self.player_left, self.player_right)

		self.gameloop()

	def convert_background(self):
		Game.floor_surface.convert()
		Game.wall_vertical.convert()
		Game.wall_horizontal.convert()
		Game.corner_top_left.convert()
		Game.corner_top_right.convert()

	def create_player_left(self, color):
		name = PLAYER_LEFT_NAME
		key_up = PLAYER_LEFT_KEY_UP
		key_down = PLAYER_LEFT_KEY_DOWN

		player_left = player.Player(name, key_up, key_down, color)

		self.score[player_left] = 0

		return player_left

	def create_player_right(self, color):
		name = PLAYER_RIGHT_NAME
		key_up = PLAYER_RIGHT_KEY_UP
		key_down = PLAYER_RIGHT_KEY_DOWN

		player_right = player.Player(name, key_up, key_down, color)

		self.score[player_right] = 0
		
		return player_right

	def create_ball_left(self):
		for paddle in self.player_left.paddle_group:
			ball.Ball(paddle.x + paddle.width + 1, paddle.y + (paddle.height / 2), 0, self.player_left)

	def create_ball_right(self):
		for paddle in self.player_right.paddle_group:
			ball.Ball(paddle.x - paddle.width - 1, paddle.y + (paddle.height / 2), math.pi, self.player_right)

	def setup_gamefield(self, player_left, player_right):
		distance_to_blocks_from_wall = block.Block.width * 2
		amount_of_strong = 2
		amount_of_weak = 2
		amount_of_rows = (LEVEL_HEIGHT - (block.Block.height * 2)) / block.Block.height

		for x in range(0, amount_of_strong):
			for y in range(0, amount_of_rows):
				block_strong.StrongBlock(LEVEL_X + distance_to_blocks_from_wall + (block.Block.width * x), LEVEL_Y + block.Block.height + (block.Block.height * y), self.player_left)
				temp_block_right = block_strong.StrongBlock(LEVEL_MAX_X - (block.Block.width * 3) - (block.Block.width * x), LEVEL_Y + block.Block.height + (block.Block.height * y), self.player_right)
				temp_block_right.image = pygame.transform.flip(temp_block_right.image, True, False)
		for x in range(0, amount_of_weak):
			for y in range(0, amount_of_rows):
				block_normal.NormalBlock(LEVEL_X + (distance_to_blocks_from_wall * amount_of_strong) + (block.Block.width * x), LEVEL_Y + block.Block.height + (block.Block.height * y), self.player_left)
				temp_block_right = block_normal.NormalBlock(LEVEL_MAX_X - (block.Block.width * 5) - (block.Block.width * x), LEVEL_Y + block.Block.height + (block.Block.height * y), self.player_right)
				temp_block_right.image = pygame.transform.flip(temp_block_right.image, True, False)

		left_paddle_x = LEVEL_X + (amount_of_strong * block.Block.width) + (amount_of_weak * block.Block.width) + (paddle.Paddle.width * 4)
		left_paddle_y = (LEVEL_Y + (LEVEL_MAX_Y- paddle.Paddle.height)) / 2.0
		player_left.paddle_group.add(paddle.Paddle(left_paddle_x, left_paddle_y, player_left))

		right_paddle_x = LEVEL_MAX_X - (amount_of_strong * paddle.Paddle.width) - (amount_of_weak * paddle.Paddle.width) - (paddle.Paddle.width * 5)
		right_paddle_y = (LEVEL_Y + (LEVEL_MAX_Y- paddle.Paddle.height)) / 2.0
		paddle_right = paddle.Paddle(right_paddle_x, right_paddle_y, player_right)
		paddle_right.image = pygame.transform.flip(paddle_right.image, True, False)
		player_right.paddle_group.add(paddle_right)

	def gameloop(self):
		# We start a countdown before the game starts.
		countdown_screen = countdown.Countdown(self.main_clock, self.start_game)
		self.update(countdown_screen)
		self.draw()	

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
					elif event.type == KEYDOWN and event.key == K_l:
						debug.create_ball_left(self.player_left)
					elif event.type == KEYDOWN and event.key == K_r:
						debug.create_ball_right(self.player_right)
					elif event.type == KEYDOWN and event.key == K_p:
						debug.create_powerup()

			# Win detection: for now just go back to previous screen if the game is over.
			if len(self.player_left.block_group) == 0:
				self.winner = self.player_left
				self.done = True
			elif len(self.player_right.block_group) == 0:
				self.winner = self.player_right
				self.done = True

			self.update(countdown_screen)

			self.draw()
			
			countdown_screen.update_and_draw(self.window_surface)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(MAX_FPS)

		self.on_exit()

	def start_game(self):
		self.create_ball_left()
		self.create_ball_right()

	def update(self, countdown_screen):
		# If debug mode is enabled, allow certain commands. This is all done in the debug module.
		if DEBUG_MODE and countdown_screen.done:
			debug.update(self.player_left, self.player_right)

		# Update the balls.
		groups.Groups.ball_group.update(self.main_clock)
		
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
		# Begin a frame by blitting the background to the game_surface.
		self.window_surface.fill(BACKGROUND_COLOR)
		self.window_surface.blit(Game.floor_surface, (LEVEL_X, LEVEL_Y))

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

		# Draw the background walls and overlying area.
		self.draw_background(self.window_surface)

		if DEBUG_MODE:
			# Display various debug information.
			debug.Debug.display(self.window_surface, self.main_clock)

	def draw_background(self, surface):
		surface.blit(Game.wall_horizontal, (LEVEL_X, LEVEL_Y - (4 * GAME_SCALE)))
		surface.blit(Game.wall_horizontal, (LEVEL_X, LEVEL_MAX_Y))
		surface.blit(Game.wall_vertical, (LEVEL_X - (4 * GAME_SCALE), LEVEL_Y))
		surface.blit(Game.wall_vertical, (LEVEL_MAX_X, LEVEL_Y))
		surface.blit(Game.corner_top_left, (LEVEL_X - (4 * GAME_SCALE), LEVEL_Y - (4 * GAME_SCALE)))
		surface.blit(Game.corner_top_left, (LEVEL_MAX_X, LEVEL_MAX_Y))
		surface.blit(Game.corner_top_right, (LEVEL_MAX_X, LEVEL_Y - (4 * GAME_SCALE)))
		surface.blit(Game.corner_top_right, (LEVEL_X - (4 * GAME_SCALE), LEVEL_MAX_Y))

	def on_exit(self):
		# Gameloop is over, so we clear all the groups of their contents.
		groups.empty()

		if self.next_screen == None:
			pygame.quit()
			sys.exit()
		elif self.next_screen == gameover.GameOver:
			self.score[self.winner] = self.score[self.winner] + 1
			self.next_screen(self.window_surface, self.main_clock, self.player_left.color, self.player_right.color, self.winner, self.score)
		else:
			self.next_screen(self.window_surface, self.main_clock)