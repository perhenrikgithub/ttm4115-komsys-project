
import stmpy
import time


bblue = "🟦" 
green = "🟩" 
brown = "🟫" 
yello = "🟨" 
gray1 = "🟪" 
black = "⬛️" 
gray2 = "⬜️" 
red__ = "🟥" 

bblue = [120, 120, 249]
_blu_ = [0, 0, 255]
green = [34, 177, 76]
brown = [156, 90, 60]
yello = [255, 193, 14]
gray1 = [70, 70, 70]
black = [0, 0, 0]
gray2 = [180, 180, 180]
red__ = [237, 28, 36]
white = [255, 255, 255]

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
    frame = [row[:] for row in bg] 
    for r in range(8):
        for c in range(8):
            if bike[r][c] != empty and c + x_offset < 8 and c + x_offset >= 0:
                frame[r][c + x_offset] = bike[r][c]
    return frame

def set_display(sense, offset):
    frame = animate(bg, bike, offset % 8)
    sense.set_pixels(flatten_grid(frame))

# lock and unlock symbols

lock = [
    [black, black, black, black, black, black, black, black],
    [black, black, red__, red__, red__, red__, black, black],
    [black, black, red__, black, black, red__, black, black],
    [black, black, red__, black, black, red__, black, black],
    [black, red__, red__, red__, red__, red__, red__, black],
    [black, red__, red__, red__, red__, red__, red__, black],
    [black, red__, red__, red__, red__, red__, red__, black],
    [black, red__, red__, red__, red__, red__, red__, black],
]

unlock = [
    [black, black, black, black, black, black, black, black],
    [black, black, green, green, green, green, black, black],
    [black, black, green, black, black, green, black, black],
    [black, black, green, black, black, black, black, black],
    [black, green, green, green, green, green, green, black],
    [black, green, green, green, green, green, green, black],
    [black, green, green, green, green, green, green, black],
    [black, green, green, green, green, green, green, black],
]

reserved = [
    white, white, white, white, white, white, white, black,
    white, white, white, white, white, white, white, white,
    white, white, white, black, black, white, white, white,
    white, white, white, black, black, white, white, white,
    white, white, white, white, white, white, white, black,
    white, white, white, white, white, white, white, black,
    white, white, white, black, black, white, white, white,
    white, white, white, black, black, white, white, white,
]

unreserved = [
    red__, white, white, white, white, white, white, red__,
    white, red__, white, white, white, white, red__, white,
    white, white, red__, black, black, red__, white, white,
    white, white, white, red__, black, white, white, white,
    white, white, white, white, red__, white, white, black,
    white, white, red__, white, white, red__, white, black,
    white, red__, white, black, black, white, red__, white,
    red__, white, white, black, black, white, white, red__,
]

red_bg = [
    red__, red__, red__, red__, red__, red__, red__, red__,
    red__, red__, red__, red__, red__, red__, red__, red__,
    red__, red__, red__, red__, red__, red__, red__, red__,
    red__, red__, red__, red__, red__, red__, red__, red__,
    red__, red__, red__, red__, red__, red__, red__, red__,
    red__, red__, red__, red__, red__, red__, red__, red__,
    red__, red__, red__, red__, red__, red__, red__, red__,
    red__, red__, red__, red__, red__, red__, red__, red__,
]



def set_lock_display(sense):
    sense.set_pixels(flatten_grid(lock))

def set_unlock_display(sense):
    sense.set_pixels(flatten_grid(unlock))

def set_reserved_display(sense):
    sense.set_pixels(reserved)

def set_unreserved_display(sense):
    sense.set_pixels(unreserved)

def error_blink(sense):
    for _ in range(3):
        sense.set_pixels(flatten_grid(red_bg))
        time.sleep(0.1)
        sense.clear()
        time.sleep(0.1)
    sense.clear()