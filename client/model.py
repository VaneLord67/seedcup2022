from resp import *
from base import *
from saveload import *
from env import *
import time 
import threading

whitelandColor: int = 0
point = {
    "wall":-1,
    "othersland":2,
    "whiteland":1,
    "faster":5,
    "blood":3,
    "enemy": 10
}
directiondic ='wedxza'
def argmax(l=[1,2,3,3]):
    '''返回各个最大值的索引'''
    m = max(l)
    ml = []
    for index,i in enumerate(l):
        if i == m:
            ml.append(index)
    return ml

def get_around_pos(pos):
    dir = [(-1,1),(-1,0),(0,-1),(1,-1),(1,0),(0,1)]
    #dir = [(1,-1),(0,-1),(-1,0),(-1,1),(0,1),(1,0)]
    return [(i+pos[0],j+pos[1]) for i,j in dir]
def get_block(blocks,pos):
    return blocks[pos[0]][-pos[1]]
    # id = pos[0]*24+abs(pos[1])
    # if pos[0] in range(21) and -pos[1] in range(21):
    #     return blocks[pos[0]][pos[1]]
    # else:
    #     return None

def get_weapon2_pos(pos):
    dir = [(-1,1),(0,1),(1,0),(1,-1),(0,-1),(-1,0)]
    six_center = [(2*i+pos[0],2*j+pos[1]) for i,j in dir]
    return [get_around_pos(i)+[i] for i in six_center]

def add_score(all_pos,blocks,c):
    score = []
    for i in all_pos:
        t1 = []
        for j in i:
            t2 = 0
            for k in j :
                b = get_block(blocks,k)
                if b == None:
                    t2 += point['wall']
                elif b.color == 0:
                    t2 += point['whiteland']
                elif b.color != c.color:
                    t2 += point['othersland']
            t1.append(t2)
        score.append(t1)
    return score
def get_dir_score(map,c,weapon=2):
    '''计算6个方向的分数  计算方法为向哪个方向走一步,六个方向的武器攻击加分的最大值
    Arg
        map 地图信息
        dir 我的位置
        weapon 武器类型 1为西瓜  2为榴莲
        [] 六个方向的分数以wedxza顺序排列
    '''
    blocks = map.blocks
    pos = (c.x,c.y)
    around = get_around_pos(pos)
    all_pos = []
    for p in around:
        if weapon == 2:
            all_pos.append(get_weapon2_pos(p))
    score = add_score(all_pos,blocks,c)
    dir_score = [sum(d) for d in score]
    return dir_score

def direction(dir_score,tool_score):
    score = [0,0,0,0,0,0]
    for i in range(6):
        score[i] = dir_score[i]+ tool_score[i]
        s = argmax(score)
    return directiondic[s[0]]

def distance(pos1,pos2):
    #计算距离
    dx = pos1[0]-pos2[0]
    dy = pos1[1]-pos2[1]
    return max(abs(dx),abs(dy))

def add_score_to_dir(score,tool,pos,a):
    for i in tool:
        dx = i[0]-pos[0]
        dy = i[1]-pos[1]
        dir = []
        if dx<0 and dy>0:
            #dir = [(-1,1),(-1,0),(0,-1),(1,-1),(1,0),(0,1)]
            dir.append(0)
        if dx<0 and dy<0:
            dir.append(1)
            dir.append(2)
        if dx>0 and dy<0:
            dir.append(3)
        if dx>0 and dy>0:
            dir.append(4)
            dir.append(5)
        if dx < 0 and dy==0:
            dir.append(1)
        if dx == 0 and dy<0:
            dir.append(2)
        if dx > 0 and dy==0:
            dir.append(4)
        if dx > 0 and dy==0:
            dir.append(5)
        for d in dir:
            score[d] += (13 - i[2])*a#距离越远分数越低
    return score
def get_tool_score(map,c):
    '''计算道具与人距离的分数，距离越近分数越大，人能往道具方向前进'''
    blocks = map.blocks
    pos = (c.x,c.y)
    hp = c.hp
    movecd = c.moveCD
    tool_score = [0,0,0,0,0,0]
    blood = []
    faster = []
    enemy = None
    for blockList in blocks:
        for block in blockList:
            if len(block.objs)>0:
                d = distance(pos,(block.x,block.y))
                if (block.objs[0].type-1):
                    #block上是道具
                    if (int(str(block.objs[0].status)[-2])-1):
                        #是bufftype2
                        blood.append((block.x,block.y,d))
                    else:
                        faster.append((block.x,block.y,d))
                else:
                    #block上是人
                    if (block.objs[0].status.x,block.objs[0].status.y)!=pos:
                        enemy = block.objs[0]
    alpha = movecd #cd越大越需要faster
    beta = 10-hp//10 #hp越低越需要blood
    tool_score = add_score_to_dir(tool_score,faster,pos,alpha)

    tool_score = add_score_to_dir(tool_score,blood,pos,beta)
    
    return tool_score

