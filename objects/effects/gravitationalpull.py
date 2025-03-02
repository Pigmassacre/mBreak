__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import objects.groups as groups
import objects.effects.effect as effect
import objects.particle as particle
import settings.settings as settings
from settings.sounds import POWERUP_SOUNDS, play_sound

"""

This is the GravitationalPull effect. Balls that have this effect will have their trajectory
affected by a gravitational pull toward the opponent's side, making their movement curve.
The gravity direction changes randomly within a range, creating a jerky, unpredictable movement.

"""

class GravitationalPull(effect.Effect):

    # Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
    image = pygame.image.load("res/effect/timeout.png")  # Reusing timeout image for now

    # Initialize the sound effect.
    sound_effect = POWERUP_SOUNDS[0]  # Using first powerup sound

    # Standard values. These will be used unless any other values are specified per instance of this class.
    width = image.get_width()
    height = image.get_height()
    duration = 8000
    particle_spawn_rate = 300  # Reduced from 600 to 300 to spawn particles more frequently
    particle_spawn_amount = 4  # Increased from 2 to 4 for more particles

    # Gravity effect values
    gravity_strength = 100  # Repulsion strength from paddle
    attraction_strength = 10  # Attraction strength towards opponent's side
    max_effect_distance = 75  # Maximum distance at which repulsion has any effect
    min_effect_distance = 5   # Distance at which repulsion reaches maximum strength
    
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
        
        # Create the image attribute that is drawn to the surface.
        self.image = GravitationalPull.image.copy()
        
        # Apply gravity effect to the ball when created
        self.parent.gravity_strength = GravitationalPull.gravity_strength
        
        # Calculate initial gravity direction
        self.update_gravity_direction()
        
        # Play the sound effect
        play_sound(GravitationalPull.sound_effect)
            
    def get_opponent_paddle(self):
        # Get the opponent's paddle based on ball ownership
        opponent_player = None
        for player in groups.Groups.player_group:
            if player != self.parent.owner:
                opponent_player = player
                break
        
        if opponent_player:
            for paddle in groups.Groups.paddle_group:
                if paddle.owner == opponent_player:
                    return paddle
        return None
            
    def update_gravity_direction(self):
        opponent_paddle = self.get_opponent_paddle()
        if opponent_paddle:
            # Calculate the center points of the ball and paddle
            ball_center_x = self.parent.x + self.parent.rect.width / 2
            ball_center_y = self.parent.y + self.parent.rect.height / 2
            paddle_center_x = opponent_paddle.x + opponent_paddle.rect.width / 2
            paddle_center_y = opponent_paddle.y + opponent_paddle.rect.height / 2
            
            # Calculate the distance between ball and paddle
            dx = ball_center_x - paddle_center_x
            dy = ball_center_y - paddle_center_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Calculate repulsion strength based on distance from paddle
            if distance >= GravitationalPull.max_effect_distance:
                # No repulsion if too far
                repulsion_strength = 0
            elif distance <= GravitationalPull.min_effect_distance:
                # Maximum repulsion if very close
                repulsion_strength = GravitationalPull.gravity_strength
            else:
                # Linear interpolation between min and max distance
                # As distance increases, repulsion strength decreases
                strength_factor = (GravitationalPull.max_effect_distance - distance) / (GravitationalPull.max_effect_distance - GravitationalPull.min_effect_distance)
                repulsion_strength = GravitationalPull.gravity_strength * strength_factor

            # Calculate repulsion angle (away from paddle)
            repulsion_angle = math.atan2(dy, dx)
            
            # Calculate attraction angle (towards opponent's side)
            # If we are player 1 (left side), attract right (angle 0)
            # If we are player 2 (right side), attract left (angle π)
            # This is opposite of the opponent's position because we want to move towards them
            attraction_angle = 0 if self.parent.owner == list(groups.Groups.player_group)[0] else math.pi
            
            # Combine the forces using vector addition
            # Convert forces to x,y components
            repulsion_x = repulsion_strength * math.cos(repulsion_angle)
            repulsion_y = repulsion_strength * math.sin(repulsion_angle)
            attraction_x = GravitationalPull.attraction_strength * math.cos(attraction_angle)
            attraction_y = GravitationalPull.attraction_strength * math.sin(attraction_angle)
            
            # Add the forces
            total_x = repulsion_x + attraction_x
            total_y = repulsion_y + attraction_y
            
            # Calculate resulting angle and strength
            self.base_direction = math.atan2(total_y, total_x)
            self.parent.gravity_strength = math.sqrt(total_x * total_x + total_y * total_y)
            
            # Add some random variation to make it more interesting
            # Scale variation based on distance too - less variation when close
            max_variation = GravitationalPull.direction_variation * (distance / GravitationalPull.max_effect_distance)
            variation = random.uniform(-max_variation, max_variation)
            self.parent.gravity_direction = self.base_direction + variation

    def update(self, main_clock):
        # Only apply gravity if the ball is owned by the player who picked up the powerup
        if self.parent.owner == self.real_owner:
            # Update direction and strength
            self.update_gravity_direction()
            
            # Update direction change timer
            self.direction_change_time += main_clock.get_time()
            if self.direction_change_time >= GravitationalPull.direction_change_rate:
                # Reset the direction change time
                self.direction_change_time = 0
                # Update the gravity direction
                self.update_gravity_direction()
            
            # If it's time, spawn particles.
            self.particle_spawn_time += main_clock.get_time()
            if self.particle_spawn_time >= GravitationalPull.particle_spawn_rate:
                # Reset the particle spawn time.
                self.particle_spawn_time = 0

                # Spawn a random amount of particles.
                for _ in range(0, random.randrange(2, GravitationalPull.particle_spawn_amount + 1)):
                    # Use the current gravity direction for particle angle, with some variation
                    angle = self.parent.gravity_direction + random.uniform(-math.pi/4, math.pi/4)
                    speed = random.uniform(0.3 * settings.GAME_FPS, 0.5 * settings.GAME_FPS)
                    retardation = speed / 50.0
                    
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
                        self.parent.rect.width / 1.5,
                        self.parent.rect.width / 1.5, 
                        angle, speed, retardation, color, 4 * settings.GAME_FPS
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
            self.parent.gravity_strength = GravitationalPull.gravity_strength
            # Update gravity direction for new ownership
            self.update_gravity_direction()
        else:
            # The ball is now owned by the opponent, turn off gravity
            self.parent.gravity_direction = 0
            self.parent.gravity_strength = 0

    def on_kill(self):
        # Reset gravity values when the effect expires
        self.parent.gravity_direction = 0
        self.parent.gravity_strength = 0 