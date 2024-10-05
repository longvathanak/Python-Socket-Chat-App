from colorama import Fore, Style, init
import socket
import threading
import sys

# Configuration constants
PORT = 5050
BUFFER_SIZE = 1024
HOST = socket.gethostbyname(socket.gethostname())
ADDRESS = (HOST, PORT)
ENCODING = "utf-8"
EXIT_COMMAND = "!EXIT"

# Color constants
COLOR_WHITE = Fore.WHITE
COLOR_BLUE = Fore.BLUE
COLOR_RESET = Style.RESET_ALL

def establish_connection():
    """Initiates connection with the server."""
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(ADDRESS)
        print(f"Connected to the server at {ADDRESS}")
        return conn
    except Exception as err:
        print(f"Connection failed: {err}")
        return None

def transmit(conn, message):
    """Sends data to the server and informs the user that an email notification has been sent."""
    try:
        msg_data = message.encode(ENCODING)
        conn.send(msg_data)
        print("Message sent. Email notification will be sent to all users.")
    except Exception as err:
        print(f"Message transmission error: {err}")

def handle_server_responses(conn):
    """Listens for and displays messages from the server."""
    while True:
        try:
            incoming_msg = conn.recv(BUFFER_SIZE).decode(ENCODING)
            if incoming_msg:
                sys.stdout.write("\033[K")  # Clears the line
                sys.stdout.write(f"\r{COLOR_WHITE}{incoming_msg}{COLOR_RESET}\n")
                sys.stdout.write("Type here: ")
                sys.stdout.flush()
            else:
                break
        except Exception:
            break

def send_user_identity(conn, username):
    """Sends the username to the server upon connection."""
    transmit(conn, username)

def input_handler(conn, username):
    """Handles user inputs in a separate thread."""
    send_user_identity(conn, username)

    while True:
        msg_content = input("Type here: ").strip()
        
        if msg_content.lower() == 'q':
            break

        user_msg = f"{COLOR_BLUE}{username}: {msg_content}{COLOR_RESET}"
        transmit(conn, user_msg)

def initiate_client():
    init()

    decision = input('Would you like to initiate a connection (yes/no)? ')
    if decision.lower() != 'yes':
        print("Exiting the client.")
        return

    connection = establish_connection()
    if not connection:
        return

    user_name = input("Enter your preferred username: ").strip()
    if not user_name:
        print("Username cannot be empty. Disconnecting...")
        connection.close()
        return

    receiver_thread = threading.Thread(target=handle_server_responses, args=(connection,))
    receiver_thread.daemon = True
    receiver_thread.start()

    try:
        input_handler(connection, user_name)
    except KeyboardInterrupt:
        print(f"\n{user_name} has disconnected.")
    finally:
        transmit(connection, EXIT_COMMAND)
        connection.close()
        print('Client has been disconnected.')

# Run the client
initiate_client()