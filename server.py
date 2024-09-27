from colorama import Fore, Style, init
import threading
import socket
import time
import sys

# Configuration constants
PORT = 5050
BUFFER_SIZE = 1024
HOST = socket.gethostbyname(socket.gethostname())
ADDRESS = (HOST, PORT)
ENCODING = "utf-8"
EXIT_COMMAND = "!EXIT"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDRESS)

connected_clients = {}
client_lock = threading.Lock()


def disconnect_client(username, connection):
    """Disconnects a client and removes them from the list."""
    with client_lock:
        if username in connected_clients:
            del connected_clients[username]
            connection.close()


def send_to_all(message, exclude=None, target=None):
    """Sends messages to all connected clients except the sender or to a specific target."""
    with client_lock:
        if target:
            if target in connected_clients:
                try:
                    connected_clients[target].send(message)
                except Exception as e:
                    print(f"Failed to send message to {target}: {e}")
                    disconnect_client(target, connected_clients[target])
        else:
            for client_name, client_socket in connected_clients.items():
                if client_socket != exclude:
                    try:
                        client_socket.send(message)
                    except Exception as e:
                        print(f"Failed to send to {client_name}: {e}")
                        disconnect_client(client_name, client_socket)


def manage_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} joined.")

    try:
        username = conn.recv(BUFFER_SIZE).decode(ENCODING)
        with client_lock:
            connected_clients[username] = conn
        print(f"{username} joined the chat.")

        welcome_message = f"{Fore.GREEN}{username} has entered the chat.{Style.RESET_ALL}".encode(
            ENCODING)
        send_to_all(welcome_message, exclude=conn)

        while True:
            message = conn.recv(BUFFER_SIZE).decode(ENCODING)
            if not message:
                break

            if message == EXIT_COMMAND:
                break

            if "@" in message:
                mentioned = message.split('@')[1].split()[0]
                if mentioned in connected_clients:
                    private_msg = f"{Fore.MAGENTA}[PRIVATE] {message}{Style.RESET_ALL}".encode(
                        ENCODING)
                    send_to_all(private_msg, exclude=conn, target=mentioned)
                    print(f"[PRIVATE] {message}")
                else:
                    error_msg = f"{Fore.RED}User @{mentioned} was not found.{Style.RESET_ALL}".encode(
                        ENCODING)
                    conn.send(error_msg)
            else:
                time_stamp = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime())
                final_msg = f"[{time_stamp}] {message}".encode(ENCODING)
                send_to_all(final_msg, exclude=conn)
                print(f"[{time_stamp}] {message}")

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        disconnect_client(username, conn)
        leave_msg = f"{Fore.RED}{username} has left.{Style.RESET_ALL}".encode(
            ENCODING)
        send_to_all(leave_msg)
        print(f"{username} has left.")


def admin_messages():
    """Server-side input to send messages to clients."""
    while True:
        sys.stdout.write("Admin: ")
        sys.stdout.flush()
        msg = input()
        if msg:
            server_msg = f"{Fore.YELLOW}[SERVER] {msg}{Style.RESET_ALL}".encode(
                ENCODING)
            send_to_all(server_msg)


def initialize_server():
    init()

    print(f"[SERVER STARTED] Listening on {HOST}")
    server_socket.listen()

    admin_thread = threading.Thread(target=admin_messages, daemon=True)
    admin_thread.start()

    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(
            target=manage_client, args=(conn, addr))
        client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[SERVER INITIALIZING]")
initialize_server()