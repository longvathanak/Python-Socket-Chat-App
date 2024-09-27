import socket

# Configuration
PORT = 5050
BUFFER_SIZE = 1024
HOST = socket.gethostbyname(socket.gethostname())
ADDRESS = (HOST, PORT)
ENCODING = "utf-8"
EXIT_COMMAND = "!EXIT"


def create_connection():
    """Creates a connection to the designated server."""
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(ADDRESS)
        print(f"Connected to the server at {ADDRESS}")
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None


def begin_session():
    conn = create_connection()
    if not conn:
        return

    try:
        while True:
            try:
                message = conn.recv(BUFFER_SIZE).decode(ENCODING)
                if message:
                    print(f"{message}")
                else:
                    print("[SERVER] Connection was terminated by the server.")
                    break

                if message == EXIT_COMMAND:
                    print("You have been disconnected from the server.")
                    break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
    except KeyboardInterrupt:
        print("\nSession ended by the user.")
    finally:
        conn.close()
        print("Connection to the server has been closed.")


begin_session()