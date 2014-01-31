__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import objects.paddle as paddle
import objects.blocks.block as block
import objects.blocks.normal as normalblock
import objects.blocks.strong as strongblock
import objects.blocks.weak as weakblock
import settings.settings as settings

"""

This is the class that is used to populate the game with blocks and paddles.

The "level" generated by this class can be changed by passing different values to the amount_* parameters.

"""

class Level:
	
	def __init__(self, player_one, player_two, amount_of_strong, amount_of_normal, amount_of_weak):
		# These variables are used to construct the level out of blocks.
		distance_to_blocks_from_left_wall = block.Block.width * 2
		distance_to_blocks_from_right_wall = distance_to_blocks_from_left_wall + block.Block.width
		self.amount_of_strong = amount_of_strong
		self.amount_of_normal = amount_of_normal
		self.amount_of_weak = amount_of_weak
		amount_of_rows = settings.LEVEL_HEIGHT / block.Block.height #  - (block.Block.height * 2)

		# Create and place the given amount of strong blocks.
		for x in range(0, amount_of_strong):
			for y in range(0, amount_of_rows):
				strongblock.StrongBlock(settings.LEVEL_X + distance_to_blocks_from_left_wall + (block.Block.width * x), settings.LEVEL_Y + (block.Block.height * y), player_one)
				temp_block_right = strongblock.StrongBlock(settings.LEVEL_MAX_X - distance_to_blocks_from_right_wall - (block.Block.width * x), settings.LEVEL_Y + (block.Block.height * y), player_two)
				temp_block_right.image = pygame.transform.flip(temp_block_right.image, True, False)

		# Create and place the given amount of normal blocks.
		for x in range(0, amount_of_normal):
			for y in range(0, amount_of_rows):
				normalblock.NormalBlock(settings.LEVEL_X + distance_to_blocks_from_left_wall + (block.Block.width * amount_of_strong) + (block.Block.width * x), settings.LEVEL_Y + (block.Block.height * y), player_one)
				temp_block_right = normalblock.NormalBlock(settings.LEVEL_MAX_X - distance_to_blocks_from_right_wall - (block.Block.width * amount_of_strong) - (block.Block.width * x), settings.LEVEL_Y + (block.Block.height * y), player_two)
				temp_block_right.image = pygame.transform.flip(temp_block_right.image, True, False)

		# Create and place the given amount of weak blocks.
		for x in range(0, amount_of_weak):
			for y in range(0, amount_of_rows):
				weakblock.WeakBlock(settings.LEVEL_X + distance_to_blocks_from_left_wall + (block.Block.width * amount_of_strong) + (block.Block.width * amount_of_normal) + (block.Block.width * x), settings.LEVEL_Y + (block.Block.height * y), player_one)
				temp_block_right = weakblock.WeakBlock(settings.LEVEL_MAX_X - distance_to_blocks_from_right_wall - (block.Block.width * amount_of_strong) - (block.Block.width * amount_of_normal) - (block.Block.width * x), settings.LEVEL_Y + (block.Block.height * y), player_two)
				temp_block_right.image = pygame.transform.flip(temp_block_right.image, True, False)

		# Create a paddle for player one.
		left_paddle_x = settings.LEVEL_X + (amount_of_strong * block.Block.width) + (amount_of_normal * block.Block.width) + (amount_of_weak * block.Block.width) + (paddle.Paddle.width * 3)
		left_paddle_y = (settings.LEVEL_Y + (settings.LEVEL_MAX_Y- paddle.Paddle.height)) / 2.0
		player_one.paddle_group.add(paddle.Paddle(left_paddle_x, left_paddle_y, player_one))

		# Create a paddle for player two.
		right_paddle_x = settings.LEVEL_MAX_X - (amount_of_strong * block.Block.width) - (amount_of_normal * block.Block.width) - (amount_of_weak * block.Block.width) - (paddle.Paddle.width * 4)
		right_paddle_y = (settings.LEVEL_Y + (settings.LEVEL_MAX_Y- paddle.Paddle.height)) / 2.0
		player_two.paddle_group.add(paddle.Paddle(right_paddle_x, right_paddle_y, player_two))
		