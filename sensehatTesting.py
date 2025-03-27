from sense_hat import SenseHat

sense = SenseHat()

sense.clear()

bblue = (144, 202, 249)
green = (34, 177, 76)
brown = (156, 90, 60)
yello = (255, 193, 14)
gray1 = (70, 70, 70)
black = (0, 0, 0)
gray2 = (180, 180, 180)
red__ = (237, 28, 36)

empty = black 

def flatten_grid(grid):
    """Flattens a 2D grid into a 1D list."""
    return [item for row in grid for item in row]

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

sense.set_pixels(flatten_grid(bike))