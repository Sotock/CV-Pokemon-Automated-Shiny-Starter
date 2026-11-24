import socket

with socket.create_connection(("127.0.0.1", 8765), timeout=5) as connection:
    connection.sendall(b"START")

print("START command sent.")