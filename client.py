import PySimpleGUI as sg
import socket, sys, os, base64
from utils import (cv2, black_image_bytes, png_bytes_to_cv2_array,
                   image_to_bts, server_log, warning_log, check_port)


class UDPClientStreaming:
    def __init__(self, host : str = None, port : int = None):
        self.host = host
        self.port = port

    def start(self, host : str = None, port : int = None, GUI : bool = True):
        if self.host and self.port:
            host = self.host
            port = self.port

        if GUI:
            layout = [
                [ sg.Image(expand_x=True, expand_y=True, key="-image-") ]
            ]
            window = sg.Window("RECIEVING IMAGES", layout=layout, size=(600,600), resizable=False)


        BUFF_SIZE = 65536
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)

        while GUI:
            try:
                event, values = window.read(timeout=10)
                if event == sg.WIN_CLOSED:
                    break
                s.sendto(b"12345", (host, port))
                data, raddr = s.recvfrom(BUFF_SIZE)
                window["-image-"].update(data=data)
            except Exception as e:
                warning_log(repr(e))
                break

        while not(GUI):
            try:
                s.sendto(b"12345", (host, port))
                data, raddr = s.recvfrom(BUFF_SIZE)
                data = base64.b64decode(data)
                img = png_bytes_to_cv2_array(data)
                cv2.imshow("RECIEVING IMAGE", img)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
            except Exception as e:
                warning_log(repr(e))
                break
        s.close()
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        HOST = sys.argv[1]
        PORT = sys.argv[2]
        if not(PORT.isdigit() and check_port(PORT)):
            warning_log("Usage: port must be int between 1025 and 65535")
            sys.exit(1)
        PORT = int(PORT)
    else:
        warning_log("Usage: client.py <HOST> <PORT>")
        sys.exit(1)

    client = UDPClientStreaming(HOST, PORT)
    client.start(GUI=False)