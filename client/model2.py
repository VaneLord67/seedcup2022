from pg_model import PGModel
from pg_env import Enviroment
from pg_agent import PGAgent
from mytrain import run_train_episode,calc_reward_to_go,run_evaluate_episodes, killServerAndBot
from resp import *
from base import *
import parl
import os
import threading

class Model():
    def __init__(self):
        self.condition: threading.Condition = threading.Condition() # 接收和发送线程间同步使用
        self.resp = None
        self.frame: int = -1
        self.epoch = None
        #self.playerID = None
        LEARNING_RATE = 0.001
        self.EarlyStopThreshold: int = -100
        self.modelPath = './pgmodel1.ckpt'
        with open('log_action.txt', 'w')as file:
            pass # 不需要手动close. with open会自动管理
        with open('log_reward.txt', 'w')as file:
            pass
        act_dim = 6
        self.action = 0
        
        self.env = Enviroment()
        self.pgmodel = PGModel(obs_dim=16*16, act_dim=act_dim)
        self.alg = parl.algorithms.PolicyGradient(self.pgmodel, lr=LEARNING_RATE)
        self.agent = PGAgent(self.alg, act_dim)
        if os.path.exists(self.modelPath):
            self.agent.restore(self.modelPath)
        self.env.agent = self.agent
        self.env.obs_list, self.env.action_list, self.env.reward_list =[],[],[]

        # warm up agent，加快游戏开始后的计算速度
        obs = [0]*16*16
        self.env.agent.predict(obs)
    def input(self, resp: PacketResp):
        if resp.type == PacketType.GameOver:
            return
        actionResp: ActionResp = resp.data
        self.resp = actionResp
        if self.resp.frame > self.frame:
            # self.actionFrame = self.frame
            # print(f'frame = {self.frame}')
            self.condition.acquire()
            self.condition.notify()
            self.condition.release()
        self.frame = self.resp.frame

    def output(self):
        # time.sleep(0.1)
        if self.epoch%5 == 0:#evaluate
            obs, self.action, reward = run_evaluate_episodes(self.env,self.action,self.resp)
        else:
            obs, self.action, reward = run_train_episode(self.env,self.action,self.resp)
        a = 'wedxza'[self.action]+'sj'
        with open('log_action.txt', 'a+')as file:
            print(a, file=file)
        with open('log_reward.txt', 'a+')as file:
            print(reward, file=file)
        if reward <= self.EarlyStopThreshold:
            # earlyStop
            killServerAndBot()
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
        with open("log_saved.txt",'a+') as f:
            print("frame {} model saved in {}".format(self.frame,self.modelPath),file = f)
        return 'ok'