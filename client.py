import socket
import ssl
import os 
HOST = '192.168.100.4'
PORT = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
ssl_socket = context.wrap_socket(client_socket, server_hostname=HOST)
ssl_socket.connect((HOST, PORT))

username = input("Enter your username: ")
pwd = input("Enter the password: ")
ssl_socket.send(username.encode())
ssl_socket.send(pwd.encode())
client_ip=ssl_socket.getsockname()[0]
auth = ssl_socket.recv().decode()
if auth == "failed":
    print("Authentication failed")
    ssl_socket.close()
    exit()
print("\nAuthenticated successfully")
def read_data_from_file(filename):
    try:
        with open(filename, 'r') as file:
            data = file.read()
        return data
    except Exception as e:
        print("Error reading data from file:", e)
        return None
while True:
    print("\n")
    print("What do you want to do:")
    print("1. Send data to server")
    print("2. Receive data from server")
    print("3. Delete file on server")
    print("4. View list of files on server")
    print("5. Exit")
    choice = input("Enter your choice as an integer: ")
    if choice == '1':
        ssl_socket.send("client_sending".encode())
        input_file = input("Enter the file name you want to store on the server: ")
        ssl_socket.send(input_file.encode())
        data_to_send = read_data_from_file(input_file)
        if data_to_send is not None:
            ssl_socket.sendall(data_to_send.encode())
            print("\nFile is sent to server")
            ack = ssl_socket.recv(1024).decode()
            print("Server acknowledgment:", ack)
    elif choice == '2':
        ssl_socket.send("client_receiving".encode())
        filename = input("Enter the filename to access: ")
        ssl_socket.send(filename.encode())
        data = ssl_socket.recv(4096).decode()
        client_folder = f"client_{client_ip}"
        if not os.path.exists(client_folder):
            os.makedirs(client_folder)
        with open(f"client_{client_ip}/{filename}", 'w') as file:
            file.write(data)
        print("\nData has been received from server and saved")
    elif choice == '3':
        ssl_socket.send("client_delete".encode())
        filename = input("Enter the filename to delete: ")
        ssl_socket.send(filename.encode())
        delete_response = ssl_socket.recv(1024).decode()
        print(delete_response)
    elif choice == '4':
        ssl_socket.send("client_list".encode())
        file_list = ssl_socket.recv(4096).decode()
        print("List of files on server:")
        print(file_list)
    elif choice == '5':
        ssl_socket.send("exit".encode())
        ssl_socket.close()
        break
