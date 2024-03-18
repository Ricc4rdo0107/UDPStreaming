import PySimpleGUI as sg
from threading import Thread
import socket, sys, os, base64
from utils import (cv2, black_image, black_image_bytes, png_bytes_to_cv2_array,
                   image_to_bts, server_log, warning_log, check_port, screenshot_bytes)


class UDPStreamingServer:
    def __init__(self, host : str = None, port : int = None) :
        self.host = host
        self.port = port
        self.current_client : tuple|bool = None
        self.clients = []
        self.cap = cv2.VideoCapture(0)

    def GUI(self):
        sg.theme("darkblack")
        clients = [
            [ 
                sg.Text("Client Addres: ", justification="l", font=("Arial", 10)),
                sg.Text("", key="-client-", justification="r", font=("Arial", 10)) 
            ]
        ]
        layout = [
            [ sg.Column(layout=clients, expand_x=True) ],
            [ sg.Button("STOP SERVER", key="-stop-", button_color="white on red", font=("Arial", 10), expand_x=True) ],
            [ sg.Button("Keep On Top", key="-kot-", button_color="white on red", font=("Arial", 10), expand_x=True) ]
        ]
        window = sg.Window("UDP SERVER (Control Panel)", layout=layout, resizable=False, size=(400, 140))

        kot = False
        while True:
            event, values = window.read(timeout=25)
            
            if event == sg.WIN_CLOSED:
                break
            
            if event == "-stop-" and self.server_on:
                self.s.close()
                window["-stop-"].update("START SERVER")
                window["-stop-"].update(button_color="white on green")

            if event == "-stop-" and not self.server_on:
                self.cap = cv2.VideoCapture(0)
                server_thread = Thread(target=server.start, args=(self.host, self.port, False))
                server_thread.start()
                window["-stop-"].update("STOP SERVER")
                window["-stop-"].update(button_color="white on red")

            if event == "-kot-":
                kot = not(kot)
                if kot:
                    window["-kot-"].update(button_color="white on green")
                else:
                    window["-kot-"].update(button_color="white on red") 
                window.TKroot.wm_attributes("-topmost", kot)

            if len(self.clients):
                self.clients = list(set(self.clients))
                window["-client-"].update(" ".join([ f"{x[0]}:{x[1]}" for x in self.clients]))

        window.close()

    def start(self, host : str|bool = None, port : int|bool = None, screen : bool = False):
        self.server_on = True
        if self.host and self.port:
            host = self.host
            port = self.port

        BUFF_SIZE = 65536
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
        
        self.s.bind((host, port))
        server_log("Listening...")
        
        QUAL = 80

        while True:
            if screen:
                screen_bytes = screenshot_bytes()
                screen_img = png_bytes_to_cv2_array(screen_bytes, debug=False)
                screen_img = cv2.resize(screen_img, (720, 405), interpolation=cv2.INTER_NEAREST)
                frame = image_to_bts(screen_img, qual=QUAL)
                
            else:
                ret, frame = self.cap.read()
                frame = cv2.flip(frame, 1)
                frame = image_to_bts(frame)

            image_packet = base64.b64encode(frame)

            while len(image_packet) >= BUFF_SIZE:
                if QUAL > 60:
                    QUAL -= 5
                    warning_log("QUALITY -5")
                else:
                    warning_log("QUALITY BELOW 60")
                    screen_img = black_image

                frame = image_to_bts(screen_img, qual=QUAL)
                image_packet = base64.b64encode(frame)
                    
            try:
                data, raddr = self.s.recvfrom(BUFF_SIZE)
            except:
                break
            if data:
                if data == b"12345":
                    try:
                        self.s.sendto(image_packet, raddr)
                    except ConnectionResetError:
                        server_log("Server shutted down.")
                        sys.exit(0)
                    #self.current_client = raddr
                    self.clients.append(raddr)
                    server_log(f"SENDING BUFFER TO {raddr[0]}:{raddr[1]}")
                    #cv2.imshow("SENDING IMAGE", frame)
                    #key = cv2.waitKey(1) & 0xFF
                    #if key==ord("q"):
                    #    break
                else:
                    self.s.sendto(base64.b64encode(black_image_bytes()), raddr)
            else:
                break
        self.cap.release()
        self.s.close()
        self.server_on = False
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
        warning_log("Usage: server.py <HOST> <PORT>")
        sys.exit(1)

    server = UDPStreamingServer(HOST, PORT)

    server_thread = Thread(target=server.start, args=(None, None, False))
    server_thread.start()

    server.GUI()