class Model(object):
    def __init__(self,id,weapon):
        self.id = id
        self.weapon = weapon
        self.t = time.time()

        self.color: int = 0
        self.playerID: int = 0
        self.dirs: list(tuple(int, int)) = [(-1,1),(0,1),(1,0),(1,-1),(0,-1),(-1,0)]
        self.frame: int = -1
        self.condition = threading.Condition()
    def output(self):
        frame = self.env.frame
        if not self.isAlive():
            return ""
        dir_score = get_dir_score(map = self.env.map ,c = self.env.us[0],weapon=2)
        tool_score = get_tool_score(map = self.env.map ,c = self.env.us[0])
        st = direction(dir_score,tool_score)
        if not self.isInMasterWeaponCD():
            if not self.isInMoveCD(): 
                st += 'sj'
        if not self.isInSlaveWeaponCD():
            st += self.getKiwifruitAttackDirStr()
            st += 'k'
        #record
        fileName='log_opearator.txt'
        with open(fileName, 'a+') as file:
            print('frame:{}'.format(frame), file=file)
            print('operations is {}'.format(st), dir_score, file=file)
            t = time.time()
            print('model cost {%.3f} s'%(t-self.t),file=file)
            self.t = t
        save(self.env, st)
        return st

    def input(self, env: Env):
        self.env = env
        self.color: int = env.us[0].color
        self.playerID: int = gContext['playerID']
        if env.frame > self.frame:
            self.condition.acquire()
            self.condition.notify()
            self.condition.release()
            self.frame = env.frame

    def isInMasterWeaponCD(self):
        for character in self.env.us:
            if character.masterWeapon.attackCDLeft == 0:
                return False
        return True

    def isInSlaveWeaponCD(self):
        for character in self.env.us:
            if character.slaveWeapon.attackCDLeft == 0:
                return False
        return True
    
    def isInMoveCD(self):
        for character in self.env.us:
            if character.moveCDLeft == 0:
                return False
        return True

    def isAlive(self):
        for character in self.env.us:
            return character.isAlive
        return False

    def getKiwifruitAttackDirStr(self):
        scores = self.getKiwifruitScore((self.env.us[0].x, self.env.us[0].y))
        maxIndex = scores.index(max(scores))
        return directiondic[maxIndex]

    def getKiwifruitScore(self, pos: tuple):
        '''猕猴桃分数计算'''
        # 猕猴桃每回合移动1次，最⼤距离为8
        playerX = pos[0]
        playerY = pos[1]
        scores = []
        for dirX, dirY in self.dirs:
            dirScore: int = 0
            for i in range(1, 8):
                blockScore: int = self.getBlockScore((playerX + dirX*i, playerY + dirY*i))
                dirScore += blockScore
            scores.append(dirScore)
        return scores
            
    def getBlockScore(self, blockPos: tuple):
        block: Block = get_block(self.env.map.blocks, blockPos)
        score: int = 0
        if block == None or block.valid == False:
            score += point['wall']
        elif block.color == whitelandColor:
            score += point['whiteland']
        elif block.color != self.color:
            score += point['othersland']
        if self.isEnemyStandInBlock(block):
            score += point['enemy']
        return score
    
    def isEnemyStandInBlock(self, block: Block):
        if block == None:
            return False
        if len(block.objs) == 0:
            return False
        for obj in block.objs:
            if obj.type != ObjType.Character:
                return False
            if obj.status.playerID != self.playerID:
                return True
        return False

if __name__ == "__main__":
    def getresp(fileName='log_player.txt'):
        with open(fileName) as file:
            allres =  file.read()
            matches = allres.split("resp = ")[1:]
            for match in matches:
                yield match.strip()
    model = Model(1,2)
    frame = -1 #从FRAME 帧后开始接受包
    for f,s in enumerate(getresp()):
        if f<=frame:
            continue
        packetResp = PacketResp()
        actionResp = packetResp.from_json(s).data
        model.resp = actionResp
        model.characters = actionResp.characters
        model.map = actionResp.map
        action = model.output()
        print(action)