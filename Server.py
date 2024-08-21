import socket
from GameStatistics import *
import time
import threading
import copy
import random
import colorama

# Global variables
colorama.init()
last_player_connection_time = time.time()
connected_players = []
in_game_players = []
broadcasting = True
broadcast_end_event = threading.Event()
statistics = GameStatistics()


def print_green(text):
    """Print text in green color."""
    print("\033[32m{}\033[0m".format(text))


def print_magenta(text, end='\n', flush=False):
    """Print text in magenta color."""
    print("\033[35m{}\033[0m".format(text), end=end, flush=flush)


def player_thread(player, first_M, message, correct_answer, end_time, lock):
    """Thread function to handle each player's trivia question."""
    flag = False
    temp_message = message
    first = True
    while not flag:
        try:
            if first:
                message = first_M + message
                first = False
            t_mass = str(end_time) + " " + message
            player['socket'].sendall(t_mass.encode())
            message = temp_message
            answer = player['socket'].recv(1024).decode().strip()
        except Exception as e:
            print_magenta(f"Error in player_thread for {player['name']}: {e}")
            player['socket'] = False
            return

        if answer != "TIMEOUT":
            print_green(f"{player['name']} answer " + answer + "\n")

        with lock:
            if answer == "TIMEOUT":
                print_green(f"Player {player['name']} timed out.")
                player['answered'] = True
                player['correct'] = False
                flag = True
            elif not answer in ["Y", "T", "1", "N", "F", "0"]:

                print_green(f"Player {player['name']} provided invalid input.")
                player['answered'] = True
                player['correct'] = False
                message = " invalid input try again...\n" + message

            else:
                correct = (answer in ["Y", "T", "1"] and correct_answer) or (
                        answer in ["N", "F", "0"] and not correct_answer)
                player['answered'] = True
                player['correct'] = correct
                statistics.update_player_performance(player)
                statistics.update_typed_characters(answer)
                response = f"{player['name']} is {'correct' if player['correct'] else 'incorrect'}!\n"
                print_green(response)
                flag = True


def start_trivia_round():
    """Starts a round of trivia questions."""
    global connected_players
    trivia_questions = [
        ("True or false: Bees play a crucial role in pollination?", True),
        ("True or false: Dolphins are highly intelligent marine mammals?", True),
        ("True or false: Owls are nocturnal birds of prey?", True),  # Fixed quotation marks here
        ("True or false: Trees absorb carbon dioxide and release oxygen during photosynthesis?", True),
        ("True or false: Penguins are flightless birds that primarily inhabit the Southern Hemisphere?", True),
        ("True or false: Elephants are the largest land animals on Earth?", True),
        ("True or false: Monarch butterflies undergo a long-distance migration each year?", True),
        ("True or false: Honey is produced by bees from nectar collected from flowers?", True),
        ("True or false: Coral reefs are biodiversity hotspots found in tropical marine environments?", True),
        ("True or false: Wolves are social animals that live in packs?", True),
        ("True or false: Sharks are mammals?", False),
        ("True or false: Cacti thrive in moist environments?", False),
        ("True or false: All snakes are venomous?", False),
        ("True or false: Spiders have six legs?", False),
        ("True or false: Bears primarily feed on plants and berries?", False),
        ("True or false: Alligators are native to Europe?", False),
        ("True or false: Venus flytraps capture prey using scent and color?", False),
        ("True or false: Penguins can fly?", False),
        ("True or false: Sunflowers always face east?", False),
        ("True or false: Kangaroos are native to Africa?", False)
        # Add more questions as needed
    ]

    for player in connected_players:
        player['answered'] = False
        player['correct'] = False

    random.shuffle(trivia_questions)
    lock = threading.Lock()
    in_game_players = copy.copy(connected_players)
    correct_players = []
    counter = 1

    for question, correct_answer in trivia_questions:
        in_game_players[:] = [p for p in in_game_players if p['socket']]
        connected_players[:] = [p for p in in_game_players if p['socket']]
        if len(in_game_players) < 2:
            break
        names = [player['name'] for player in in_game_players]
        played_by = ','.join(names)
        round_and_names = f"round {counter}   played by: {played_by}"
        message = f"\nfollowing question: {question} \n"

        print_green(round_and_names + message)

        threads = []
        counter += 1
        end_time = time.time() + 10

        for player in in_game_players:
            player_thread_instance = threading.Thread(target=player_thread, args=(
                player, round_and_names, message, correct_answer, end_time, lock))
            threads.append(player_thread_instance)
            player_thread_instance.start()

        for thread in threads:
            thread.join()

        # Check the answer status of all players
        correct_players = [p for p in in_game_players if p['correct'] == True]
        in_correct_players = [p for p in in_game_players if p['correct'] == False]

        if len(in_correct_players) == len(in_game_players):
            continue
        else:
            in_game_players[:] = [p for p in in_game_players if p.get('correct', False)]
            if len(in_game_players) == 1:
                break
            else:
                continue

    game_over_message = "\nGame over! "

    if len(in_game_players) == 1 and len(connected_players) > 1:
        game_over_message += f"Congratulations to the winner: {in_game_players[0]['name']}\n"
    else:
        game_over_message += "No winners this round.\n"

    if len(in_game_players) > 1:
        game_over_message += "tie go home"
    print_green(game_over_message)
    statistics.write_statistics_to_file()
    statistics.print_statistics()

    game_over_message = game_over_message + statistics.get_statistics()
    game_over_message_lose = "you lose!! :(  " + game_over_message
    game_over_message_won = "you won!! :)  " + game_over_message

    for player in connected_players:
        if player in correct_players:
            try:
                player['socket'].sendall(game_over_message_won.encode())
            except Exception as e:
                print_magenta(f"Error sending game over message to {player['name']}: {e}")
        else:
            try:
                player['socket'].sendall(game_over_message_lose.encode())
            except Exception as e:
                print_magenta(f"Error sending game over message to {player['name']}: {e}")


