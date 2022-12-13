from base import *
from resp import *
from env import *
import time
import subprocess
from ui import UI
saveloadPath = "./finalData.jsonl"
sequence: int = int(round(time.time() * 1000))

class SaveInfo():
    def __init__(self, actionResp: ActionResp, actions: str):
        self.sequence: int = sequence
        self.actions: str = actions
        self.actionResp: ActionResp = actionResp

def save(actionResp: ActionResp, actions: str, path: str = saveloadPath):
    # 需要每次save有一个特定的序号
    with open(path, 'a+') as file:
        saveInfo: SaveInfo = SaveInfo(actionResp, actions)
        file.write(json.dumps(saveInfo.__dict__, cls=JsonEncoder) + "\n")

def load(path: str):
    # 加载信息
    loadData: list[SaveInfo] = []
    with open(path, 'r') as file:
        for lineStr in file.readlines():
            jsonObj: dict = json.loads(lineStr, cls=JsonEncoder)
            saveInfo: SaveInfo = SaveInfo(jsonObj['actionResp'], jsonObj['actions'])
            saveInfo.sequence = jsonObj['sequence']
            loadData.append(saveInfo)
    return loadData

def getresp(sequence=None):
    with open(saveloadPath, 'r') as file:
        content = file.readlines()[-1200:]
        if sequence == None:
            jsonObj: dict = json.loads(content[-1])
            sequence = jsonObj['sequence']
        for lineStr in content:
            jsonObj: dict = json.loads(lineStr)
            actionResp = ActionResp().from_json(json.dumps(jsonObj['actionResp']))
            saveInfo: SaveInfo = SaveInfo(actionResp, jsonObj['actions'])
            saveInfo.sequence = jsonObj['sequence']
            if saveInfo.sequence == sequence:
                yield saveInfo

def refreshUI(ui: UI, packet: PacketResp):
    """Refresh the UI according to the response."""
    data = packet.data
    if packet.type == PacketType.ActionResp:
        ui.playerID = data.playerID
        ui.color = data.color
        ui.characters = data.characters
        ui.score = data.score
        ui.kill = data.kill
        ui.frame = data.frame

        for block in data.map.blocks:
            if len(block.objs):
                ui.block = {
                    "x": block.x,
                    "y": block.y,
                    "color": block.color,
                    "valid": block.valid,
                    "frame": block.frame,
                    "obj": block.objs[-1].type,
                    "data": block.objs[-1].status,
                }
            else:
                ui.block = {
                    "x": block.x,
                    "y": block.y,
                    "color": block.color,
                    "valid": block.valid,
                    "frame": block.frame,
                    "obj": ObjType.Null,
                }
    subprocess.run(["clear"])
    ui.display()
if __name__ == '__main__':
    '''加载特定一次训练的信息'''
    pass
    # ui = UI()
    # packet =  PacketResp()
    # #model = Model()
    # for saveInfo in getresp():
    #     actionResp = saveInfo.actionResp
    #     packet.data = actionResp
    #     refreshUI(ui,packet)
    #     model.input(actionResp)
    #     st = model.output()
    #     print(f"actionResp = {st}")