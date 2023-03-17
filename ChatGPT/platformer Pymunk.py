import pygame
import pymunk

pygame.init()

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRAVITY = 900.0

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Initialize Pygame
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Create Pymunk space and set gravity
space = pymunk.Space()
space.gravity = (0, -GRAVITY)

# Create walls
static_body = space.static_body
left_wall = pymunk.Segment(static_body, (0, 0), (0, SCREEN_HEIGHT), 1)
right_wall = pymunk.Segment(static_body, (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), 1)
floor = pymunk.Segment(static_body, (0, 0), (SCREEN_WIDTH, 0), 1)
space.add(left_wall, right_wall, floor)

# Create player body
player_body = pymunk.Body(1, float('inf'))
player_circle = pymunk.Circle(player_body, 16)
player_circle.friction = 0.5
player_circle.elasticity = 0.0
player_circle.collision_type = 1

# Create collision shapes for player's sides and bottom
player_width = 32
player_height = 48
player_shape_left = pymunk.Segment(player_body, (-player_width / 2, -player_height / 2), (-player_width / 2, player_height / 2), 2)
player_shape_right = pymunk.Segment(player_body, (player_width / 2, -player_height / 2), (player_width / 2, player_height / 2), 2)
player_shape_bottom = pymunk.Segment(player_body, (-player_width / 2, -player_height / 2), (player_width / 2, -player_height / 2), 2)
player_shape_left.friction = 0.5
player_shape_left.elasticity = 0.0
player_shape_left.collision_type = 2
player_shape_right.friction = 0.5
player_shape_right.elasticity = 0.0
player_shape_right.collision_type = 2
player_shape_bottom.friction = 0.5
player_shape_bottom.elasticity = 0.0
player_shape_bottom.collision_type = 2

# Set positions for collision shapes
player_shape_left.offset = (-player_width / 2, 0)
player_shape_right.offset = (player_width / 2, 0)
player_shape_bottom.offset = (0, -player_height / 2)

player_body.position = (100, 50)

# Add player shapes to space
space.add(player_body, player_circle, player_shape_left, player_shape_right, player_shape_bottom)

# Define collision handler
def collision_handler(arbiter, space, data):
    global jumping
    jumping = False
    return True

handler = space.add_collision_handler(1, 2)
handler.begin = collision_handler

# Define key constants
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_JUMP = pygame.K_UP

# Initialize variables
velocity = 0.0
jumping = False

# Game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Handle keyboard input
    keys = pygame.key.get_pressed()
    if keys[KEY_LEFT]:
        player_body.apply_impulse_at_local_point((-10, 0))
    if keys[KEY_RIGHT]:
        player_body.apply_impulse_at_local_point((10, 0))
    if keys[KEY_JUMP] and not jumping:
        player_body.apply_impulse_at_local_point((0, 20))
        jumping = True
    
	# Step Pymunk space
    space.step(1/60.0)

    # Update player velocity
    velocity = player_body.velocity

    # Update Pygame display
    screen.fill(BLACK)

    # Draw walls
    pygame.draw.line(screen, WHITE, left_wall.a, left_wall.b, 2)
    pygame.draw.line(screen, WHITE, right_wall.a, right_wall.b, 2)
    pygame.draw.line(screen, WHITE, floor.a, floor.b, 2)

    # Draw player
    player_pos = player_body.position
    player_rect = pygame.Rect(player_pos.x - player_width / 2, SCREEN_HEIGHT - player_pos.y - player_height / 2, player_width, player_height)
    pygame.draw.circle(screen, WHITE, (int(player_pos.x), int(SCREEN_HEIGHT - player_pos.y)), int(player_circle.radius), 0)
    pygame.draw.line(screen, WHITE, player_shape_left.a, player_shape_left.b, 2)
    pygame.draw.line(screen, WHITE, player_shape_right.a, player_shape_right.b, 2)
    pygame.draw.line(screen, WHITE, player_shape_bottom.a, player_shape_bottom.b, 2)

    # Update Pygame display
    pygame.display.update()
    clock.tick(60)

pygame.quit()