def send_message_to_player(player_socket, message):
    """Send a message to a specific player."""
    try:
        player_socket.sendall(message.encode())
    except Exception as e:
        print_magenta(f"Error sending message to player: {e}")


def broadcast_welcome_message(server_name):
    """Sends a welcome message to all connected players."""

    message = "Welcome to the " + server_name + ", where we are answering trivia questions about animals and nature.\n"
    for i, player in enumerate(connected_players, 1):
        message += f"Player {i}: {player['name']}\n"
    for player in connected_players:
        try:
            player['socket'].sendall(message.encode())
        except Exception as e:
            print_magenta(f"Error sending welcome message to {player['name']}: {e}")


def broadcast_message(server_name, tcp_port):
    """Sends a broadcast message with a specific packet format."""
    magic_cookie = 0xabcddcba.to_bytes(4, byteorder='big')
    message_type = (0x2).to_bytes(1, byteorder='big')
    server_name_encoded = server_name.encode('utf-8')
    server_name_padded = server_name_encoded.ljust(32, b'\x00')
    server_port_bytes = tcp_port.to_bytes(2, byteorder='big')
    packet = magic_cookie + message_type + server_name_padded + server_port_bytes
    return packet


def create_udp_broadcast_socket():
    """Creates and configures a UDP socket for broadcasting."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return udp_socket


def start_broadcasting(server_name, tcp_port, udp_port=13117):
    """Starts broadcasting UDP packets to discover clients."""

    global broadcasting
    time.sleep(0.5)
    udp_socket = create_udp_broadcast_socket()
    spacial_packet = broadcast_message(server_name, tcp_port)
    try:
        while broadcasting:
            current_time = time.time()
            if current_time > last_player_connection_time + 10:
                print_green("No new players for 10 seconds, stopping broadcasting.\n starting the game....\n")
                broadcasting = False
                broadcast_end_event.set()  # Signal that the broadcasting phase has ended
                broadcast_welcome_message(server_name)  # Send the welcome message after the event is set
                break
            udp_socket.sendto(spacial_packet, ("<broadcast>", udp_port))
            print_green(f"Broadcast packet sent to port:{udp_port}")
            time.sleep(1)
    except KeyboardInterrupt:
        print_magenta("Broadcasting stopped.")
    finally:
        udp_socket.close()


def handle_client_connection(client_socket):
    """Handles a new client connection."""
    global last_player_connection_time, connected_players
    try:
        client_socket.sendall(str(last_player_connection_time + 10).encode())
        player_name = client_socket.recv(1024).decode().strip()
        if player_name == "E":
            pass
        elif player_name:
            connected_players.append({'socket': client_socket, 'name': player_name})
            print(f"Player {player_name} connected.")
            last_player_connection_time = time.time()  # Update for the last connection
    except Exception as e:
        print_magenta(f"Error handling connection: {e}")


def accept_tcp_connections(tcp_port):
    """Accepts incoming TCP connections from clients."""
    global broadcasting
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.bind(('', tcp_port))
    tcp_socket.listen()
    print_green(f"TCP Server listening on port {tcp_port}")

    while not broadcast_end_event.is_set():
        tcp_socket.settimeout(1)  # Set a timeout for the accept call to periodically check the event
        try:
            client_socket, _ = tcp_socket.accept()
        except socket.timeout:
            continue  # Continue checking the event if the accept call times out
        client_thread = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_thread.start()


def find_available_port():
    """Find an available TCP port for the server to use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def initialize_global_variables():
    """Initialize/reset global variables."""
    global last_player_connection_time, connected_players, in_game_players, broadcasting, broadcast_end_event, statistics
    last_player_connection_time = time.time()
    connected_players = []
    in_game_players = []
    broadcasting = True
    broadcast_end_event = threading.Event()  # Re-create the event to reset its state
    statistics = GameStatistics()  # Assuming GameStatistics is defined elsewhere and resettable like this


if __name__ == "__main__":
    while True:
        initialize_global_variables()
        server_name = "YALA BALAGAN " + str(random.choice([x for x in range(1000)]))
        print_green(server_name)
        tcp_port = find_available_port()
        threading.Thread(target=accept_tcp_connections, args=(tcp_port,)).start()
        start_broadcasting(server_name, tcp_port)
        start_trivia_round()


