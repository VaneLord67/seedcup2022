from pg_model import PGModel
from pg_env import Enviroment
from pg_agent import PGAgent
from mytrain import run_train_episode,calc_reward_to_go
from resp import *
from base import *
import parl
import os
import time

class Model():
    def __init__(self):
        self.resp = None
        #self.playerID = None
        LEARNING_RATE = 0.001
        modelPath = './pgmodel1.ckpt'
        with open('log_action.txt', 'w')as file:
            file.close()
        with open('log_reward.txt', 'w')as file:
            file.close()#清空缓存
        act_dim = 6
        self.action = 0
        self.env = Enviroment()
        self.pgmodel = PGModel(obs_dim=16*16, act_dim=act_dim)
        self.alg = parl.algorithms.PolicyGradient(self.pgmodel, lr=LEARNING_RATE)
        self.agent = PGAgent(self.alg, act_dim)
        if os.path.exists(modelPath):
            self.agent.restore(modelPath)
        self.env.agent = self.agent
        self.env.obs_list, self.env.action_list, self.env.reward_list =[],[],[]
    def input(self, resp: PacketResp):
        if resp.type == PacketType.GameOver:
            return
        actionResp: ActionResp = resp.data
        self.resp = actionResp

    def output(self):
        time.sleep(0.16)
        obs, self.action, reward = run_train_episode(self.env,self.action,self.resp)
        a = 'wedxza'[self.action]+'sj'
        with open('log_action.txt', 'a+')as file:
            print(a, file=file)
        with open('log_reward.txt', 'a+')as file:
            print(reward, file=file)
        return a
    def learn(self):
        batch_reward = calc_reward_to_go(self.env.reward_list)
        self.env.agent.learn(self.env.obs_list, self.env.action_list,batch_reward)
        #     model.resp = actionResp
        #     model.character = actionResp.characters
        #     model.map = actionResp.map
        #     action = model.output()
        #     print(action)
        self.env.agent.save(self.modelPath)
        print("model saved in {}".format(self.modelPath))
        return 'ok'