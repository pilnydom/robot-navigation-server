import socket
from threading import *

from protocols import *
from helpers import *
from connection import *


class server:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port

    def run(self):
        # Creating a socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Binding the socket
            sock.bind((self.host, self.port))

            # Listening for incoming connections
            sock.listen(1)
            print("Waiting for a connection...")

            while True:
                # Waiting for a connection
                connection, client_address = sock.accept()
                connection.settimeout(TIMEOUT)
                print(f"Connected to {client_address}")

                # Creating thread for the connection
                thread = Thread(target=self.communicate, args=(connection,))
                thread.start()

    def authenticate(self, robot):
        # Receiving username from client
        client_username = robot.recieve_message()

        # Checking username
        if len(client_username) > CLIENT_USERNAME_LENGTH:
            robot.send_message(SERVER_SYNTAX_ERROR)
            return False

        # Sending key request to client
        robot.send_message(SERVER_KEY_REQUEST)

        # Receiving key ID from client
        client_key_id = robot.recieve_message()

        # Verifying client key ID
        if not valid_syntax(client_key_id, CLIENT_KEY_ID_LENGTH):
            robot.send_message(SERVER_SYNTAX_ERROR)
            return False

        # Calculating hash of username
        client_username_hash = sum(ord(c) for c in client_username) * 1000 % HASH_MODULO

        # Calculating and sending server confirmation code
        server_confirmation_code = (client_username_hash + SERVER_KEYS[int(client_key_id)]) % HASH_MODULO
        robot.send_message(server_confirmation_code)

        # Receiving client confirmation code from client
        client_confirmation_code = robot.recieve_message()

        # Verifying client confirmation code
        if not valid_syntax(client_confirmation_code, CLIENT_CONFIRMATION_LENGTH):
            robot.send_message(SERVER_SYNTAX_ERROR)
            return False

        if (client_username_hash + CLIENT_KEYS[int(client_key_id)]) % HASH_MODULO != int(client_confirmation_code):
            robot.send_message(SERVER_LOGIN_FAILED)
            return False

        # Sending final response to client
        robot.send_message(SERVER_OK)
        return True

    def communicate(self, sock):
        try:
            robot = connection(sock)

            # Authenticating client
            if not self.authenticate(robot):
                return
            
            # Moving robot
            robot.turn_left()

            curr_x_diff, curr_y_diff = 0, 0
            prev_x_diff, prev_y_diff = 0, 0
            curr_x, curr_y = 0, 0
            prev_x, prev_y = 0, 0
            turned = False

            while True:
                response = robot.recieve_message()

                # Movement    
                if response.split(" ")[0] == CLIENT_OK:

                    if len(response) > CLIENT_OK_LENGTH or response.count(" ") > 2:
                        robot.send_message(SERVER_SYNTAX_ERROR)
                        return

                    prev_x, prev_y = curr_x, curr_y
                    curr_x, curr_y = get_coordinates(response)
                    
                    prev_x_diff, prev_y_diff = curr_x_diff, curr_y_diff
                    curr_x_diff, curr_y_diff = coordinate_diff(prev_x, curr_x), coordinate_diff(prev_y, curr_y)
                    
                    prev_positive_segment = is_positive_segment(prev_x, prev_y)
                    curr_positive_segment = is_positive_segment(curr_x, curr_y)

                    # At target destination
                    if curr_x == 0 and curr_y == 0:
                        robot.pick_up()
                        continue
                    
                    if not turned:
                        # No movement (obstacle in the way)
                        if curr_x_diff == curr_y_diff:
                            if curr_positive_segment:
                                if prev_x_diff < 0:
                                    robot.turn_right()
                                else:
                                    robot.turn_left()

                            else:
                                if prev_y_diff < 0:
                                    robot.turn_left()
                                else:
                                    robot.turn_right()

                        # Moving away from Y axis
                        elif curr_x_diff > 0:
                            if curr_positive_segment:
                                robot.turn_right()
                            else:
                                robot.turn_left()

                        # Moving away from X axis
                        elif curr_y_diff > 0:
                            if curr_positive_segment:
                                robot.turn_left()
                            else:
                                robot.turn_right()

                        # On axis
                        elif curr_x == 0 and not (curr_y_diff < 0):
                            if prev_positive_segment:
                                robot.turn_left()
                            else:
                                robot.turn_right()

                        elif curr_y == 0 and not (curr_x_diff < 0):
                            if prev_positive_segment:
                                robot.turn_right()
                            else:
                                robot.turn_left()

                        else:
                            robot.move()
                            turned = False
                            continue

                        turned = True
                    
                    else:
                        robot.move()
                        turned = False

                # Recharging
                elif response == CLIENT_RECHARGING:
                    print("Recharging")

                elif response == CLIENT_FULL_POWER:
                    print("Full power")

                # Extracting message
                else:
                    if len(response) > CLIENT_MESSAGE_LENGTH:
                        robot.send_message(SERVER_SYNTAX_ERROR)
                        return

                    robot.send_message(SERVER_LOGOUT)
                    break

        except ValueError:
            robot.send_message(SERVER_SYNTAX_ERROR)

        except IndexError:
            robot.send_message(SERVER_KEY_OUT_OF_RANGE_ERROR)

        except socket.timeout:
            print("Socket timed out")

        finally:
            sock.close()
            print("Connection  closed\n")