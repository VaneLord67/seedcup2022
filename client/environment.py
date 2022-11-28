import numpy as np
from pg_agent import *
from resp import *
import subprocess

class Environment():
    def __init__(self) -> None:
        self.reward_list = []
        self.action_list = []
        self.obs_list = []
        self.cnt: int = 0
        self.action: int
        self.agent: PGAgent
        self.waiting: bool = False
        self.obs = None
        self.ui_turn = True
        self.reward: int = 0
        self.agentSaveCnt: int = 0
        self.modelPath: str
        self.score: int = 0
        self.actionResp: ActionResp = None
        self.scoreReward: int = 0
        self.moveCDReward: int = 0
        self.hpReward: int = 0
        self.killReward: int = 0
        self.distanceReward: int = 0
        self.moveReward: int = 0
        self.enemyScore: int = 0
        self.enemyReward: int = 0
        self.distance: int = 0
        self.illegalMoveReward: int = 0
    
    def killServerAndBot(self):
        subprocess.getoutput('''ps -ef |grep seedcupServer|grep -v grep|awk '{print $2}'|xargs kill -9''')

    def reset(self):
        self.killServerAndBot()

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
