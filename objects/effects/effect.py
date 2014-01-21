__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import settings.settings as settings

"""

This is the base class of all effects in the game. It takes care of alot of things, like updating the position of the effect
and destroying the effect when the duration runs out. It also provides a few overridable methods.

"""

class Effect(pygame.sprite.Sprite):

	def __init__(self, parent, duration):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Store the parent.
		self.parent = parent

		# We store the amount of time passed. When time passed is greater than timeout time, the parent is killed.
		self.time_passed = 0

		# Store the duration. The effect will be killed when time_passed is greater than duration.
		self.duration = duration
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(self.parent.rect.x, self.parent.rect.y, self.parent.rect.width, self.parent.rect.height)

		# Image is used to draw the effect. If image is None, it will not be drawn.
		self.image = None

		# We store self in the parents effect_group.
		self.parent.effect_group.add(self)

		# If we want, we can connect powerups to this effect that is killed when this effect is killed. Primarily used to 
		# connect the powerups that are displayed on the player.
		self.displayed_powerups = []
		
		# Store self in the main effect_group.
		groups.Groups.effect_group.add(self)

	def on_hit_ball(self, hit_ball):
		pass

	def on_hit_block(self, hit_block):
		pass

	def on_hit_paddle(self, hit_paddle):
		pass
		
	def on_hit_wall(self):
		pass

	def update(self, main_clock):
		# Update the position of this effect, so it follows its parent.
		self.rect.x = self.parent.rect.x + ((self.parent.rect.width - self.rect.width) / 2)
		self.rect.y = self.parent.rect.y + ((self.parent.rect.height - self.rect.height) / 2)

		self.time_passed += main_clock.get_time()
		if self.time_passed >= self.duration:
			# When the duration runs out, we destroy ourselves.
			self.destroy()

	def draw(self, surface):
		# If the image exists, we blit it to the surface.
		if not self.image == None:
			surface.blit(self.image, self.rect)

	def destroy(self):
		self.kill()

		# Destroy all powerups that are connected to this effect.
		for powerup in self.displayed_powerups:
			powerup.destroy(False)

		self.on_kill()

	def on_kill(self):
		pass