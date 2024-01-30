import re
import socket
import sys
import threading
from time import sleep

from configs import STUN_SERVER_HOST, STUN_SERVER_PORT
from utils import Address, ProtocolMessages

message = ""


def get_registered_ids(udp_socket: socket.socket, server_address: Address):
    request = ProtocolMessages.LIST
    udp_socket.sendto(request.encode(), server_address)


def request_connect(udp_socket: socket.socket, server_address: Address, requested_id):
    request = ProtocolMessages.CONNECT + ":" + str(requested_id)
    udp_socket.sendto(request.encode(), server_address)


def request_exit(udp_socket: socket.socket, server_address: Address):
    request = ProtocolMessages.EXIT
    udp_socket.sendto(request.encode(), server_address)


def send_message_to_requested_client(udp_socket: socket.socket, response: str):
    response_splitted = response.split(":")
    requested_client = (response_splitted[1], int(response_splitted[2]))
    global message
    udp_socket.sendto(message.encode(), requested_client)


def print_list(response: str):
    for row in response.split(":")[1].split("\n"):
        print(row)


def handle_coming_messages(udp_socket: socket.socket):
    while True:
        data, address = udp_socket.recvfrom(1024)
        response = data.decode()
        if response.startswith(ProtocolMessages.LIST_ACK):
            print_list(response)
        elif response.startswith(ProtocolMessages.CONNECT_ACK):
            send_message_to_requested_client(udp_socket, response)
        elif response == ProtocolMessages.EXIT_ACK:
            sys.exit(0)
        else:
            print(f"Received Incoming Message From {address}: {response}")


def interact_with_user(
    udp_socket: socket.socket, server_address: Address, client_id: int
):
    while True:
        sleep(0.01)
        print("Choose:\n1.MY ID\n2.LIST\n3.CONNECT\n4.EXIT")
        chosen = input()

        if chosen in ["1", "MY ID"]:
            print(f"Your ID is: {client_id}")
        elif chosen in ["2", "LIST"]:
            get_registered_ids(udp_socket, server_address)
        elif chosen in ["3", "CONNECT"]:
            requested_id = input("Enter the id of client you want to connect: ")
            global message
            message = input("Enter the message you want to send: ")
            request_connect(udp_socket, server_address, requested_id)
        elif chosen in ["4", "EXIT"]:
            request_exit(udp_socket, server_address)
            sys.exit(0)


def register_client(udp_socket: socket.socket, server_address: Address):
    while True:
        request = ProtocolMessages.REGISTER
        udp_socket.sendto(request.encode(), server_address)
        data, from_address = udp_socket.recvfrom(1024)
        matched = re.match(f"{ProtocolMessages.REGISTER_ACK}:(.+)", data.decode())
        if from_address == server_address and matched:
            client_id = matched.group(1)
            print(f"You Have Been Registered SuccessFully. Your Id is: {client_id}")
            return client_id


def handle_client(server_host: str, server_port: int):
    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (server_host, server_port)
    client_id = register_client(udp_socket, server_address)

    t1 = threading.Thread(
        target=interact_with_user,
        args=(udp_socket, server_address, client_id),
    )
    t2 = threading.Thread(
        target=handle_coming_messages,
        args=(udp_socket,),
    )
    t1.start()
    t2.start()

    t1.join()
    t2.join()


if __name__ == "__main__":
    handle_client(
        server_host=STUN_SERVER_HOST,
        server_port=STUN_SERVER_PORT,
    )
