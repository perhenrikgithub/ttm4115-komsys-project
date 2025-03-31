ROLL_THRESHOLD = 0.125
PITCH_THRESHOLD = 0.175

def normalize_angle(angle):
    if angle > 180:
        angle -= 360
    elif angle < -180:
        angle += 360
    return abs(angle / 180)