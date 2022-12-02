import numpy as np
from pg_agent import *
from resp import *


point = {
    "wall":-10,
    "othersland":-1,
    "myland":1,
    "whiteland":0,
    "faster":50,
    "blood":30,
    "enemy": -100,
    "me":100
}
class Enviroment():
    def __init__(self):
        self.reward_list = []
        self.action_list = []
        self.obs_list = []
        self.frame_list = []

        self.agent: PGAgent

        self.act: str = None
        self.actionResp: ActionResp = None



        self.cnt: int = 0
        self.action: int
        self.waiting: bool = False
        self.obs = None
        self.ui_turn = True
        self.reward: int = 0
        self.agentSaveCnt: int = 0
        self.modelPath: str
        self.score: int = 0
        
        self.scoreReward: int = 0
        self.moveCDReward: int = 0
        self.hpReward: int = 0
        self.killReward: int = 0
        self.distanceReward: int = 0
        self.moveReward: int = 0
        self.enemyScore: int = 0
        self.enemyReward: int = 0
        self.distance: int = 0

    def step(self):
        self.obs_list.append(self.obs)
        self.reward_list.append(self.reward)
        self.action_list.append(self.action)
        self.cnt += 1
        self.agentSaveCnt += 1
        if self.agentSaveCnt % 100 == 0:
            self.agent.save(self.modelPath)
            self.agentSaveCnt = 0
        done: bool = (self.cnt % 75) == 0
        if done:
            self.cnt = 0
        return done

    def get_obs(self,actionResp):
        obs = actionResp
        obs = np.zeros((16,16))
        blocks = actionResp.map.blocks
        pos = (actionResp.characters[0].x,actionResp.characters[0].y)
        for block in blocks:
            x,y = (block.x,-block.y)
            if len(block.objs)>0:
                #有obj
                if (block.objs[0].type-1):
                    #block上是道具
                    if (int(str(block.objs[0].status)[-2])-1):
                        #是blood
                        obs[x][y]+= point["blood"]
                    else:
                        obs[x][y]+= point["faster"]
                elif(block.objs[0].status.x,block.objs[0].status.y)!=pos:
                    #block上是敌人
                    obs[x][y]+= point["enemy"]
                    #block上什么都没有
                else:
                    obs[x][y]+= point["me"]
            else:
                #block上啥也没有
                if block.valid == False:
                    obs[x][y] += point['wall']
                elif block.color == 0:
                    obs[x][y] += point['whiteland']
                elif block.color != actionResp.characters[0].color:
                    obs[x][y] += point['othersland']
                else:
                    obs[x][y] += point['myland']
        return obs


    def get_reward(self,act,actionResp):
        #self.actionResp.score记录上次的resp
        direction2DeltaPosition = [(-1,1),(-1,0),(0,-1),(1,-1),(1,0),(0,1)]

        if self.actionResp:
            scoreReward = actionResp.score - self.actionResp.score
            hpReward = actionResp.characters[0].hp - self.actionResp.characters[0].hp
            moveCDReward = actionResp.characters[0].moveCD - self.actionResp.characters[0].moveCD
            killReward = actionResp.kill - self.actionResp.kill
            illegalMoveReward = 0
            if act<6:
                di = direction2DeltaPosition[act]
                targetBlockPositionX = actionResp.characters[0].x + di[0]
                targetBlockPositionY = actionResp.characters[0].y + di[1]
                if (targetBlockPositionX < 0) or (targetBlockPositionY > 0) or (targetBlockPositionY < -15) or (targetBlockPositionX > 15) == True:
                    illegalMoveReward = -50
                if (targetBlockPositionX*16-targetBlockPositionY)<16*16:
                    if actionResp.map.blocks[targetBlockPositionX*16-targetBlockPositionY].valid == False:
                        illegalMoveReward = -100

            reward = scoreReward * 4 + hpReward * 5 + moveCDReward * 250 + killReward * 1000 + illegalMoveReward
            return reward
        else: 
            return 0
