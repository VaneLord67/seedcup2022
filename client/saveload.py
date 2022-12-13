from base import *
from resp import *
from env import *
import time

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
        content = file.readlines()
        if sequence == None:
            jsonObj: dict = json.loads(content[-1])
            sequence = jsonObj['sequence']
        for lineStr in content:
            jsonObj: dict = json.loads(lineStr)
            actionResp = ActionResp().from_json(json.dumps(jsonObj['actionResp']))
            saveInfo: SaveInfo = SaveInfo(actionResp, jsonObj['actions'])
            saveInfo.sequence = jsonObj['sequence']
            if saveInfo.sequence != sequence:
                yield saveInfo
