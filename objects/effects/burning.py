__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import objects.blocks.block as block
import objects.groups as groups
import objects.effects.effect as effect
import objects.particle as particle
import settings.settings as settings

"""

This is an effect that is applied by the Fire powerup. When applied to balls, those balls will spread the effect
to enemy blocks (that is, enemies to the parent of the ball).

When this effect is applied to a block, that block will take some damage per second. This only happens to entities
that have the "health" attribute.

This effect plays a sound effect when it is created.

"""

class Burning(effect.Effect):

    # Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
    image = pygame.image.load("res/effect/burning.png")

    # Initialize the mixer (so we can load a sound) and load the sound effect.
    pygame.mixer.init(44100, -16, 2, 2048)
    sound_effect = pygame.mixer.Sound("res/sounds/burning.ogg")

    # Standard values. These will be used unless any other values are specified per instance of this class.
    width = image.get_width()
    height = image.get_height()
    damage_per_second = 2.0
    particle_spawn_rate = 75
    particle_least_spawn_amount = 3
    particle_maximum_spawn_amount = 5
    duration = 10000
    block_duration = 5000
    spread_check_rate = 500  # Check for spread every 0.5 seconds
    spread_range = 15  # Reduced range - blocks need to be closer to spread
    spread_duration_factor = 0.8  # Each spread reduces duration by 20%
    spread_chance = 0.25  # 25% chance to spread to each eligible neighbor

    # Scale image.
    image = pygame.transform.scale(image, (width, height))

    def __init__(self, parent, duration = None):
        # We check if a duration has been given.
        if not duration == None:
            # We start by calling the superconstructor with the given duration value.
            effect.Effect.__init__(self, parent, duration)
        else:
            # We start by calling the superconstructor with the standard duration value.
            effect.Effect.__init__(self, parent, Burning.duration)

        # When this reaches particle_spawn_rate, a particle is spawned.
        self.particle_spawn_time = 0

        # When this reaches spread_check_rate, we check for spreading
        self.spread_check_time = 0

        # Play the sound effect.
        sound = Burning.sound_effect.play()
        if not sound is None:
            sound.set_volume(settings.SOUND_VOLUME)

        # If the parent is subclass of block, show an effect on top of the block.
        if issubclass(self.parent.__class__, block.Block):
            # Create the image attribute that is drawn to the surface.
            self.image = Burning.image.copy()

            # Set the rects width and height to the standard values.
            self.rect.width = Burning.width
            self.rect.height = Burning.height

    def find_neighboring_blocks(self):
        """Find blocks that are close to the current burning block."""
        if not issubclass(self.parent.__class__, block.Block):
            return []
        
        neighbors = []
        parent_center = (self.parent.rect.centerx, self.parent.rect.centery)
        
        # Check all blocks in the game
        for block_sprite in groups.Groups.block_group:
            if block_sprite != self.parent:  # Don't include self
                block_center = (block_sprite.rect.centerx, block_sprite.rect.centery)
                # Calculate distance between block centers
                distance = math.sqrt(
                    (block_center[0] - parent_center[0]) ** 2 + 
                    (block_center[1] - parent_center[1]) ** 2
                )
                if distance <= Burning.spread_range:
                    neighbors.append(block_sprite)
        
        return neighbors

    def spread_to_neighbors(self):
        """Attempt to spread burning effect to neighboring blocks."""   
        if not issubclass(self.parent.__class__, block.Block):
            return
            
        neighbors = self.find_neighboring_blocks()
        for neighbor in neighbors:
            # Only spread to blocks that aren't already burning and pass the random check
            has_burning = any(isinstance(effect, Burning) for effect in neighbor.effect_group)
            if not has_burning and random.random() < Burning.spread_chance:
                # Calculate new duration based on current duration
                new_duration = int(self.duration * Burning.spread_duration_factor)
                if new_duration >= 1000:  # Only spread if duration would be at least 1 second
                    Burning(neighbor, new_duration)

    def on_hit_block(self, hit_block):
        # Spread the effect to any hit blocks not owned by the parents owner.
        if self.parent.owner == self.real_owner:
            if not self.parent.owner == hit_block.owner:
                # Apply the burning effect
                burning_effect = Burning(hit_block, Burning.block_duration)
                # Immediately try to spread to neighbors in case the block is destroyed
                burning_effect.spread_to_neighbors()

    def update(self, main_clock):
        # We make sure to call the supermethod.
        effect.Effect.update(self, main_clock)

        if self.parent.owner == self.real_owner:
            # If the parent has health, deal damage to it.
            if hasattr(self.parent, "health"):
                self.parent.hurt(Burning.damage_per_second * main_clock.delta_time)

            # Check for spreading to neighbors
            if issubclass(self.parent.__class__, block.Block):
                self.spread_check_time += main_clock.get_time()
                if self.spread_check_time >= Burning.spread_check_rate:
                    self.spread_check_time = 0
                    self.spread_to_neighbors()

            # If it's time, spawn particles.
            self.particle_spawn_time += main_clock.get_time()
            if self.particle_spawn_time >= Burning.particle_spawn_rate:
                # Reset the particle spawn time.
                self.particle_spawn_time = 0

                # Spawn a random amount of particles.
                for _ in range(0, random.randrange(Burning.particle_least_spawn_amount, Burning.particle_maximum_spawn_amount)):
                    width = random.uniform(self.parent.rect.width / 4.0, self.parent.rect.width / 2.0)
                    if hasattr(self.parent, "angle"):
                        angle = self.parent.angle + random.uniform(-math.pi / 5.0, math.pi / 5.0)
                    else:
                        angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(0.5 * settings.GAME_FPS, 0.9 * settings.GAME_FPS)
                    retardation = speed / 24.0
                    if random.random() > 0.1:
                        color = pygame.Color(random.randint(200, 255), random.randint(0, 255), 0)
                    else:
                        a_color = random.randint(0, 255)
                        color = pygame.Color(a_color, a_color, a_color)
                    particle.Particle(self.parent.x + self.parent.rect.width / 2, self.parent.y + self.parent.rect.height / 2, width, width, angle, speed, retardation, color, 5 * settings.GAME_FPS)
