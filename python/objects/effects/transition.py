import pygame
import random
import math
import settings.settings as settings

class ScreenTransition:
    def __init__(self, window_surface, square_size=20, duration=500, max_delay=2000, global_delay=0):
        self.window_surface = window_surface
        self.square_size = square_size
        self.duration = duration
        self.max_delay = max_delay
        self.global_delay = global_delay
        self.global_time = 0
        
        # Calculate number of squares needed to cover the screen
        self.cols = math.ceil(settings.SCREEN_WIDTH / square_size)
        self.rows = math.ceil(settings.SCREEN_HEIGHT / square_size)
        
        # Calculate center points
        center_x = settings.SCREEN_WIDTH / 2
        center_y = settings.SCREEN_HEIGHT / 2
        
        # Calculate maximum possible distance from center for normalization
        max_distance = math.sqrt((center_x ** 2) + (center_y ** 2))
        
        # Initialize squares with radial delays
        self.squares = []
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * square_size
                y = row * square_size
                
                # Calculate square center
                square_center_x = x + (square_size / 2)
                square_center_y = y + (square_size / 2)
                
                # Calculate distance from center
                dx = square_center_x - center_x
                dy = square_center_y - center_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Apply non-linear scaling to make the spread more gradual
                # Using a power curve to make distances near the center bunch up more
                normalized_distance = (distance / max_distance)
                delay = self.max_delay * math.pow(normalized_distance, 1.5)  # Power of 2.5 for more gradual spread
                
                self.squares.append({
                    'rect': pygame.Rect(x, y, square_size, square_size),
                    'delay': delay,
                    'time': 0,
                    'alpha': 255,
                    'scale': 1.0
                })
        
        # Create surface for the transition
        self.surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.done = False
        
    def update(self, delta_time):
        if self.done:
            return True
            
        # Update global time first
        self.global_time += delta_time
        if self.global_time < self.global_delay:
            return False
            
        all_squares_done = True
        
        for square in self.squares:
            # Update time only after delay has passed
            if square['time'] >= square['delay']:
                progress = (square['time'] - square['delay']) / self.duration
                if progress < 1:
                    # Simple fade out
                    square['scale'] = max(0, 1.0 - progress)
                    square['alpha'] = int(255 * (1 - progress))
                    all_squares_done = False
            else:
                square['time'] += delta_time
                all_squares_done = False
                
            square['time'] += delta_time
            
        self.done = all_squares_done
        return self.done
        
    def draw(self):
        self.surface.fill((0, 0, 0, 0))
        
        # If we haven't reached global delay, draw all squares at full size/alpha
        if self.global_time < self.global_delay:
            for square in self.squares:
                pygame.draw.rect(self.surface, (0, 0, 0, 255), square['rect'])
            self.window_surface.blit(self.surface, (0, 0))
            return
        
        for square in self.squares:
            if square['time'] >= square['delay']:
                progress = (square['time'] - square['delay']) / self.duration
                if progress < 1:
                    # Calculate current square size based on scale
                    current_size = int(self.square_size * square['scale'])
                    if current_size > 0:
                        # Calculate position to keep square centered as it scales
                        offset = (self.square_size - current_size) // 2
                        rect = pygame.Rect(
                            square['rect'].x + offset,
                            square['rect'].y + offset,
                            current_size,
                            current_size
                        )
                        pygame.draw.rect(self.surface, (0, 0, 0, square['alpha']), rect)
            else:
                # Draw full size square before delay is over
                pygame.draw.rect(self.surface, (0, 0, 0, 255), square['rect'])
                
        self.window_surface.blit(self.surface, (0, 0)) 