# Interactive Trivia Game Server

![Trivia Game Logo](trivia-game-logo2.png "Logo of the Trivia Game")

This project hosts an interactive trivia game server and client system designed to provide a fun and competitive quiz environment over a network. Users can connect via a client interface, participate in timed trivia rounds, and compete to answer questions correctly.

## Key Features

- **UDP Broadcast for Discovery**: The server uses UDP broadcasting to announce its presence on the network, allowing clients to automatically discover the server without needing to specify an IP address manually.
- **Dynamic TCP Connection Handling**: After clients discover the server through UDP, they connect via TCP. Each client connection is handled in its own thread, allowing multiple clients to connect and interact with the server simultaneously without blocking each other.
- **Multithreaded Game Management**: Each trivia question initiates a new thread for handling responses, ensuring that the server can manage multiple players’ answers concurrently and efficiently. This approach keeps the gameplay smooth and responsive.
- **Dynamic Port Selection**: The server dynamically chooses an available TCP port at startup, enhancing flexibility and easing deployment across various environments. This feature ensures that the server can always start successfully without manual configuration, even if the preferred port is in use.
- **Interactive Trivia Sessions**: Clients receive trivia questions from the server and must respond within a given timeframe. The server evaluates answers in real-time and provides immediate feedback.
- **Scalable Client-Server Architecture**: Designed to scale seamlessly, the server can handle an increasing number of client connections by leveraging Python’s threading capabilities, which are crucial for maintaining performance as the game grows in popularity.

## Technologies Used

- **Python**: The entire backend, both server and client, is implemented in Python.
- **Threading**: Python's threading module is used to handle multiple client connections concurrently.
- **Scapy**: Utilized for listening to UDP broadcast packets in the network detection phase.
- **Socket Programming**: Core network communication between client and server is handled using Python's socket library.

## Project Structure

- **Server.py**: Manages the server operations including UDP broadcasting, TCP connections, and game logic.
- **Client.py**: A client that listens for server broadcasts, connects via TCP, and interacts with the game server.
- **GameStatistics.py**: Handles the recording and updating of game statistics.
- **Bot.py**: A bot client designed to automatically connect to the server and play the game.

## Setup and Installation

Ensure you have Python installed on your system. This project was developed using Python 3.8.

```bash
# Clone the repository
git clone https://github.com/yourusername/trivia-game.git
```
# Navigate to the project directory
cd trivia-game

No additional dependencies are required, just Python 3.

## Running the Application

**Server**  
Run the server using the following command. This starts the server and begins broadcasting its presence on the network:

```bash
python Server.py
```

**Clients**  
To connect a client to the server, use the following command. Ensure the server is running before you start the client:
```bash
python Server.py
```

**Bot Client**  
Optionally, if you want to run a bot client that simulates a player, use the following command:
```bash
python Server.py
```


## Contact
For any inquiries or issues, please open an issue on the GitHub repository or contact the maintainers directly:

Omri Arie – omriarie@gmail.com  
Project Link: https://github.com/omriarie/Trivia-Client-Server

