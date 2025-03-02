import pygame
import math
import settings.settings as settings
import objects.groups as groups

class Trajectory(pygame.sprite.Sprite):
    """
    A class that visualizes the predicted trajectory of a ball.
    """
    def __init__(self, ball, prediction_time=0.25):
        # Call the parent class constructor
        pygame.sprite.Sprite.__init__(self)
        
        # Store references
        self.ball = ball
        self.prediction_time = prediction_time
        
        # Create a surface for drawing the trajectory
        self.image = pygame.Surface((settings.LEVEL_MAX_X - settings.LEVEL_X, settings.LEVEL_MAX_Y - settings.LEVEL_Y), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = settings.LEVEL_X
        self.rect.y = settings.LEVEL_Y
        
        # Add to trajectory group
        groups.Groups.trajectory_group.add(self)
        
    def predict_trajectory(self):
        """
        Predicts the ball's trajectory for the next prediction_time seconds.
        Returns a list of points representing the trajectory path.
        """
        points = [(self.ball.x + self.ball.rect.width/2, self.ball.y + self.ball.rect.height/2)]
        
        # Calculate velocities
        speed_x = self.ball.speed * math.cos(self.ball.angle)
        speed_y = self.ball.speed * math.sin(self.ball.angle)
        
        # Current position
        current_x = self.ball.x
        current_y = self.ball.y
        
        # Time step for simulation (smaller steps = more accurate)
        dt = 1.0 / settings.GAME_FPS
        time_simulated = 0
        
        while time_simulated < self.prediction_time:
            # Calculate next position
            next_x = current_x + speed_x * dt
            next_y = current_y + speed_y * dt
            
            # Check for collisions with walls
            if next_x < settings.LEVEL_X:
                # Hit left wall
                next_x = settings.LEVEL_X
                speed_x = -speed_x
            elif next_x + self.ball.rect.width > settings.LEVEL_MAX_X:
                # Hit right wall
                next_x = settings.LEVEL_MAX_X - self.ball.rect.width
                speed_x = -speed_x
                
            if next_y < settings.LEVEL_Y:
                # Hit top wall
                next_y = settings.LEVEL_Y
                speed_y = -speed_y
            elif next_y + self.ball.rect.height > settings.LEVEL_MAX_Y:
                # Hit bottom wall
                next_y = settings.LEVEL_MAX_Y - self.ball.rect.height
                speed_y = -speed_y
            
            # Check for collisions with blocks
            test_rect = pygame.Rect(next_x, next_y, self.ball.rect.width, self.ball.rect.height)
            blocks_hit = pygame.sprite.spritecollide(self.ball, groups.Groups.block_group, False)
            
            if blocks_hit:
                # Add collision point and stop prediction
                points.append((next_x + self.ball.rect.width/2, next_y + self.ball.rect.height/2))
                break
            
            # Add point to trajectory
            points.append((next_x + self.ball.rect.width/2, next_y + self.ball.rect.height/2))
            
            # Update position
            current_x = next_x
            current_y = next_y
            
            time_simulated += dt
            
        return points
        
    def update(self, main_clock):
        # Clear the surface
        self.image.fill((0, 0, 0, 0))
        
        # Get trajectory points
        points = self.predict_trajectory()
        
        # Draw dotted line
        if len(points) > 1:
            # Convert points to screen coordinates
            screen_points = [(int(x - settings.LEVEL_X), int(y - settings.LEVEL_Y)) for x, y in points]
            
            # Draw dotted line segments
            for i in range(len(screen_points) - 1):
                if i % 2 == 0:  # Draw every other segment for dotted effect
                    start = screen_points[i]
                    end = screen_points[i + 1]
                    pygame.draw.line(self.image, self.ball.color, start, end, 2)
                    
    def destroy(self):
        self.kill() 