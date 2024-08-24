from scapy.layers.inet import UDP, IP
import names
import colorama
colorama.init()
from scapy.all import *
from _socket import SHUT_RDWR

# Constants
UDP_PORT = 13117  # UDP port number
MAGIC_COOKIE = 0xabcddcba  # Magic cookie for identifying offer messages
OFFER_MESSAGE_TYPE = 0x2  # Offer message type


def delete_last_printed_row():
    """Delete the last printed row in the terminal"""
    sys.stdout.write('\033[A')  # Move cursor up one line
    sys.stdout.write('\033[K')  # Clear the line


def listen_for_udp_offer_scapy():
    """
        Listen for UDP offer messages using Scapy.

        Returns:
            server_ip (str): IP address of the server.
            tcp_port (int): TCP port number.
        """

    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enable port reusability and bind to the broadcast port
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('', UDP_PORT))

    print_blue(f"Listening for offers on UDP port {UDP_PORT}...")

    tcp_port = None
    sender_ip = None

    while True:
        message, address = listener.recvfrom(1024)
        print_blue(f"Received broadcast from {address}:")

        # Check if the message contains the expected magic cookie and message type
        if len(message) >= 7:
            magic_cookie = int.from_bytes(message[:4], 'big')
            message_type = message[4]
            if magic_cookie == MAGIC_COOKIE and message_type == OFFER_MESSAGE_TYPE:
                tcp_port = int.from_bytes(message[37:39], 'big')  # Adjusted slicing to match Scapy version
                sender_ip = address[0]  # Extracting the IP address of the sender
                print_blue(f"Offer received from {sender_ip} on port {tcp_port}")
                break  # Exit loop once the correct packet is found

    return sender_ip, tcp_port


def connect_and_play(server_ip, tcp_port):
    """Connect to the server via TCP, handle trivia questions.

    Args:
        server_ip (str): IP address of the server.
        tcp_port (int): TCP port number

    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        try:
            tcp_socket.connect((server_ip, tcp_port))  # Connect to the server
        except:
            return None
        _ = float(tcp_socket.recv(1024).decode())  # Receive and discard initial server message
        print_blue("Connected to the server.")
        print_blue("enter your name ")
        player_name = "BOT " + names.get_first_name(gender="female")  # Generate a random BOT name
        time.sleep(2)
        try:
            tcp_socket.sendall(player_name.encode())  # Send the BOT name to the server
        except Exception as e:
            print_magenta(e)
            return None
        print(player_name.encode().decode())

        while True:
            try:
                message = tcp_socket.recv(1024).decode()  # Receive a message from the server
            except socket.timeout:
                print_magenta("Connection timed out waiting for a message from the server.")
                break
            except (ConnectionAbortedError, OSError) as e:
                print_magenta(e)
                break

            if not message:
                print_blue("Server has closed the connection.")
                break

            if "question:" in message:
                timestamp, text_message = message.split(" ", 1)  # Split message into timestamp and text
                print_cyan(text_message)  # Print the trivia question
                print_blue("Your answer (Y/N): ")
                answer = random.choice(["Y", "N"])  # Generate a random answer
                print(answer)
                time.sleep(2)
                try:
                    tcp_socket.sendall(answer.encode())  # Send the answer to the server
                except Exception as e:
                    print_magenta(e)
                    tcp_socket.shutdown(SHUT_RDWR)
                    tcp_socket.close()
            elif "Game over!" in message:
                game_over_message, statistics_message = message.split("Statistics:")
                print_blue(game_over_message)
                print_green(statistics_message)
                break
            else:
                print_blue(message)


def print_blue(text, end='\n', flush=False):
    """Print text in blue color."""
    print("\033[34m{}\033[0m".format(text), end=end, flush=flush)


def print_magenta(text, end='\n', flush=False):
    """Print text in magenta color."""
    print("\033[35m{}\033[0m".format(text), end=end, flush=flush)


def print_cyan(text, end='\n', flush=False):
    """Print text in cyan color."""
    print("\033[36m{}\033[0m".format(text), end=end, flush=flush)

def print_green(text):
    """Print text in green color."""
    print("\033[32m{}\033[0m".format(text))


if __name__ == "__main__":
    while True:
        print_blue("Client started, listening for offer requests with Scapy...")
        server_ip, tcp_port = listen_for_udp_offer_scapy()
        if tcp_port:
            print_blue(f"Received offer, attempting to connect on port {tcp_port}...")
            connect_and_play(server_ip, tcp_port)
        else:
            print_blue("No offer received.")
