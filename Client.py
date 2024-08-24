from _socket import SHUT_RDWR
from scapy.all import *
import socket
from scapy.layers.inet import UDP, IP
import sys
import colorama
from inputimeout import inputimeout, TimeoutOccurred

colorama.init()
# Constants
UDP_PORT = 13117
MAGIC_COOKIE = 0xabcddcba
OFFER_MESSAGE_TYPE = 0x2


def print_red(text, end='\n', flush=False):
    """Print text in red color."""
    print("\033[31m{}\033[0m".format(text), end=end, flush=flush)


def print_magenta(text, end='\n', flush=False):
    """Print text in magenta color."""
    print("\033[35m{}\033[0m".format(text), end=end, flush=flush)


def print_cyan(text, end='\n', flush=False):
    """Print text in cyan color."""
    print("\033[36m{}\033[0m".format(text), end=end, flush=flush)


def print_green(text):
    """Print text in green color."""
    print("\033[32m{}\033[0m".format(text))


def delete_last_printed_row():
    """Delete the last printed row in the terminal."""
    sys.stdout.write('\033[A')  # Move cursor up one line
    sys.stdout.write('\033[K')  # Clear the line


def connect_and_play(server_ip, tcp_port):
    """Connect to the server via TCP, handle trivia questions.
    Args:
        server_ip (str): IP address of the server.
        tcp_port (int): TCP port number.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        try:
            tcp_socket.connect((server_ip, tcp_port))  # Connect to the server
        except Exception as e:
            print_magenta(e)

        # Receive and calculate the remaining time
        time_left = float(tcp_socket.recv(1024).decode())
        time_left = time_left - time.time()
        print_red("Connected to the server.")

        player_name = None
        # Get player name with timeout
        try:
            print_red("Enter your player name: ")
            player_name = inputimeout(timeout=time_left)
        except TimeoutOccurred:
            print("Timeout, game over")
            tcp_socket.shutdown(socket.SHUT_RDWR)
            tcp_socket.close()
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            tcp_socket.shutdown(socket.SHUT_RDWR)
            tcp_socket.close()
            return None

        if player_name is None:
            tcp_socket.shutdown(SHUT_RDWR)
            tcp_socket.close()
            return

        try:
            tcp_socket.sendall(player_name.encode())  # Send the player name to the server
        except Exception as e:
            print_magenta(e)
            return None

        while True:
            try:
                message = tcp_socket.recv(1024).decode()  # Receive a message from the server
            except socket.timeout:
                print_magenta("Connection timed out waiting for a message from the server.")
                continue
            except (ConnectionAbortedError, OSError) as e:
                print_magenta(e)
                break

            if not message:
                print_red("\nServer has closed the connection.")
                break

            if ("question:" or "invalid input") in message:
                # Extract timestamp and text message
                timestamp, text_message = message.split(" ", 1)
                print_cyan(text_message)  # Print the trivia question
                END_TIME = float(timestamp)
                answer = "TIMEOUT"
                try:
                    # Get user answer with timeout
                    answer = inputimeout(prompt="Your answer (Y/N): ", timeout=END_TIME - time.time())
                except:
                    print_magenta("time out \n")
                try:
                    tcp_socket.sendall(answer.encode())  # Send the answer to the server
                except Exception as e:
                    print_magenta(e)
                    tcp_socket.shutdown(SHUT_RDWR)
                    tcp_socket.close()

            elif "Game over!" in message:
                game_over_message, statistics_message = message.split("Statistics:")
                print_red(game_over_message)
                print_green(statistics_message)
                tcp_socket.shutdown(SHUT_RDWR)
                tcp_socket.close()
                return
            else:
                print_red(message)


# def listen_for_udp_offer_scapy():
#     """
#         Listen for UDP offer messages using Scapy.
#
#         Returns:
#             sender_ip (str): IP address of the sender.
#             tcp_port (int): TCP port number.
#         """
#
#     tcp_port = None
#     sender_ip = None
#
#     def udp_filter(packet):
#         """Filter UDP packets to find offer messages."""
#
#         nonlocal tcp_port, sender_ip
#         if packet.haslayer(UDP) and packet[UDP].dport == UDP_PORT:
#             data = packet[UDP].payload.load
#             if len(data) >= 7:
#                 magic_cookie = int.from_bytes(data[:4], 'big')
#                 message_type = data[4]
#                 if magic_cookie == MAGIC_COOKIE and message_type == OFFER_MESSAGE_TYPE:
#                     tcp_port = int.from_bytes(data[37:39], 'big')
#                     sender_ip = packet[IP].src  # Extracting the IP address of the sender
#                     print_red(f"Offer received from {sender_ip} on port {tcp_port}")
#                     return True  # Indicate that the correct packet was found
#
#     def stop_sniffing(packet):
#         """Stop sniffing when TCP port is set."""
#         return tcp_port is not None  # Stop sniffing if tcp_port is set
#
#     print_red(f"Listening for offers on UDP port {UDP_PORT}...")
#     sniff(filter=f"udp and dst port {UDP_PORT}", prn=udp_filter, stop_filter=stop_sniffing, store=0)
#     delete_last_printed_row()  # Clear the last printed row
#     return sender_ip, tcp_port

def listen_for_udp_offer_scapy():
    """
        Listen for UDP offer messages using the socket module instead of Scapy.

        Returns:
            sender_ip (str): IP address of the sender.
            tcp_port (int): TCP port number.
        """

    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enable port reusability and bind to the broadcast port
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('', UDP_PORT))

    print_red(f"Listening for offers on UDP port {UDP_PORT}...")

    tcp_port = None
    sender_ip = None

    while True:
        message, address = listener.recvfrom(1024)
        print_red(f"Received broadcast from {address}:")

        # Check if the message contains the expected magic cookie and message type
        if len(message) >= 7:
            magic_cookie = int.from_bytes(message[:4], 'big')
            message_type = message[4]
            if magic_cookie == MAGIC_COOKIE and message_type == OFFER_MESSAGE_TYPE:
                tcp_port = int.from_bytes(message[37:39], 'big')  # Adjusted slicing to match Scapy version
                sender_ip = address[0]  # Extracting the IP address of the sender
                print_red(f"Offer received from {sender_ip} on port {tcp_port}")
                break  # Exit loop once the correct packet is found

    return sender_ip, tcp_port


if __name__ == "__main__":
    while True:
        print_red("Client started, listening for offer requests...")
        ip_server, tcp_port = listen_for_udp_offer_scapy()
        if tcp_port:
            print_red(f"Received offer, attempting to connect on port {tcp_port}...")
            connect_and_play(ip_server, tcp_port)
        else:
            print_red("No offer received.")

# python Client.py






