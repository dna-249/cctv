import socket
import cv2
import pickle
import struct
import threading

host_ip = 'cctv-i1ly.onrender.com'
port = 1000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host_ip, port))
server_socket.listen(5)
print(f"LISTENING AT: {host_ip}:{port}")

def server():
    while True:
        client_socket, addr = server_socket.accept()
        print(f'[CONNECTION] {addr}')

        vid = cv2.VideoCapture(0)
        while vid.isOpened():
            ret, frame = vid.read()
            if not ret:
                break

            data = pickle.dumps(frame)
            message = struct.pack("Q", len(data)) + data
            try:
                client_socket.sendall(message)
            except:
                break

            # Optional: show on server side
            cv2.imshow('TRANSMITTING VIDEO', frame)
            if cv2.waitKey(1) == ord('q'):
                break

        client_socket.close()
        vid.release()
        cv2.destroyAllWindows()

# Start server in a background thread
threading.Thread(target=server, daemon=True).start()