from base import *
from resp import *
import time

path = "./finalData.jsonl"

class SaveInfo():
    def __init__(self, actionResp: ActionResp, actions: str):
        self.sequence: int = int(round(time.time() * 1000)) # save的序号
        self.actions: str = actions
        self.actionResp: ActionResp = actionResp

def save(actionResp: ActionResp, actions: str, path: str = path):
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

if __name__ == '__main__':
    '''加载特定一次训练的信息'''
    sequence = 1670844776
    resultSaveInfo: SaveInfo
    with open(path, 'r') as file:
        for lineStr in file.readlines():
            jsonObj: dict = json.loads(lineStr, cls=JsonEncoder)
            saveInfo: SaveInfo = SaveInfo(jsonObj['actionResp'], jsonObj['actions'])
            saveInfo.sequence = jsonObj['sequence']
            if saveInfo.sequence == sequence:
                resultSaveInfo = saveInfo
                break
    print(f"resultSaveInfo = {resultSaveInfo}")