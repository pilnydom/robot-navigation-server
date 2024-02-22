from protocols import *

class connection:
    def __init__(self, sock):
        self.sock = sock
        self.buffer = ""

    def send_message(self, message):
        self.sock.sendall((f"{message}\a\b").encode())
        print(f"S: {message}\a\b")
    
    def recieve_message(self):
        while "\a\b" not in self.buffer:
            new_data = self.sock.recv(1024)
            if not new_data:
                raise ValueError

            self.buffer += new_data.decode()

        next_message, self.buffer = self.buffer.split("\a\b", 1)
        print(f"C: {next_message}")
        return next_message
    
    def move(self):
        self.send_message(SERVER_MOVE)

    def turn_left(self):
        self.send_message(SERVER_TURN_LEFT)

    def turn_right(self):
        self.send_message(SERVER_TURN_RIGHT)

    def pick_up(self):
        self.send_message(SERVER_PICK_UP)