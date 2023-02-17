# Made with the prompt "Please make a sidescrolling shooter in Python using Pygame". Had to continue it with "Continue previous response". I then had to ask it "Can you add a framerate limiter to this?" because it forgot to do that. I then asked it "Please limit the player to the bounds of the screen and make the player die if hit by an enemy"

import pygame
import random

# Initialize Pygame
pygame.init()

# Set the dimensions of the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the title of the window
pygame.display.set_caption("Side-Scrolling Shooter")

# Load the player image and get its dimensions
player_img = pygame.image.load("player.png")
player_width, player_height = player_img.get_rect().size

# Load the bullet image and get its dimensions
bullet_img = pygame.image.load("bullet.png")
bullet_width, bullet_height = bullet_img.get_rect().size

# Load the enemy image and get its dimensions
enemy_img = pygame.image.load("enemy.png")
enemy_width, enemy_height = enemy_img.get_rect().size

# Set the starting position of the player
player_x = 50
player_y = 250

# Set the speed of the player and the bullets
player_speed = 5
bullet_speed = 10

# Create a list to store the bullets
bullets = []

# Set the starting position and speed of the enemy
enemy_x = screen_width
enemy_y = random.randint(0, screen_height - enemy_height)
enemy_speed = 3

# Create a variable to keep track of the score
score = 0

# Load the font and set the size
font = pygame.font.Font(None, 36)

# Set up the clock object
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    # Limit the framerate to 60 frames per second
    clock.tick(60)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Create a new bullet when the space key is pressed
                bullet_x = player_x + player_width
                bullet_y = player_y + player_height / 2 - bullet_height / 2
                bullets.append((bullet_x, bullet_y))

    # Move the player up or down when the up or down arrow keys are pressed
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_y -= player_speed
        if player_y < 0:
            player_y = 0
    elif keys[pygame.K_DOWN]:
        player_y += player_speed
        if player_y > screen_height - player_height:
            player_y = screen_height - player_height

    # Move the bullets to the right and remove them if they go off the screen
    bullets = [(bullet_x + bullet_speed, bullet_y) for bullet_x, bullet_y in bullets if bullet_x < screen_width]

    # Move the enemy to the left and reset its position if it goes off the screen
    enemy_x -= enemy_speed
    if enemy_x < -enemy_width:
        enemy_x = screen_width
        enemy_y = random.randint(0, screen_height - enemy_height)

    # Check for collisions between bullets and the enemy
    for bullet in bullets:
        bullet_x, bullet_y = bullet
        if bullet_x + bullet_width > enemy_x and bullet_y < enemy_y + enemy_height and bullet_y + bullet_height > enemy_y:
            # Remove the bullet and reset the enemy position if there's a collision
            bullets.remove(bullet)
            enemy_x = screen_width
            enemy_y = random.randint(0, screen_height - enemy_height)
            score += 1
    
    # Check for collisions between the player and the enemy
    if player_x + player_width > enemy_x and player_y < enemy_y + enemy_height and player_y + player_height > enemy_y:
        # Player hit by the enemy, game over
        running = False

    # Clear the screen
    screen.fill((255, 255, 255))

    # Draw the player, bullets, enemy, and score on the screen
    screen.blit(player_img, (player_x, player_y))
    for bullet in bullets:
        bullet_x, bullet_y = bullet
        screen.blit(bullet_img, (bullet_x, bullet_y))
    screen.blit(enemy_img, (enemy_x, enemy_y))
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # Update the screen
    pygame.display.flip()

# Clean up
pygame.quit()