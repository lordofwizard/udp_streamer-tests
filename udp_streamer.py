from itertools import count
import socket
import cv2
import numpy as np
import struct
import time

def main():
    # Initialize the camera capture
    capture = cv2.VideoCapture("rotated_rigbetel.mp4")  # Use 0 for the default camera
    PORT = 9050
    BUFFER_SIZE = 8 * 1000
    RESTART_THRESHOLD = 2  # in seconds
    MAX_PACKET_SIZE = 65450  # Maximum size for a UDP packet

    # Set the desired image width and height
    width = 1280
    height = 720
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    __udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    __udp_server_socket.bind(('0.0.0.0', PORT))
    address = None
    last_received_time = time.time()

    while True:
        # Read a frame from the camera
        ret, frame = capture.read()

        # Convert the frame to a byte array
        _, img_bytes = cv2.imencode('.jpg', frame)
        img_byte_array = np.array(img_bytes).tobytes()
        arrlen = len(img_byte_array)
        timestamp = time.time()  # Add timestamp
        img_byte_array_with_length = struct.pack('dI', timestamp, arrlen) + img_byte_array

        if address is None:
            _, address = __udp_server_socket.recvfrom(BUFFER_SIZE)
            last_received_time = time.time()

        try:
            # Split the data into smaller chunks and send them separately
            totalstepsrequired = 0
            for i in range(0, len(img_byte_array), MAX_PACKET_SIZE):
                totalstepsrequired += 1

            count = 0
            for i in range(0, len(img_byte_array), MAX_PACKET_SIZE):
                chunk = img_byte_array_with_length[i:i + MAX_PACKET_SIZE]
                chunkwithcunkId = struct.pack('i', count) + struct.pack('i', totalstepsrequired) + chunk
                __udp_server_socket.sendto(chunkwithcunkId, address)
                count += 1
        except socket.error as e:
            print("UDP send error:", e)
            __udp_server_socket.close()
            __udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            __udp_server_socket.bind(('0.0.0.0', PORT))
            address = None
            last_received_time = time.time()
            continue

        print(address)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera capture and close the window
    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
