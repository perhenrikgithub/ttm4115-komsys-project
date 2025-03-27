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

bblue = [120, 120, 249]
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

def set_display(offset):
    frame = animate(bg, bike, offset % 8)
    sense.set_pixels(flatten_grid(frame))

# lock and unlock symbols

empty = [0, 0, 0]

lock = [
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [empty, empty, red__, red__, red__, red__, empty, empty],
    [empty, empty, red__, empty, empty, red__, empty, empty],
    [empty, empty, red__, empty, empty, red__, empty, empty],
    [empty, red__, red__, red__, red__, red__, red__, empty],
    [empty, red__, empty, empty, empty, empty, red__, empty],
    [empty, red__, empty, empty, empty, empty, red__, empty],
    [empty, red__, red__, red__, red__, red__, red__, empty],
]

unlock = [
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [empty, empty, green, green, green, green, empty, empty],
    [empty, empty, green, empty, empty, green, empty, empty],
    [empty, empty, green, empty, empty, empty, empty, empty],
    [empty, green, green, green, green, green, green, empty],
    [empty, green, empty, empty, empty, empty, green, empty],
    [empty, green, empty, empty, empty, empty, green, empty],
    [empty, green, green, green, green, green, green, empty],
]


def set_lock_display():
    sense.set_pixels(flatten_grid(lock))

def set_unlock_display():
    sense.set_pixels(flatten_grid(unlock))