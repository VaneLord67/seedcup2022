from resp import *
import time 
import re 
import json
point = {
    "wall":-1,
    "othersland":2,
    "whiteland":1
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
    id = pos[0]*16+abs(pos[1])
    if pos[0] in range(13) and -pos[1] in range(13):
        return blocks[id]
    else:
        return None

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
    return score
def direction(dir_score):
    l = [max(d) for d in dir_score]
    s = argmax(l)
    if len(s) >= 2:
        s = argmax([sum(d) for d in dir_score])[:1]
    return directiondic[s[0]]

class Model(object):
    def __init__(self,id,weapon):
        self.id = id
        self.weapon = weapon
        self.resp = None
        self.character = None
        self.map = None
    def output(self):
        dir_score = get_dir_score(map = self.map ,c = self.character[0],weapon=2)
        st = direction(dir_score)+'sj'
        time.sleep(0.1)
        fileName='log_opearator.txt'
        with open(fileName, 'a+')as file:
            print(st, dir_score, file=file)
        return st

    def input(self, resp: PacketResp):
        fileName='log_player.txt'
        self.resp = resp
        #self.character = resp['data']['characters']
        #self.map = resp['data']['map']
        if resp.type == PacketType.GameOver:
            return
        self.character = resp.data.characters
        self.map = resp.data.map
        #save to file 
        with open(fileName, 'a+')as file:
            print("resp = ", resp, file=file)


if __name__ == "__main__":
    def getresp(fileName='log_player.txt',frame=None):
        with open(fileName) as file:
            allres =  file.read()
            matches = allres.split("resp = ")[1:]
            for match in matches:
                yield match.strip()
    model = Model(1,2)
    for s in getresp():
        packetResp = PacketResp()
        actionResp = packetResp.from_json(s).data
        model.resp = actionResp
        model.character = actionResp.characters
        model.map = actionResp.map
        action = model.output()
        print(action)