import json
import socket
from base import *
from req import *
from resp import *
from config import config
from ui import UI
from ui import mutex
import subprocess
import logging
import re
from threading import Thread
from itertools import cycle
from time import sleep
import sys
from model import *
from pg_agent import *
from pg_model import *
from environment import *
import os

LEARNING_RATE = 1e-3

# logger config
logging.basicConfig(
    # uncomment this will redirect log to file *client.log*
    # filename="client.log",
    format="[%(asctime)s][%(levelname)s] %(message)s",
    filemode="a+",
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

result = []
resultScore = []
gContext: dict[str, Any]

def initGlobalContext():
    # record the context of global data
    global gContext
    gContext = {
        "playerID": None,
        "characterID": [],
        "gameOverFlag": False,
        "prompt": (
            "Take actions!\n"
            "'s': move in current direction\n"
            "'w': turn up\n"
            "'e': turn up right\n"
            "'d': turn down right\n"
            "'x': turn down\n"
            "'z': turn down left\n"
            "'a': turn up left\n"
            "'u': sneak\n"
            "'i': unsneak\n"
            "'j': master weapon attack\n"
            "'k': slave weapon attack\n"
            "Please complete all actions within one frame! \n"
            "[example]: a12sdq2\n"
        ),
        "steps": ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"],
        "gameBeginFlag": False,
        "kill": 0,
    }


class Client(object):
    """Client obj that send/recv packet.

    Usage:
        >>> with Client() as client: # create a socket according to config file
        >>>     client.connect()     # connect to remote
        >>> 
    """
    def __init__(self, port) -> None:
        self.config = config
        self.host = self.config.get("Host")
        if port == None:
            self.port = self.config.get("Port")
        else:
            self.port = port
        assert self.host and self.port, "host and port must be provided"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        return packet

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.socket.close()
        if traceback:
            print(traceback)
            return False
        return True


def cliGetInitReq():
    """Get init request from user input."""
    # masterWeaponType = input("Make choices!\nmaster weapon type: [select from {1-2}]: ")
    masterWeaponType = "2"
    # slaveWeaponType = input("slave weapon type: [select from {1-2}]: ")
    slaveWeaponType = "1"
    return InitReq(
        MasterWeaponType(int(masterWeaponType)), SlaveWeaponType(int(slaveWeaponType))
    )



def cliGetActionReq(characterID: int, env: Environment):
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

    time.sleep(0.1)
    if env.ui_turn:
        return
    mutex.acquire()
    # fileName='log_obs.txt'
    # with open(fileName, 'a+') as file:
    #     print("agent turn", file=file)
    try:
        if env.obs and env.ui.characters[0].isAlive:
            env.action = env.agent.sample(env.obs)
            actions = action_list[env.action]
            done = env.step()
            if done:
                batch_obs = np.array(env.obs_list)
                batch_action = np.array(env.action_list)
                batch_reward = calc_reward_to_go(env.reward_list)
                env.agent.learn(batch_obs, batch_action, batch_reward)
                env.obs_list = []
                env.action_list = []
                env.reward_list = []
        else:
            return
    finally:
        env.ui_turn = True
        mutex.release()

    for s in get_action(actions):
        actionReq = ActionReq(characterID, *str2action[s])
        actionReqs.append(actionReq)

    return actionReqs

def refreshUI(ui: UI, packet: PacketResp):
    """Refresh the UI according to the response."""
    data = packet.data
    if packet.type == PacketType.ActionResp:
        ui.playerID = data.playerID
        ui.color = data.color
        if len(ui.characters) > 0:
            if ui.characters[0].x == data.characters[0].x and ui.characters[0].y == data.characters[0].y:
                ui.moveReward = -5
            else:
                ui.moveReward = 5
            ui.moveCDReward = ui.characters[0].moveCD - data.characters[0].moveCD
            ui.hpReward = ui.characters[0].hp - data.characters[0].hp
        ui.characters = data.characters
        ui.scoreReward = data.score - ui.score
        ui.score = data.score
        ui.killReward = data.kill - ui.kill
        ui.kill = data.kill
        gContext['kill'] = data.kill

        for block in data.map.blocks:
            if len(block.objs):
                ui.block = {
                    "x": block.x,
                    "y": block.y,
                    "color": block.color,
                    "valid": block.valid,
                    "obj": block.objs[-1].type,
                    "data": block.objs[-1].status,
                }
            else:
                ui.block = {
                    "x": block.x,
                    "y": block.y,
                    "color": block.color,
                    "valid": block.valid,
                    "obj": ObjType.Null,
                }
    subprocess.run(["clear"])
    ui.display()


def recvAndRefresh(ui: UI, client: Client):
    """Recv packet and refresh ui."""
    global gContext
    resp = client.recv()
    refreshUI(ui, resp)

    if resp.type == PacketType.ActionResp:
        if len(resp.data.characters) and not gContext["gameBeginFlag"]:
            gContext["characterID"] = resp.data.characters[-1].characterID
            gContext["playerID"] = resp.data.playerID
            client.model.playerID = gContext['playerID']
            gContext["gameBeginFlag"] = True

    while resp.type != PacketType.GameOver:
        resp = client.recv()
        refreshUI(ui, resp)

    refreshUI(ui, resp)
    print(f"Game Over!")

    for (idx, score) in enumerate(resp.data.scores):
        if gContext["playerID"] == idx:
            resultScore.append(score + gContext['kill'] * 10)
            print(f"You've got \33[1m{score} score\33[0m")
        else:
            print(f"The other player has got \33[1m{score} score \33[0m")

    if resp.data.result == ResultType.Win:
        print("\33[1mCongratulations! You win! \33[0m")
        result.append("win")
    elif resp.data.result == ResultType.Tie:
        print("\33[1mEvenly matched opponent \33[0m")
        result.append("tie")
    elif resp.data.result == ResultType.Lose:
        result.append("lose")
        print(
            "\33[1mThe goddess of victory is not on your side this time, but there is still a chance next time!\33[0m"
        )

    gContext["gameOverFlag"] = True
    print("Press any key to exit......")

modelPath = "./pgmodel6.ckpt"
action_list = ["wsjk", "dsjk", "esjk", "xsjk", "zsjk", "asjk"]
action_cnt = len(action_list)

def main(port=None):
    ui = UI()
    env = Environment()
    env.ui: UI = ui
    env.modelPath = modelPath
    ui.env: Environment = env
    obs_dim = 16*16
    act_dim = action_cnt
    logger.info('obs_dim {}, act_dim {}'.format(obs_dim, act_dim))
    # build an agent
    model = PGModel(obs_dim=obs_dim, act_dim=act_dim)
    alg = parl.algorithms.PolicyGradient(model, lr=LEARNING_RATE)
    agent = PGAgent(alg)
    if os.path.exists(modelPath):
        agent.restore(modelPath)
    env.agent = agent

    with Client(port) as client:
        env.client: Client = client
        client.connect()

        initPacket = PacketReq(PacketType.InitReq, cliGetInitReq())
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
        while not gContext["gameOverFlag"]:
            if gContext["characterID"] is None:
                continue

            if action := cliGetActionReq(gContext["characterID"], env):
                if action:
                    actionPacket = PacketReq(PacketType.ActionReq, action)
                    client.send(actionPacket)

        # gracefully shutdown
        t.join()
        agent.save(modelPath)

def calc_reward_to_go(reward_list, gamma=1.0):
    for i in range(len(reward_list) - 2, -1, -1):
        # G_i = r_i + γ·G_i+1
        reward_list[i] += gamma * reward_list[i + 1]  # Gt
    return np.array(reward_list)

if __name__ == "__main__":
    initGlobalContext()
    main()