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
        
        # Create a temporary sprite for collision detection
        class TempSprite(pygame.sprite.Sprite):
            def __init__(self, rect):
                super().__init__()
                self.rect = rect
        
        temp_sprite = TempSprite(pygame.Rect(0, 0, self.ball.rect.width, self.ball.rect.height))
        
        # Time step for simulation (smaller steps = more accurate)
        dt = 1.0 / settings.GAME_FPS
        time_simulated = 0
        bounce_count = 0
        max_bounces = 3
        
        while time_simulated < self.prediction_time and bounce_count < max_bounces:
            # Calculate next position
            next_x = current_x + speed_x * dt
            next_y = current_y + speed_y * dt
            
            # Check for collisions with walls
            if next_x < settings.LEVEL_X:
                # Hit left wall
                next_x = settings.LEVEL_X
                speed_x = -speed_x
                bounce_count += 1
            elif next_x + self.ball.rect.width > settings.LEVEL_MAX_X:
                # Hit right wall
                next_x = settings.LEVEL_MAX_X - self.ball.rect.width
                speed_x = -speed_x
                bounce_count += 1
                
            if next_y < settings.LEVEL_Y:
                # Hit top wall
                next_y = settings.LEVEL_Y
                speed_y = -speed_y
                bounce_count += 1
            elif next_y + self.ball.rect.height > settings.LEVEL_MAX_Y:
                # Hit bottom wall
                next_y = settings.LEVEL_MAX_Y - self.ball.rect.height
                speed_y = -speed_y
                bounce_count += 1
            
            # Update temp_sprite rect for collision detection
            temp_sprite.rect.x = next_x
            temp_sprite.rect.y = next_y

            # Check for collisions with paddles first
            paddles_hit = pygame.sprite.spritecollide(temp_sprite, groups.Groups.paddle_group, False)
            if paddles_hit:
                bounce_count += 1
                if bounce_count >= max_bounces:
                    # Add final collision point before stopping
                    points.append((next_x + self.ball.rect.width/2, next_y + self.ball.rect.height/2))
                    break

                paddle = paddles_hit[0]  # Handle first paddle hit

                # Determine which side of the paddle we'll hit
                if temp_sprite.rect.bottom >= paddle.rect.top and temp_sprite.rect.top < paddle.rect.top:
                    # Top side collision
                    if temp_sprite.rect.right - paddle.rect.left > paddle.rect.top - temp_sprite.rect.top:
                        # More left side collision
                        # Calculate the new angle based on hit position
                        paddle_center = paddle.y + paddle.rect.height / 2.0
                        distance_from_paddle_center = (next_y + self.ball.height / 2.0) - paddle_center
                        max_distance = (paddle.y + paddle.rect.height + self.ball.height) - paddle_center
                        normalized_distance = (distance_from_paddle_center / max_distance)
                        max_angle_offset = (math.pi / 2 - self.ball.least_allowed_vertical_angle)
                        angle = math.pi - normalized_distance * max_angle_offset
                        speed_x = -abs(self.ball.speed * math.cos(angle))
                        speed_y = self.ball.speed * math.sin(angle)
                        next_x = paddle.rect.left - self.ball.rect.width
                    elif temp_sprite.rect.left - paddle.rect.right > paddle.rect.top - temp_sprite.rect.top:
                        # More right side collision
                        # Calculate the new angle based on hit position
                        paddle_center = paddle.y + paddle.rect.height / 2.0
                        distance_from_paddle_center = (next_y + self.ball.height / 2.0) - paddle_center
                        max_distance = (paddle.y + paddle.rect.height + self.ball.height) - paddle_center
                        normalized_distance = (distance_from_paddle_center / max_distance)
                        max_angle_offset = (math.pi / 2 - self.ball.least_allowed_vertical_angle)
                        angle = normalized_distance * max_angle_offset
                        speed_x = abs(self.ball.speed * math.cos(angle))
                        speed_y = self.ball.speed * math.sin(angle)
                        next_x = paddle.rect.right
                    else:
                        # Top collision
                        speed_y = -abs(speed_y)  # Bounce up
                        next_y = paddle.rect.top - self.ball.rect.height

                elif temp_sprite.rect.top <= paddle.rect.bottom and temp_sprite.rect.bottom > paddle.rect.bottom:
                    # Bottom side collision
                    if temp_sprite.rect.right - paddle.rect.left > temp_sprite.rect.bottom - paddle.rect.bottom:
                        # More left side collision
                        # Calculate the new angle based on hit position
                        paddle_center = paddle.y + paddle.rect.height / 2.0
                        distance_from_paddle_center = (next_y + self.ball.height / 2.0) - paddle_center
                        max_distance = (paddle.y + paddle.rect.height + self.ball.height) - paddle_center
                        normalized_distance = (distance_from_paddle_center / max_distance)
                        max_angle_offset = (math.pi / 2 - self.ball.least_allowed_vertical_angle)
                        angle = math.pi - normalized_distance * max_angle_offset
                        speed_x = -abs(self.ball.speed * math.cos(angle))
                        speed_y = self.ball.speed * math.sin(angle)
                        next_x = paddle.rect.left - self.ball.rect.width
                    elif temp_sprite.rect.left - paddle.rect.right > temp_sprite.rect.bottom - paddle.rect.bottom:
                        # More right side collision
                        # Calculate the new angle based on hit position
                        paddle_center = paddle.y + paddle.rect.height / 2.0
                        distance_from_paddle_center = (next_y + self.ball.height / 2.0) - paddle_center
                        max_distance = (paddle.y + paddle.rect.height + self.ball.height) - paddle_center
                        normalized_distance = (distance_from_paddle_center / max_distance)
                        max_angle_offset = (math.pi / 2 - self.ball.least_allowed_vertical_angle)
                        angle = normalized_distance * max_angle_offset
                        speed_x = abs(self.ball.speed * math.cos(angle))
                        speed_y = self.ball.speed * math.sin(angle)
                        next_x = paddle.rect.right
                    else:
                        # Bottom collision
                        speed_y = abs(speed_y)  # Bounce down
                        next_y = paddle.rect.bottom

                elif temp_sprite.rect.right >= paddle.rect.left and temp_sprite.rect.left < paddle.rect.left:
                    # Left side collision
                    # Calculate the new angle based on hit position
                    paddle_center = paddle.y + paddle.rect.height / 2.0
                    distance_from_paddle_center = (next_y + self.ball.height / 2.0) - paddle_center
                    max_distance = (paddle.y + paddle.rect.height + self.ball.height) - paddle_center
                    normalized_distance = (distance_from_paddle_center / max_distance)
                    max_angle_offset = (math.pi / 2 - self.ball.least_allowed_vertical_angle)
                    angle = math.pi - normalized_distance * max_angle_offset
                    speed_x = -abs(self.ball.speed * math.cos(angle))
                    speed_y = self.ball.speed * math.sin(angle)
                    next_x = paddle.rect.left - self.ball.rect.width

                elif temp_sprite.rect.left <= paddle.rect.right and temp_sprite.rect.right > paddle.rect.right:
                    # Right side collision
                    # Calculate the new angle based on hit position
                    paddle_center = paddle.y + paddle.rect.height / 2.0
                    distance_from_paddle_center = (next_y + self.ball.height / 2.0) - paddle_center
                    max_distance = (paddle.y + paddle.rect.height + self.ball.height) - paddle_center
                    normalized_distance = (distance_from_paddle_center / max_distance)
                    max_angle_offset = (math.pi / 2 - self.ball.least_allowed_vertical_angle)
                    angle = normalized_distance * max_angle_offset
                    speed_x = abs(self.ball.speed * math.cos(angle))
                    speed_y = self.ball.speed * math.sin(angle)
                    next_x = paddle.rect.right

                # Add collision point and continue prediction with new trajectory
                points.append((next_x + self.ball.rect.width/2, next_y + self.ball.rect.height/2))
                continue  # Skip block collision check for this iteration

            # Check for collisions with blocks
            blocks_hit = pygame.sprite.spritecollide(temp_sprite, groups.Groups.block_group, False)
            
            if blocks_hit:
                bounce_count += 1
                if bounce_count >= max_bounces:
                    # Add final collision point before stopping
                    points.append((next_x + self.ball.rect.width/2, next_y + self.ball.rect.height/2))
                    break
                    
                block = blocks_hit[0]  # Handle first block hit
                
                # Determine which side of the block we'll hit
                if temp_sprite.rect.bottom >= block.rect.top and temp_sprite.rect.top < block.rect.top:
                    # Top side collision
                    if temp_sprite.rect.right - block.rect.left > block.rect.top - temp_sprite.rect.top:
                        # More left side collision
                        speed_x = -abs(speed_x)  # Bounce left
                        next_x = block.rect.left - self.ball.rect.width
                    elif temp_sprite.rect.left - block.rect.right > block.rect.top - temp_sprite.rect.top:
                        # More right side collision
                        speed_x = abs(speed_x)  # Bounce right
                        next_x = block.rect.right
                    else:
                        # Top collision
                        speed_y = -abs(speed_y)  # Bounce up
                        next_y = block.rect.top - self.ball.rect.height
                
                elif temp_sprite.rect.top <= block.rect.bottom and temp_sprite.rect.bottom > block.rect.bottom:
                    # Bottom side collision
                    if temp_sprite.rect.right - block.rect.left > temp_sprite.rect.bottom - block.rect.bottom:
                        # More left side collision
                        speed_x = -abs(speed_x)  # Bounce left
                        next_x = block.rect.left - self.ball.rect.width
                    elif temp_sprite.rect.left - block.rect.right > temp_sprite.rect.bottom - block.rect.bottom:
                        # More right side collision
                        speed_x = abs(speed_x)  # Bounce right
                        next_x = block.rect.right
                    else:
                        # Bottom collision
                        speed_y = abs(speed_y)  # Bounce down
                        next_y = block.rect.bottom
                
                elif temp_sprite.rect.right >= block.rect.left and temp_sprite.rect.left < block.rect.left:
                    # Left side collision
                    speed_x = -abs(speed_x)  # Bounce left
                    next_x = block.rect.left - self.ball.rect.width
                
                elif temp_sprite.rect.left <= block.rect.right and temp_sprite.rect.right > block.rect.right:
                    # Right side collision
                    speed_x = abs(speed_x)  # Bounce right
                    next_x = block.rect.right
                
                # Add collision point and continue prediction with new trajectory
                points.append((next_x + self.ball.rect.width/2, next_y + self.ball.rect.height/2))
            
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
            
            # Calculate total path length
            total_length = 0
            for i in range(len(screen_points) - 1):
                x1, y1 = screen_points[i]
                x2, y2 = screen_points[i + 1]
                dx = x2 - x1
                dy = y2 - y1
                total_length += math.sqrt(dx * dx + dy * dy)
            
            # Calculate number of segments based on desired length
            segment_length = 4  # Length of each segment (drawn + gap)
            num_segments = max(1, int(total_length / segment_length))
            
            # Draw evenly spaced segments
            for i in range(num_segments):
                # Calculate start and end positions along the path (0 to 1)
                start_pos = (i * segment_length) / total_length
                end_pos = (i * segment_length + segment_length/2) / total_length  # Draw half of each segment
                
                if start_pos >= 1.0:  # Stop if we've reached the end
                    break
                    
                # Find the points for this segment
                current_length = 0
                segment_start = None
                segment_end = None
                
                # Find start point
                for j in range(len(screen_points) - 1):
                    x1, y1 = screen_points[j]
                    x2, y2 = screen_points[j + 1]
                    dx = x2 - x1
                    dy = y2 - y1
                    length = math.sqrt(dx * dx + dy * dy)
                    
                    next_length = current_length + length
                    target_length = start_pos * total_length
                    
                    if current_length <= target_length < next_length:
                        # Interpolate to find exact point
                        t = (target_length - current_length) / length
                        segment_start = (x1 + t * dx, y1 + t * dy)
                        break
                    current_length = next_length
                
                # Find end point
                current_length = 0
                for j in range(len(screen_points) - 1):
                    x1, y1 = screen_points[j]
                    x2, y2 = screen_points[j + 1]
                    dx = x2 - x1
                    dy = y2 - y1
                    length = math.sqrt(dx * dx + dy * dy)
                    
                    next_length = current_length + length
                    target_length = min(end_pos * total_length, total_length)
                    
                    if current_length <= target_length < next_length:
                        # Interpolate to find exact point
                        t = (target_length - current_length) / length
                        segment_end = (x1 + t * dx, y1 + t * dy)
                        break
                    current_length = next_length
                
                # Draw the segment
                if segment_start and segment_end:
                    # Calculate alpha value that fades from full (255) to 25
                    alpha = int(255 - (230 * start_pos))  # 255 -> 25 linear fade
                    # Create new color with same RGB but new alpha
                    color = pygame.Color(self.ball.color.r, self.ball.color.g, self.ball.color.b, max(25, alpha))
                    pygame.draw.line(self.image, color, segment_start, segment_end, 2)
                    
    def destroy(self):
        self.kill() 