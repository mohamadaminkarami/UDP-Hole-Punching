import socket

from configs import STUN_SERVER_HOST, STUN_SERVER_PORT
from utils import Address, ProtocolMessages, database


def handle_register(udp_socket: socket.socket, address: Address):
    print(f"Received REGISTER Request From Client: {address}")
    if not database.does_address_exists(address):
        client_id = database.add_client(address)
    else:
        client_id = database.get_id_from_address(address)
    response = ProtocolMessages.REGISTER_ACK + ":" + str(client_id)
    udp_socket.sendto(response.encode(), address)


def handle_list(udp_socket: socket.socket, address: Address):
    print(f"Received LIST Request From Client: {address}")
    list_response = database.get_list_response(excluded_address=address)
    response = ProtocolMessages.LIST_ACK + ":" + list_response
    udp_socket.sendto(response.encode(), address)


def handle_connect(udp_socket: socket.socket, address: Address, requested_id: int):
    requested_address = database.get_address_from_id(requested_id)
    print(database.id_to_address)
    print(
        f"Received CONNECT Request From Client: {address} To Client: {requested_address}"
    )

    response = (
        ProtocolMessages.CONNECT_ACK
        + ":"
        + requested_address[0]
        + ":"
        + str(requested_address[1])
    )
    udp_socket.sendto(response.encode(), address)


def handle_exit(udp_socket: socket.socket, address: Address):
    print(f"Received EXIT Request From client: {address}")
    database.remove_client_by_address(address)
    response = ProtocolMessages.EXIT_ACK
    udp_socket.sendto(response.encode(), address)


def udp_server(host, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("", port))
    print(f"Running STUN Server on {host}:{port}...")

    while True:
        data, address = udp_socket.recvfrom(1024)
        request = data.decode()
        if request == ProtocolMessages.REGISTER:
            handle_register(udp_socket, address)
        elif request == ProtocolMessages.LIST:
            handle_list(udp_socket, address)
        elif request.startswith(ProtocolMessages.CONNECT):
            requested_id = int(request.split(":")[1])
            handle_connect(udp_socket, address, requested_id)
        elif request == ProtocolMessages.EXIT:
            handle_exit(udp_socket, address)


if __name__ == "__main__":
    udp_server(host=STUN_SERVER_HOST, port=STUN_SERVER_PORT)
