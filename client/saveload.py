from base import *
from resp import *
from env import *
import time

saveloadPath = "./finalData.jsonl"
sequence: int = int(round(time.time() * 1000))

class SaveInfo():
    def __init__(self, env: Env, actions: str):
        self.actions: str = actions
        self.env: Env = env

def save(env: Env, actions: str, path: str = saveloadPath):
    # 需要每次save有一个特定的序号
    with open(path, 'a+') as file:
        saveInfo: SaveInfo = SaveInfo(env, actions)
        file.write(json.dumps(saveInfo.__dict__, cls=JsonEncoder) + "\n")

def load(path: str):
    # 加载信息
    loadData: list[SaveInfo] = []
    with open(path, 'r') as file:
        for lineStr in file.readlines():
            jsonObj: dict = json.loads(lineStr, cls=JsonEncoder)
            saveInfo: SaveInfo = SaveInfo(jsonObj['env'], jsonObj['actions'])
            loadData.append(saveInfo)

def initSequence():
    with open(saveloadPath, 'a+') as file:
        file.write(str(sequence) + "\n")

if __name__ == '__main__':
    '''加载特定一次训练的信息'''
    findSequence = str(1670860025783) + "\n"
    resultSaveInfo = None
    loadData: list[SaveInfo] = []
    findFlag = False
    with open(saveloadPath, 'r') as file:
        for lineStr in file.readlines():
            if findFlag:
                if len(lineStr) == len(findSequence):
                    break
                jsonObj: dict = json.loads(lineStr)
                saveInfo: SaveInfo = SaveInfo(Env().from_json(json.dumps(jsonObj['env'])), jsonObj['actions'])
                loadData.append(saveInfo)
            if lineStr == findSequence:
                findFlag = True
    print(f"result = {loadData}")