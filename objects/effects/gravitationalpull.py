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
affected by a gravitational pull toward the opponent's side, making their movement curve.
The gravity direction changes randomly within a range, creating a jerky, unpredictable movement.

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
    particle_spawn_rate = 300  # Reduced from 600 to 300 to spawn particles more frequently
    particle_spawn_amount = 4  # Increased from 2 to 4 for more particles

    # Gravity effect values
    gravity_strength = 200  # High value to be noticeable when multiplied by delta_time
    
    # Direction change values
    direction_change_rate = 150  # How often to change direction (in milliseconds)
    direction_variation = math.pi / 4  # Maximum variation from base direction (45 degrees)

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
        
        # When this reaches direction_change_rate, the gravity direction changes.
        self.direction_change_time = 0
        
        # Store the base direction based on ownership
        if self.parent.owner == list(groups.Groups.player_group)[0]:  # If ball belongs to player_one (left side)
            # Base direction to pull toward the right (0 radians or 0 degrees)
            self.base_direction = 0
        else:  # If ball belongs to player_two (right side)
            # Base direction to pull toward the left (π radians or 180 degrees)
            self.base_direction = math.pi
            
        # Set initial random direction variation
        self.randomize_direction()

        # Create the image attribute that is drawn to the surface.
        self.image = GravitationalPull.image.copy()
        
        # Apply gravity effect to the ball when created
        self.parent.gravity_strength = GravitationalPull.gravity_strength
        
        # Play the sound effect
        sound = GravitationalPull.sound_effect.play()
        if not sound is None:
            sound.set_volume(settings.SOUND_VOLUME)
            
    def randomize_direction(self):
        # Randomize the gravity direction within the allowed variation range
        variation = random.uniform(-GravitationalPull.direction_variation, GravitationalPull.direction_variation)
        self.parent.gravity_direction = self.base_direction + variation

    def update(self, main_clock):
        # Only apply gravity if the ball is owned by the player who picked up the powerup
        if self.parent.owner == self.real_owner:
            # Update base direction based on current owner
            if self.parent.owner == list(groups.Groups.player_group)[0]:  # If ball belongs to player_one (left side)
                # Base direction to pull toward the right (0 radians or 0 degrees)
                self.base_direction = 0
            else:  # If ball belongs to player_two (right side)
                # Base direction to pull toward the left (π radians or 180 degrees)
                self.base_direction = math.pi
            
            # Make sure gravity strength is set
            self.parent.gravity_strength = GravitationalPull.gravity_strength
            
            # Update direction change timer
            self.direction_change_time += main_clock.get_time()
            if self.direction_change_time >= GravitationalPull.direction_change_rate:
                # Reset the direction change time
                self.direction_change_time = 0
                # Randomize the gravity direction
                self.randomize_direction()
            
            # If it's time, spawn particles.
            self.particle_spawn_time += main_clock.get_time()
            if self.particle_spawn_time >= GravitationalPull.particle_spawn_rate:
                # Reset the particle spawn time.
                self.particle_spawn_time = 0

                # Spawn a random amount of particles.
                for _ in range(0, random.randrange(2, GravitationalPull.particle_spawn_amount + 1)):  # Ensure at least 2 particles
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(0.3 * settings.GAME_FPS, 0.5 * settings.GAME_FPS)  # Increased speed
                    retardation = speed / 50.0  # Reduced retardation for longer-lasting particles
                    
                    # Use more vibrant colors for better visibility
                    color = pygame.Color(
                        random.randint(150, 255),  # More red
                        random.randint(50, 150),   # Less green
                        random.randint(200, 255)   # More blue - creates purple/magenta tones
                    )
                    
                    # Create slightly larger particles
                    particle.Particle(
                        self.parent.x + self.parent.rect.width / 2, 
                        self.parent.y + self.parent.rect.height / 2, 
                        self.parent.rect.width / 1.5,  # Larger particles
                        self.parent.rect.width / 1.5, 
                        angle, speed, retardation, color, 4 * settings.GAME_FPS  # Longer lifetime
                    )
        else:
            # If the ball is not owned by the player who picked up the powerup,
            # turn off gravity
            self.parent.gravity_direction = 0
            self.parent.gravity_strength = 0

        # We make sure to call the supermethod last, in case it triggers on_kill
        effect.Effect.update(self, main_clock)

    def on_hit_paddle(self, paddle):
        # When the ball hits a paddle, it changes ownership
        # We need to update the gravity direction immediately
        if paddle.owner == self.real_owner:
            # The ball is now owned by the player who picked up the powerup
            if paddle.owner == list(groups.Groups.player_group)[0]:  # If paddle belongs to player_one (left side)
                # Base direction to pull toward the right (0 radians or 0 degrees)
                self.base_direction = 0
            else:  # If paddle belongs to player_two (right side)
                # Base direction to pull toward the left (π radians or 180 degrees)
                self.base_direction = math.pi
            
            self.parent.gravity_strength = GravitationalPull.gravity_strength
            # Immediately randomize direction after hitting paddle
            self.randomize_direction()
        else:
            # The ball is now owned by the opponent, turn off gravity
            self.parent.gravity_direction = 0
            self.parent.gravity_strength = 0

    def on_kill(self):
        # Reset gravity values when the effect expires
        self.parent.gravity_direction = 0
        self.parent.gravity_strength = 0 