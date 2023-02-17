import pygame

# Initialize PyGame
pygame.init()

# Set the size of the window, the player character, and the platform
size = (800, 600)
player_size = (40, 40)
platform_size = (200, 20)

# Create the window
screen = pygame.display.set_mode(size)

# Set the title of the window
pygame.display.set_caption("My Platformer Game")

# Set the background color of the window to white
screen.fill((255, 255, 255))

# Set the initial position of the player character
player_pos = [size[0] // 2 - player_size[0] // 2, size[1] - player_size[1]]

# Load the image for the player character
player_img = pygame.image.load("player.png").convert_alpha()

# Create a platform using a Surface
platform = pygame.Surface(platform_size)
platform.fill((0, 0, 255))
platform_pos = [size[0] // 2 - platform_size[0] // 2, size[1] - platform_size[1] - 50]

# Set up the clock to limit the frame rate
clock = pygame.time.Clock()
fps = 60

# Set up the variables for the game loop
gravity = 1.5
player_speed = 10
player_jump = 25
player_vel = [0, 0]
jumping = False

# Define a function to handle events
def handle_events():
    global jumping
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not jumping:
                player_vel[1] -= player_jump
                jumping = True
            elif event.key == pygame.K_LEFT:
                player_vel[0] = -player_speed
            elif event.key == pygame.K_RIGHT:
                player_vel[0] = player_speed
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player_vel[0] < 0:
                player_vel[0] = 0
            elif event.key == pygame.K_RIGHT and player_vel[0] > 0:
                player_vel[0] = 0

# Define a function to update the game state
def update():
    global jumping
    # Update the player's velocity based on gravity
    player_vel[1] += gravity
    # Move the player based on the velocity
    player_pos[0] += player_vel[0]
    player_pos[1] += player_vel[1]
    # Check if the player is on the ground or on the platform
    if player_pos[1] + player_size[1] >= size[1]:
        player_pos[1] = size[1] - player_size[1]
        player_vel[1] = 0
        jumping = False
    elif player_pos[1] + player_size[1] >= platform_pos[1] and player_pos[0] + player_size[0] > platform_pos[0] and player_pos[0] < platform_pos[0] + platform_size[0]:
        player_pos[1] = platform_pos[1] - player_size[1]
        player_vel[1] = 0
        jumping = False
    # Check if the player is outside the screen bounds
    if player_pos[0] < 0:
        player_pos[0] = 0
    elif player_pos[0] + player_size[0] > size[0]:
        player_pos[0] = size[0] - player_size[0]

# Define a function to draw the game state
def draw():
    screen.fill((255, 255, 255))
    screen.blit(player_img, player_pos)
    screen.blit(platform, platform_pos)

# Define the main game loop
def game_loop():
    while True:
        handle_events()
        update()
        draw()
        pygame.display.update()
        clock.tick(fps)

# Start the game loop
game_loop()

# Quit PyGame when the game loop ends
pygame.quit()