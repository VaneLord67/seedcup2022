from utils import *
from env import Env
import threading
from saveload import *
from ui import *
import subprocess
import time

def fill_block(env,flag):
    count = [0,0,0,0,0,0]
    pos = (env.us[flag].x,env.us[flag].y)
    minpos =[(24,24),(24,24),(24,24),(24,24),(24,24),(24,24),(24,24)]
    for block in env.map.blocks:
        if block.valid == True and (block.x,block.y)!=(0,0):
            if not (block.color == env.us[0].color and env.frame == block.frame):
                if pos != (block.x,block.y):
                    a = goTo(pos , (block.x,block.y))
                else:
                    a = 1
                count[a]+=1 
                if 0 < distance(pos,(block.x,block.y))<=distance(pos,minpos[a]):
                    minpos[a] = (block.x,block.y)
                    if distance(pos,minpos[a]) <= distance(pos,minpos[6]):
                        minpos[6] = minpos[a]
    for i in range(len(count)):
        if count[i] == max(count):
            break
    if count[i]>50 :
        minpos = minpos[i]
    else:
        minpos = minpos[6]
    a = goTo(pos , minpos)
    # if env.us[flag].masterWeapon.weaponType == 1:
    #     mudi = mweapon1(pos,a)
    # else:
    #     mudi = mweapon2(pos,a)
    if (env.us[flag].masterWeapon.attackCDLeft == 0):
        return s[a]+'j'
    if (env.us[flag].moveCDLeft == 0) and distance(pos,minpos) != 1:
        return s[a]+'s'

    return s[a]
def circle(r = 6,reverse = 0):#从2开始
    x = 20 -r#18
    y = r#2
    l1 = line((x,-y),(x,-x))
    l2 = line((x,-x),(y,-x))
    l3 = line((y,-x),(y,-y))
    l4 = line((y,-y),(x,-y))
    if reverse == 0:
        road = [(l1[:-1],2),(l2[:-1],1),(l3[:-1],5),(l4[:-1],4)]
    else:
        road = [(l1[1:],5),(l2[1:],4),(l3[1:],2),(l4[1:],1)]
    return road
def cruise(env,flag):
    character = env.us[flag]
    x = character.x
    y = character.y
    pos = (x,y)
    env.dir[flag] = None
    if env.us[flag].moveCD == 4:
        rd = 5
    if env.us[flag].moveCD == 3:
        rd = 1
    if env.us[flag].moveCD == 2:
        rd = 4
    if env.us[flag].moveCD == 1:
        rd = 7
    if flag == 0:
        road = circle(rd)
    if flag == 1:#角色1
        road = circle(rd,reverse=1)
    l = []
    for r in road:
        if pos in r[0]:
            env.dir[flag] = r[1]
        l.extend(r[0])
    if env.dir[flag] == None:
        l = list(set(l))

        mind = 24
        for i in l:
            if distance(pos,i)<= mind:
                mind = distance(pos,i)
                pos2 = i
        env.dir[flag] = goTo(pos,pos2)


    output = s[env.dir[flag]]

    if env.us[flag].moveCDLeft == 0:
        output += 's'
    if env.us[flag].masterWeapon.attackCDLeft == 0:#使用主武器
        output += 'j'
    # if env.us[flag].moveCD <= 2:
    #     output = fill_block(env,flag)

    return output


def findTool(env):
    tool_list = []
    for block in env.map.blocks:
        if len(block.objs) > 0:
            for obj in block.objs:
                if obj.type == ObjType.Item:
                    tool_list.append(block)
    return tool_list


def toolPick(env,tool_list):
    blood = []
    speed = []
    goto = [[(0,0),(0,0)],[(0,0),(0,0)]]
    state = [0,0]
    for t in tool_list:
        if t.objs[0].type==2:#如果是buff
            if t.objs[0].status.buffType == BuffType.BuffHp:
                blood.append(t)
            else:
                speed.append(t)
    for c in env.us:
        tool = None
        if c.moveCD != 1:
            mds = 100
            for sp in speed:
                if mds > distance((c.x,c.y),(sp.x,sp.y)):
                    mds = distance((c.x,c.y),(sp.x,sp.y)) 
                    if mds > 8:
                        tool = None
                    else:
                        tool = sp      
        if c.hp != 100:#血量优先级大于speed
            mdb = 100
            for b in blood:
                if mdb > distance((c.x,c.y),(b.x,b.y)):
                    mdb = distance((c.x,c.y),(b.x,b.y)) 
                    if mdb > 8:
                        tool = None
                    else:
                        tool = b  
        if tool:
            post = (tool.x,tool.y)
            goto[c.characterID] = [(c.x,c.y),post]
            state[c.characterID] = 1
    return state,goto

  
