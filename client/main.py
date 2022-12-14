import json
import socket
from base import *
from req import *
from resp import *
from config import config
from ui import UI
from saveload import refreshUI
import logging
import re
from threading import Thread
import threading
from itertools import cycle
from time import sleep
import sys
from model2 import Model
from env import *
from saveload import *

# logger config
logging.basicConfig(
    # uncomment this will redirect log to file *client.log*
    # filename="client.log",
    format="[%(asctime)s][%(levelname)s] %(message)s",
    filemode="a+",
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Client(object):
    """Client obj that send/recv packet.

    Usage:
        >>> with Client() as client: # create a socket according to config file
        >>>     client.connect()     # connect to remote
        >>> 
    """
    def __init__(self) -> None:
        self.config = config
        self.host = self.config.get("Host")
        self.port = self.config.get("Port")
        assert self.host and self.port, "host and port must be provided"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.model = Model()

    def connect(self):
        if self.socket.connect_ex((self.host, self.port)) == 0:
            logger.info(f"connect to {self.host}:{self.port}")
        else:
            logger.error(f"can not connect to {self.host}:{self.port}")
            exit(-1)
        return

    def send(self, req: PacketReq):
        msg = json.dumps(req, cls=JsonEncoder).encode("utf-8")
        length = len(msg)
        self.socket.sendall(length.to_bytes(8, sys.byteorder) + msg)
        # uncomment this will show req packet
        # logger.info(f"send PacketReq, content: {msg}")
        return

    def recv(self):
        length = int.from_bytes(self.socket.recv(8), sys.byteorder)
        result = b''
        while resp := self.socket.recv(length):
            result += resp
            length -= len(resp)
            if length <= 0:
                break

        # uncomment this will show resp packet
        # logger.info(f"recv PacketResp, content: {result}")
        packet = PacketResp().from_json(result)
        if packet.type == PacketType.ActionResp:
            self.model.env = self.model.env.readEnv(packet.data)
            self.model.actionResp = packet.data
            self.model.input(self.model.env)
        return packet

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.socket.close()
        if traceback:
            print(traceback)
            return False
        return True


def cliGetInitReq1():
    """Get init request from user input."""
    # masterWeaponType = input("Make choices!\nmaster weapon type: [select from {1-2}]: ")
    # slaveWeaponType = input("slave weapon type: [select from {1-2}]: ")
    masterWeaponType = 1
    slaveWeaponType = 2
    return InitReq(
        MasterWeaponType(int(masterWeaponType)), SlaveWeaponType(int(slaveWeaponType))
    )
def cliGetInitReq2():
    """Get init request from user input."""
    # masterWeaponType = input("Make choices!\nmaster weapon type: [select from {1-2}]: ")
    # slaveWeaponType = input("slave weapon type: [select from {1-2}]: ")
    masterWeaponType = 2
    slaveWeaponType = 2
    return InitReq(
        MasterWeaponType(int(masterWeaponType)), SlaveWeaponType(int(slaveWeaponType))
    )



def cliGetActionReq(characterID: int, model):
    """Get action request from user input.

    Args:
        characterID (int): Character's id that do actions.
    """

    def get_action(s: str):
        regex = r"[swedxzauijk]"
        matches = re.finditer(regex, s)
        for match in matches:
            yield match.group()

    str2action = {
        "s": (ActionType.Move, EmptyActionParam()),
        "w": (ActionType.TurnAround, TurnAroundActionParam(Direction.Above)),
        "e": (ActionType.TurnAround, TurnAroundActionParam(Direction.TopRight)),
        "d": (ActionType.TurnAround, TurnAroundActionParam(Direction.BottomRight)),
        "x": (ActionType.TurnAround, TurnAroundActionParam(Direction.Bottom)),
        "z": (ActionType.TurnAround, TurnAroundActionParam(Direction.BottomLeft)),
        "a": (ActionType.TurnAround, TurnAroundActionParam(Direction.TopLeft)),
        "u": (ActionType.Sneaky, EmptyActionParam()),
        "i": (ActionType.UnSneaky, EmptyActionParam()),
        "j": (ActionType.MasterWeaponAttack, EmptyActionParam()),
        "k": (ActionType.SlaveWeaponAttack, EmptyActionParam()),
    }

    actionReqs = []

    condition: threading.Condition = model.condition
    condition.acquire()
    try:
        condition.wait(timeout=1)
        actions = model.output(characterID)
    finally:
        condition.release()

    for s in get_action(actions):
        actionReq = ActionReq(characterID, *str2action[s])
        actionReqs.append(actionReq)

    return actionReqs



def recvAndRefresh(ui: UI, client: Client):
    """Recv packet and refresh ui."""
    global gContext
    resp = client.recv()
    refreshUI(ui, resp)

    if resp.type == PacketType.ActionResp:
        if len(resp.data.characters) and not gContext["gameBeginFlag"]:
            gContext["characterID"] = [
                character.characterID for character in resp.data.characters
            ]
            gContext["playerID"] = resp.data.playerID
            gContext["gameBeginFlag"] = True

    while resp.type != PacketType.GameOver:
        try:
            resp = client.recv()
            refreshUI(ui, resp)
        except:
            pass

    refreshUI(ui, resp)
    print(f"Game Over!")

    for (idx, score) in enumerate(resp.data.scores):
        if gContext["playerID"] == idx:
            print(f"You've got \33[1m{score} score\33[0m")
        else:
            print(f"The other player has got \33[1m{score} score \33[0m")

    if resp.data.result == ResultType.Win:
        print("\33[1mCongratulations! You win! \33[0m")
    elif resp.data.result == ResultType.Tie:
        print("\33[1mEvenly matched opponent \33[0m")
    elif resp.data.result == ResultType.Lose:
        print(
            "\33[1mThe goddess of victory is not on your side this time, but there is still a chance next time!\33[0m"
        )

    gContext["gameOverFlag"] = True
    print("Press any key to exit......")


def main():
    ui = UI()

    with Client() as client:
        client.connect()

        initPacket = PacketReq(PacketType.InitReq, [cliGetInitReq1(), cliGetInitReq2()])
        client.send(initPacket)
        print(gContext["prompt"])

        # IO thread to display UI
        t = Thread(target=recvAndRefresh, args=(ui, client))
        t.start()

        for c in cycle(gContext["steps"]):
            if gContext["gameBeginFlag"]:
                break
            print(
                f"\r\033[0;32m{c}\033[0m \33[1mWaiting for the other player to connect...\033[0m",
                flush=True,
                end="",
            )
            sleep(0.1)

        # IO thread accepts user input and sends requests
        while gContext["gameOverFlag"] is False:
            if not gContext["characterID"]:
                continue
            for characterID in gContext["characterID"]:
                if action := cliGetActionReq(characterID, client.model):
                    actionPacket = PacketReq(PacketType.ActionReq, action)
                    try:
                        client.send(actionPacket)
                    except:
                        pass

        # gracefully shutdown
        t.join()


if __name__ == "__main__":
    main()
