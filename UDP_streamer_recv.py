import socket
import cv2
import numpy as np
import struct
import time

def main():
    PORT = 9050
    BUFFER_SIZE = 8 * 1000
    MAX_PACKET_SIZE = 65450  # Maximum size for a UDP packet

    __udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    __udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    __udp_client_socket.settimeout(5.0)  # Set a timeout for receiving data
    server_address = ('127.0.0.1', PORT)

    __udp_client_socket.sendto(b'Client Request', server_address)

    expected_length = None
    received_data = bytearray()
    total_steps = None
    chunks_received = 0

    while True:
        try:
            chunk, _ = __udp_client_socket.recvfrom(MAX_PACKET_SIZE + 12)
            received_length, chunk_id, total_steps = struct.unpack('iii', chunk[:12])
            
            if expected_length is None:
                expected_length = received_length
            
            if chunk_id == 0:
                received_data = bytearray()
                chunks_received = 0

            received_data.extend(chunk[12:])
            chunks_received += 1

            if chunks_received == total_steps:
                if len(received_data) == expected_length:
                    np_array = np.frombuffer(received_data, dtype=np.uint8)
                    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

                    if frame is not None:
                        cv2.imshow('Received Frame', frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                expected_length = None
                received_data = bytearray()
                chunks_received = 0

        except socket.timeout:
            print("Timeout: No data received.")
            __udp_client_socket.sendto(b'Client Request', server_address)

        except Exception as e:
            print(f"Error receiving data: {e}")
            expected_length = None
            received_data = bytearray()
            chunks_received = 0

    cv2.destroyAllWindows()
    __udp_client_socket.close()

if __name__ == "__main__":
    main()