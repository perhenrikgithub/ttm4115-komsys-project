from sense_hat import SenseHat
import stmpy
import time

sense = SenseHat()

bblue = "🟦" 
green = "🟩" 
brown = "🟫" 
yello = "🟨" 
gray1 = "🟪" 
black = "⬛️" 
gray2 = "⬜️" 
red__ = "🟥" 

bblue = [144, 202, 249]
green = [34, 177, 76]
brown = [156, 90, 60]
yello = [255, 193, 14]
gray1 = [70, 70, 70]
black = [0, 0, 0]
gray2 = [180, 180, 180]
red__ = [237, 28, 36]

empty = None


def flatten_grid(grid):
    """Flattens a 2D grid into a 1D list."""
    return [item for row in grid for item in row]

bg = [
    [bblue, green, bblue, bblue, bblue, green, bblue, bblue],
    [green, green, green, bblue, green, green, green, bblue],
    [green, green, green, bblue, green, green, green, bblue],
    [bblue, brown, bblue, bblue, bblue, brown, bblue, bblue],
    [bblue, brown, bblue, bblue, bblue, brown, bblue, bblue],
    [gray2, gray2, gray2, gray2, gray2, gray2, gray2, gray2],
    [gray2, gray2, gray2, gray2, gray2, gray2, gray2, gray2],
    [gray2, gray2, gray2, gray2, gray2, gray2, gray2, gray2]
]


bike = [
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [empty, yello, yello, empty, empty, empty, empty, empty],
    [empty, yello, brown, empty, empty, empty, empty, empty],
    [yello, empty, gray1, gray1, black, black, empty, empty],
    [empty, empty, gray1, empty, red__, empty, empty, empty],
    [empty, empty, gray1, empty, red__, empty, empty, empty],
    [empty, red__, red__, red__, red__, empty, empty, empty],
    [empty, black, empty, empty, black, empty, empty, empty]
]

def animate(bg, bike, x_offset):
    frame = [row[:] for row in bg]  # Copy the background
    for r in range(8):
        for c in range(8):
            if bike[r][c] != empty and c + x_offset < 8 and c + x_offset >= 0:
                frame[r][c + x_offset] = bike[r][c]
    return frame

def print_grid(grid):
    for row in grid:
        print("".join(row))

def set_display(offset):
    frame = animate(bg, bike, offset % 8)
    sense.set_pixels(flatten_grid(frame))

# class BikeAnimation:
#     def __init__(self):
#         self.x_offset = 0

#     def update_display(self):
#         frame = animate(bg, bike, self.x_offset % 8)

#         # print_grid(frame) # terminal implementation
#         sense.set_pixels(flatten_grid(frame)) # sensehat implementation
        
#         self.x_offset = (self.x_offset + 1) % 8

# # Define the state machine
# bike_animation = BikeAnimation()
# bike_animation_transitions = [
#     {
#         "source": "initial", 
#         "target": "moving"
#         },  
#     {
#         "source": "moving", 
#         "trigger": "t", 
#         "target": "moving", 
#         "effect": "update_display"
#         },
# ]

# stm = stmpy.Machine(name="bike_stm", transitions=bike_animation_transitions, obj=bike_animation)
# driver = stmpy.Driver()
# driver.add_machine(stm)
# driver.start()

# x_off = 0

# while True:
#     set_display(x_off)
#     time.sleep(0.05)
#     x_off = (x_off + 1) % 8