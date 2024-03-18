import cv2, mss
import compress
import numpy as np
from termcolor import cprint

black_image = np.full((480, 640), 000)
black_image_bytes = lambda: cv2.imencode(".png", black_image)[1].tobytes()

compressor = compress.Compressor()

class InvalidFileFromat(Exception):
     def __init__(self, message):
        super().__init__(message)

def server_log(text:str, color="green") -> None:
        cprint(f"[SERVER] ", "green", end="")
        cprint(text, color)

def client_log(text:str, color="green") -> None:
        cprint(f"[CLIENT] ", "green", end="")
        cprint(text, color)

def check_port(port:int) -> bool:
    return int(port) in range(1025,65535)

def warning_log(text:str, color="light_red") -> None:
        cprint(f"[WARNING] ", "light_red", end="")
        cprint(text, color)

def screenshot_bytes() -> bytes:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        im = sct.grab(monitor)
        raw_bytes = mss.tools.to_png(im.rgb, im.size)
        return raw_bytes

def image_to_bts(frame, qual=80):
    try:
        img = cv2.imencode(".jpg", frame,[cv2.IMWRITE_JPEG_QUALITY,qual])[1]
    except:
        img = black_image_bytes()
    return img
def png_bytes_to_cv2_array(png_bytes, debug=True):
    nparr = np.frombuffer(png_bytes, np.uint8)
    if debug:
        print("Array NumPy:", nparr)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image