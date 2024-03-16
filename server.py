import socket
import ssl
import os
import threading
HOST = '192.168.100.4'
PORT = 12345
CERTFILE = 'server.crt'
KEYFILE = 'server.key'

user_database = {
    "usr1": "pwd1",
    "usr2": "pwd2"
}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)
server_socket.bind((HOST, PORT))
server_socket.listen()
print('Server listening on {}:{}'.format(HOST, PORT))

def authenticate_user(ssl_socket, addr):
    username = ssl_socket.recv(1024).decode()
    pwd = ssl_socket.recv(1024).decode()
    if username in user_database and user_database[username] == pwd:
        auth_username = username
        ssl_socket.send("success".encode())
        handle_client(ssl_socket, addr, auth_username)
    else:
        ssl_socket.send("failed".encode())
        print(f"{addr} has disconnected")
        ssl_socket.close()
        return False
def get_next_index(client_folder, filename):
    file_name_without_extension, file_extension = os.path.splitext(filename)
    if any(file.startswith(file_name_without_extension) for file in os.listdir(client_folder)):
        index = 1
        while True:
            new_filename = f"{file_name_without_extension}({index}){file_extension}"
            if not os.path.exists(f"{client_folder}/{new_filename}"):
                return new_filename
            index += 1
    else:
        return f"{file_name_without_extension}{file_extension}"
def handle_client(conn, addr, auth_username):
    while True:
        choice = conn.recv(1024).decode()
        if choice == 'client_sending':
            client_folder = f"svr_{auth_username}"
            if not os.path.exists(client_folder):
                os.makedirs(client_folder)
            filename = conn.recv(1024).decode()
            data = conn.recv(4096).decode()
            print("Received data from client")
            filename = get_next_index(client_folder, filename)
            with open(f"{client_folder}/{filename}", 'w') as file:
                file.write(data)
            print(f"Data has been written to {filename}")
            conn.send("Data has been written".encode())
            print("\n")
        elif choice == 'client_receiving':
            filename = conn.recv(1024).decode()
            with open(f"svr_{auth_username}/{filename}", 'r') as file:
                data = file.read()
            conn.send(data.encode())
            print(f"Data has been sent to client with name {auth_username}")
            print("\n")
        elif choice == 'client_delete':
            filename = conn.recv(1024).decode()
            if delete_file(f"svr_{auth_username}", filename):
                conn.send("File deleted successfully.".encode())
            else:
                conn.send("Error deleting file.".encode())
        elif choice == 'client_list':
            files = list_files(f"svr_{auth_username}")
            if files:
                files_str = '\n'.join(files)
                conn.send(files_str.encode())
            else:
                conn.send("No files found.".encode())
        elif choice == "exit":
            conn.close()
            break
def list_files(client_folder):
    try:
        files = os.listdir(client_folder)
        return files
    except OSError as e:
        print(f"Error listing files: {e}")
        return None
def delete_file(client_folder, filename):
    try:
        os.remove(os.path.join(client_folder, filename))
        print(f"File {filename} has been deleted.")
        return True
    except OSError as e:
        print(f"Error deleting file {filename}: {e}")
        return False
try:
    while True:
        conn, addr = server_socket.accept()
        ssl_socket = context.wrap_socket(conn, server_side=True)
        print("Connected by", addr)
        print("\n")
        client_thread = threading.Thread(target=authenticate_user, args=(ssl_socket, addr))
        client_thread.start()
except KeyboardInterrupt:
    print("\nServer interrupted. Closing server socket.")
    server_socket.close()
