from utils import *
from env import Env
import threading
from saveload import *
from ui import *
import subprocess
def show(ui,map,data):
    ui.playerID = data.playerID
    ui.color = data.color
    ui.characters = data
    ui.score = 0
    ui.kill = 0
    ui.frame = 0
    for block in map.blocks:
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
def cruise(env,flag):
    character = env.us[flag]
    x = character.x
    y = character.y
    pos = (x,y)
    if flag == 0:#角色0
        l1 = line((18,-2),(18,-18))
        l2 = line((18,-18),(2,-18))
        l3 = line((2,-18),(2,-2))
        l4 = line((2,-2),(18,-2))
    if flag == 1:#角色1
        l1 = line((13,-7),(13,-13))
        l2 = line((13,-13),(7,-13))
        l3 = line((7,-13),(7,-7))
        l4 = line((7,-7),(13,-7))
    if pos in l1[:-1]:
        env.dir[flag] = 2
    elif pos in l2[:-1]:
        env.dir[flag] = 1 
    elif pos in l3[:-1]:
        env.dir[flag] = 5
    elif pos in l4[:-1]:
        env.dir[flag] = 4
    else:
        l = list(set(l1+l2+l3+l4))
        mind = 24
        for i in l:
            if distance(pos,i)<= mind:
                mind = distance(pos,i)
                pos2 = i
        env.dir[flag] = goTo(pos,pos2)
    with open('log.txt','a') as f:
        print(pos,flag,env.dir,file=f)
    return s[env.dir[flag]]+'sj'
def findTool(env):
    tool_list = []
    for block in env.map.blocks:
        if len(block.objs) > 0:
            for obj in block.objs:
                if obj.type == ObjType.Item:
                    tool_list.append(block)
    return tool_list
def getool(env,goto,flag):
    env.dir[flag] = goTo(goto[0],goto[1])
    return s[env.dir[flag]]+'sj'
def attackDenfence(env):
    pass
class Model(object):
    def __init__(self):
        self.state = [0,0]#状态机初始化
        self.goto = [[(0,0),(0,0)],[(0,0),(0,0)]]
        self.result = []
        self.env = Env()
        self.condition = threading.Condition()
    def input(self,env: Env):
        self.env = env
        tool = findTool(env)
        if len(tool):
            for t in tool:
                pos1 = (env.us[0].x,env.us[0].y)
                pos2 = (env.us[1].x,env.us[1].y)
                post = (t.x,t.y)
                if distance(pos1,post)<distance(pos2,post):
                    id = env.us[0].characterID
                    pos = pos1
                else:
                    id = env.us[1].characterID
                    pos = pos2
                self.state[id] = 1
                self.goto[id] = [pos,post]
        else:
            self.state = [0,0]

    def output(self,characterID):
        if characterID==0:
            output = ['','']
            for flag, state in enumerate(self.state):
                if state == 0:
                    output[flag] = cruise(self.env,flag)#巡航
                if state == 1:
                    output[flag] = getool(self.env,self.goto[flag],flag)#得道具
                if state == 2:
                    output[flag] = attackDenfence(self.env,flag)
            save(self.env, output)
            self.result = output
            return self.result[characterID]
        else:
            return self.result[characterID]
def getenv():
    findSequence = str(1670912505775) + "\n"
    findFlag = False
    with open(saveloadPath, 'r') as file:
        #findSequence = file.readline()
        for lineStr in file.readlines():
            if findFlag:
                if len(lineStr) == len(findSequence):
                    break
                jsonObj: dict = json.loads(lineStr)
                saveInfo: SaveInfo = SaveInfo(Env().from_json(json.dumps(jsonObj['env'])), jsonObj['actions'])
                yield saveInfo
            if lineStr == findSequence:
                findFlag = True
if __name__ == '__main__':
    '''加载特定一次训练的信息'''
    # model = Model()
    # ui = UI()
    # characterID = 0
    # #print(f"result = {saveInfos}")
    # for saveInfo in getenv():
    #     env = saveInfo.env
 
    #     #show(ui,env.map,env.us[0])
    #     model.input(env)
    #     st = model.output(characterID)
    #     print(f"actions = {st}")
    for result in getresp(1670916270881):
        print(result)