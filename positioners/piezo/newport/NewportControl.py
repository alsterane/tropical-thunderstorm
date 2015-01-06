__author__ = 'df-setup-basement'

import socket
import time


# control MadCityLabs Piezo Stage through Madlib.dll
class NewportControl:

    def __init__(self, address, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((address, port))
        time.sleep(0.1)

    def disconnect_picomotors(self):
        self.s.close()

    def send(self, message):
        self.s.send(message + '\n')

    def receive(self):
        data = self.s.recv(1024)
        return data

    def move(self, motor, direction, steps):
        if direction:
            move_msg = str(motor) + "PA+" + str(steps)
        else:
            move_msg = str(motor) + "PA-" + str(steps)
        self.send(move_msg)





