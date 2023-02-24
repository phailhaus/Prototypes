import math

# Define the parameters of the tree
depth = 8
angle = math.pi/4
scale = 5

# Compute the size of the canvas we need
width = 2*(depth)*scale
height = (depth+2)*scale

# Create an empty image to draw on
image = [[" " for x in range(width)] for y in range(height)]

# Define a helper function to draw a branch of the tree
def draw_branch(x, y, length, angle):
    dx = int(length * math.sin(angle))
    dy = int(length * math.cos(angle))
    print(f"({x}, {y}), {length}")
    for i in range(length-y):
        image[y+i][x+int(i*dx/length)] = "*"
        image[y+i][x-int(i*dx/length)] = "*"
        #image[y+i][x+int(i*dy/length)] = "*"
        #image[y+i][x-int(i*dy/length)] = "*"

# Draw the tree recursively
def draw_tree(x, y, depth):
    if depth == 0:
        return
    draw_branch(x, y, depth*scale, -angle)
    draw_tree(x-int(depth*scale*math.sin(angle)), int(y+depth*scale*math.cos(angle)), depth-1)
    draw_tree(x+int(depth*scale*math.sin(angle)), int(y+depth*scale*math.cos(angle)), depth-1)

# Call the draw_tree function to create the tree
draw_tree(width//2, 0, depth)

# Print the resulting image
for row in image:
    print("".join(row))