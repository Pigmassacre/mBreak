import pygame
import math
import settings.settings as settings
import objects.groups as groups
import random

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
                    
                # Find the closest block (similar to our improved collision system)
                closest_block = None
                closest_distance = float('inf')
                collision_side = None
                
                for block in blocks_hit:
                    # Calculate center points
                    ball_center_x = next_x + self.ball.rect.width / 2
                    ball_center_y = next_y + self.ball.rect.height / 2
                    block_center_x = block.rect.x + block.rect.width / 2
                    block_center_y = block.rect.y + block.rect.height / 2
                    
                    # Calculate vector from ball center to block center
                    delta_x = ball_center_x - block_center_x
                    delta_y = ball_center_y - block_center_y
                    
                    # Calculate distance between centers
                    distance = math.sqrt(delta_x**2 + delta_y**2)
                    
                    # Find the closest block
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_block = block
                        
                        # Determine which side of the block was hit
                        # Calculate the absolute projections onto each axis
                        proj_x = abs(delta_x)
                        proj_y = abs(delta_y)
                        
                        # Calculate the overlap thresholds
                        overlap_x = (self.ball.rect.width + block.rect.width) / 2
                        overlap_y = (self.ball.rect.height + block.rect.height) / 2
                        
                        # Determine the collision side based on the smallest overlap
                        if proj_x / overlap_x > proj_y / overlap_y:
                            # Horizontal collision (left or right)
                            collision_side = "left" if delta_x < 0 else "right"
                        else:
                            # Vertical collision (top or bottom)
                            collision_side = "top" if delta_y < 0 else "bottom"
                
                # Handle the collision based on the side
                if closest_block and collision_side:
                    if collision_side == "top":
                        # Only reverse y velocity if moving downward
                        if speed_y > 0:
                            speed_y = -speed_y
                        next_y = closest_block.rect.top - self.ball.rect.height
                    elif collision_side == "bottom":
                        # Only reverse y velocity if moving upward
                        if speed_y < 0:
                            speed_y = -speed_y
                        next_y = closest_block.rect.bottom
                    elif collision_side == "left":
                        # Only reverse x velocity if moving rightward
                        if speed_x > 0:
                            speed_x = -speed_x
                        next_x = closest_block.rect.left - self.ball.rect.width
                    elif collision_side == "right":
                        # Only reverse x velocity if moving leftward
                        if speed_x < 0:
                            speed_x = -speed_x
                        next_x = closest_block.rect.right
                    
                    # Add a small random variation to prevent predictable patterns
                    angle = math.atan2(speed_y, speed_x)
                    angle += random.uniform(-0.05, 0.05)
                    
                    # Ensure minimum angles to prevent getting stuck
                    # Normalize angle to 0-2π range
                    normalized_angle = angle % (2 * math.pi)
                    
                    # Minimum angles (in radians)
                    min_vertical_angle = math.pi / 10  # ~18 degrees from horizontal
                    min_horizontal_angle = math.pi / 10  # ~18 degrees from vertical
                    
                    # Check if angle is too close to horizontal
                    if abs(math.sin(normalized_angle)) < math.sin(min_vertical_angle):
                        # Adjust angle to maintain direction but increase vertical component
                        if normalized_angle < math.pi:
                            angle = min_vertical_angle if normalized_angle < math.pi/2 else math.pi - min_vertical_angle
                        else:
                            angle = -min_vertical_angle if normalized_angle < 3*math.pi/2 else 2*math.pi - min_vertical_angle
                    
                    # Check if angle is too close to vertical
                    elif abs(math.cos(normalized_angle)) < math.cos(min_horizontal_angle):
                        # Adjust angle to maintain direction but increase horizontal component
                        if normalized_angle < math.pi/2 or normalized_angle > 3*math.pi/2:
                            angle = min_horizontal_angle if normalized_angle < math.pi/2 else 2*math.pi - min_horizontal_angle
                        else:
                            angle = math.pi - min_horizontal_angle if normalized_angle < math.pi else math.pi + min_horizontal_angle
                    
                    # Recalculate velocities from the new angle
                    speed_x = self.ball.speed * math.cos(angle)
                    speed_y = self.ball.speed * math.sin(angle)
                
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