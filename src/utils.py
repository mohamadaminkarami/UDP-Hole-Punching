import re
from typing import Dict, Tuple

Address = Tuple[str, int]


class ProtocolMessages:
    REGISTER = "REGISTER"
    REGISTER_ACK = "REGISTER_ACK"
    LIST = "LIST"
    LIST_ACK = "LIST_ACK"
    CONNECT = "CONNECT"
    CONNECT_ACK = "CONNECT_ACK"
    EXIT = "EXIT"
    EXIT_ACK = "EXIT_ACK"


class Database:
    def __init__(self) -> None:
        self.id_to_address: Dict[int, Address] = {}
        self.address_to_id: Dict[Address, int] = {}
        self.id = 0

    def does_id_exists(self, id: int) -> bool:
        return id in self.id_to_address

    def does_address_exists(self, address: Address) -> bool:
        return address in self.address_to_id

    def get_id_from_address(self, address: Address) -> int:
        return self.address_to_id[address]

    def get_address_from_id(self, id: int) -> Address:
        return self.id_to_address[id]

    def add_client(self, address: Tuple[str, int]):
        self.id += 1
        self.id_to_address[self.id] = address
        self.address_to_id[address] = self.id

        return self.id

    def get_list_response(self, excluded_address: Address):
        return "\n".join(
            f"{id},{self.id_to_address[id]}"
            for id in self.id_to_address
            if self.id_to_address[id] != excluded_address
        )

    def remove_client_by_address(self, address: Address):
        id = self.address_to_id[address]
        del self.address_to_id[address]
        del self.id_to_address[id]

    @staticmethod
    def parse_message_to_id_to_address(message: str):
        id_to_address = {}
        for row in message.split("\n"):
            matched = re.match("(.+),(.+):(.+)", row)
            id_to_address[matched.group(1)] = (matched.group(2), matched.group(3))

        return id_to_address


database = Database()
