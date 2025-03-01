__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import objects.groups as groups
import objects.effects.effect as effect
import objects.particle as particle
import settings.settings as settings

"""

This is the GravitationalPull effect. Balls that have this effect will have their trajectory
affected by a gravitational pull in a random direction, making their movement less predictable.

"""

class GravitationalPull(effect.Effect):

    # Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
    image = pygame.image.load("res/effect/timeout.png")  # Reusing timeout image for now

    # Initialize the mixer (so we can load a sound) and load the sound effect.
    pygame.mixer.init(44100, -16, 2, 2048)
    sound_effect = pygame.mixer.Sound("res/sounds/powerup1.ogg")  # Reusing a powerup sound for now

    # Standard values. These will be used unless any other values are specified per instance of this class.
    width = image.get_width()
    height = image.get_height()
    duration = 8000
    particle_spawn_rate = 600
    particle_spawn_amount = 2

    # Gravity effect values
    gravity_strength = 0.05

    # Scale image.
    image = pygame.transform.scale(image, (width, height))

    def __init__(self, parent, duration = None):
        # We check if a duration has been given.
        if not duration == None:
            # We start by calling the superconstructor with the given duration value.
            effect.Effect.__init__(self, parent, duration)
        else:
            # We start by calling the superconstructor with the standard duration value.
            effect.Effect.__init__(self, parent, GravitationalPull.duration)
        
        # When this reaches particle_spawn_rate, a particle is spawned.
        self.particle_spawn_time = 0

        # Set a random gravity direction
        self.gravity_direction = random.uniform(0, 2 * math.pi)
        
        # Apply gravity effect to the ball
        self.parent.gravity_direction = self.gravity_direction
        self.parent.gravity_strength = GravitationalPull.gravity_strength

        # Create the image attribute that is drawn to the surface.
        self.image = GravitationalPull.image.copy()
        
        # Play the sound effect
        sound = GravitationalPull.sound_effect.play()
        if not sound is None:
            sound.set_volume(settings.SOUND_VOLUME)

    def update(self, main_clock):
        # We make sure to call the supermethod.
        effect.Effect.update(self, main_clock)

        # If it's time, spawn particles.
        self.particle_spawn_time += main_clock.get_time()
        if self.particle_spawn_time >= GravitationalPull.particle_spawn_rate:
            # Reset the particle spawn time.
            self.particle_spawn_time = 0

            # Spawn a random amount of particles.
            for _ in range(0, random.randrange(0, GravitationalPull.particle_spawn_amount)):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.2 * settings.GAME_FPS, 0.35 * settings.GAME_FPS)
                retardation = speed / 76.0
                color = pygame.Color(random.randint(100, 255), random.randint(100, 255), random.randint(0, 100))
                particle.Particle(self.parent.x + self.parent.rect.width / 2, self.parent.y + self.parent.rect.height / 2, 
                                 self.parent.rect.width / 2, self.parent.rect.width / 2, angle, speed, retardation, color, 3 * settings.GAME_FPS)

    def on_kill(self):
        # Reset gravity values when the effect expires
        self.parent.gravity_direction = 0
        self.parent.gravity_strength = 0 