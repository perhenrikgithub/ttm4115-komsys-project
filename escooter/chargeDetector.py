import subprocess

def is_usb_device_connected():
    result = subprocess.run(['lsusb'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    # Skip root hubs and
    return len(lines) > 3

def is_charging():
    return is_usb_device_connected()

