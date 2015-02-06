__author__ = 'df-setup-basement'

import socket
import time


# control MadCityLabs Piezo Stage through Madlib.dll
class NewportControl:
    """
    Ethernet communication to Newport Picomotor controlled via Newport Picomotor Controller 8742 (open-loop).
    """

    def __init__(self, address, port):
        """
        Initialises ethernet connection to controller.
        :param address: IP address of controller.
        :param port: Port of controller.
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((address, port))
        time.sleep(0.5)

    def disconnect_picomotors(self):
        """
        Disconnect from controller, close connection.
        """
        self.s.close()

    def send(self, message):
        """
        Send message to controller. See Newport Picocontroller manual for available commands.
        :param message: Control sequence.
        """
        self.s.send(message + '\n')

    def receive(self):
        """
        Receive message from controller.
        :return: Returned message.
        """
        data = self.s.recv(1024)
        return data

    def move(self, motor, direction, steps):
        """
        Move specified motor along specified axis for specified number of steps.
        :param motor: int Motor (1,2,3 or 4)
        :param direction: int Direction (0, 1)
        :param steps: int Steps.
        """
        if direction:
            move_msg = str(motor) + "PA+" + str(steps)
        else:
            move_msg = str(motor) + "PA-" + str(steps)
        self.send(move_msg)


# Test script

def test_run():
    controlNewport = NewportControl('169.254.169.20', 23)

    # move up
    controlNewport.move(2, 0, 100)

if __name__ == "__main__":
   test_run()