def getool(env,goto,flag):
    a = goTo(goto[flag][0],goto[flag][1])
    if env.us[flag].masterWeapon.attackCDLeft == 0:
        return s[a] + 'j'
    if env.us[flag].moveCDLeft == 0:
        return s[a] + 's'
    return s[a]

def keep_distance(env,goto,flag,dis):
    a = goTo(goto[flag][0],goto[flag][1])    
    if distance(goto[flag][0],goto[flag][1]) == dis:
        for enemy in env.enemy:
            if (enemy.x,enemy.y) == goto[flag][1] and enemy.isGod == True:
                return s[a]
        if env.us[flag].moveCDLeft == 0 and env.us[flag].masterWeapon.attackCDLeft == 0 :
            return s[a]+'s'+'j'
        else:
            return s[a]
    elif distance(goto[flag][0],goto[flag][1]) < dis:
        if env.us[flag].moveCDLeft == 0:
            if env.us[flag].slaveWeapon.attackCDLeft == 0:#使用副武器
                return 'k' + s[(a-3)%6]+'s'
            return s[(a-3)%6]+'s'
        if env.us[flag].masterWeapon.attackCDLeft == 0:
            return s[a]+'j'
        return s[a]
    else:
        if env.us[flag].moveCDLeft == 0:
            return s[a]+'s'
        return s[a]
def run_away(env,goto,flag,dis):
    a = goTo(goto[flag][0],goto[flag][1]) 
    if distance(goto[flag][0],goto[flag][1]) <= dis:
        return s[(a-3)%6]+'s'
    return ''
    
class Model(object):
    def __init__(self):
        self.state = [0,0]#状态机初始化
        self.goto = [[(0,0),(0,0)],[(0,0),(0,0)]]
        self.result = []
        self.env = Env()
        self.actionResp = None
        self.condition = threading.Condition()
        self.frame: int = -1
        with open('log_output.txt','w') as f:
            pass
        
    def input(self,env: Env):
        a = time.time()
        self.env = env
        tool_list = findTool(env)
        self.state,self.goto = toolPick(env,tool_list)
        if len(env.enemy):
            for enemy in env.enemy:
                if enemy.isAlive == True:
                    for us in env.us:
                        if 0<distance((enemy.x,enemy.y),(us.x,us.y))<=8:
                            self.state[us.characterID] = 2
                            self.goto[us.characterID] = [(us.x,us.y),(enemy.x,enemy.y)]       
        if env.frame > self.frame:
            self.frame = env.frame
            self.condition.acquire()
            self.condition.notify()
            self.condition.release()


    def output(self,characterID):
        a = time.time()
        if characterID==0:
            output = ['','']
            for flag, state in enumerate(self.state):
                if state == 0:
                    output[flag] = cruise(self.env,flag)#巡航
                if state == 1:
                    output[flag] = getool(self.env,self.goto,flag)#得道具


                if state == 2:
                    output[flag] = keep_distance(self.env,self.goto,flag,4)
                        #output[flag] += run_away(self.env,self.goto,flag,8)

                if 's' not in output[flag] and 'j' not in output[flag] and 'k' not in output[flag]:#没有行动时进行张望
                    output[flag] = s[(s2i[output[flag]] - self.env.us[flag].moveCDLeft)%6]
                if self.env.us[flag].isAlive == False:#死亡不输入
                    output[flag] = ''
                if self.env.frame >= 200:
                    if 'j' in output[flag]:
                        output[flag] = 'i' + output[flag]
                    else:
                        output[flag] = 'u' + output[flag]
                   

            self.result = output
            if self.actionResp:
                save(self.actionResp, self.result)
                with open('log_output.txt','a') as f:
                    print('frame:{}'.format(self.actionResp.frame),'action{}'.format(self.result),'state:{}'.format(self.state),file=f)

            return self.result[characterID]
        else:
            return self.result[characterID]


if __name__ == '__main__':
    '''加载特定一次训练的信息'''
    packet =  PacketResp()
    model = Model()
    ui = UI()
    characterID = 0
    '1670917645822'
    for saveInfo in getresp():
        actionResp = saveInfo.actionResp
        packet.data = actionResp
        model.env = model.env.readEnv(actionResp)
        refreshUI(ui,packet)
        model.input(model.env)
        st = model.output(characterID)
        print('frame = {}'.format(actionResp.frame),'action:{}'.format(st))