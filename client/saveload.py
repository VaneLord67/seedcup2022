from base import *
from resp import *
import time
from model2 import Model
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
def getresp(sequence=None):
    with open(path, 'r') as file:
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
            
if __name__ == '__main__':
    '''加载特定一次训练的信息'''
    model = Model()
    for saveInfo in getresp():
        actionResp = saveInfo.actionResp
        model.input(actionResp)
        st = model.output()
        print(f"actionResp = {st}")