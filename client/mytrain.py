from resp import *
from base import *
from pg_agent import PGAgent
from pg_env import Enviroment
import parl
import os
import numpy as np
from pg_model import PGModel
import time



def calc_reward_to_go(reward_list, gamma=0.8):
    for i in range(len(reward_list) - 2, -1, -1):
        # G_i = r_i + γ·G_i+1
        reward_list[i] += gamma * reward_list[i + 1]# Gt
        if reward_list[0]>0:
            reward_list = [i*5 for i in reward_list]#胜利奖励分
            
    return np.array(reward_list)

    
def getresp(fileName='log_player.txt'):
    with open(fileName) as file:
        allres =  file.read()
        matches = allres.split("resp = ")[1:]
        for match in matches:
            yield match.strip()
def get_act(fileName='log_opearator.txt'):
    with open(fileName) as file:
        allact =  file.read()
        acts = allact.split("\n")
        return acts
def run_train_episode(env, act, actionResp):
    obs = env.get_obs(actionResp)#通过返回的resp来观测
    action = env.agent.sample(obs)
    reward = env.get_reward(act, actionResp)
    #obs, reward, done, info = env.step(action)
    
    env.act = act#上一次行动
    env.actionResp = actionResp#记录上一次的地图信息
    env.obs_list.append(obs)
    env.action_list.append(action)
    env.reward_list.append(reward)
    return obs, action, reward

# evaluate 5 episodes
def run_evaluate_episodes(env, act, actionResp):
    obs = env.get_obs(actionResp)#通过返回的resp来观测
    action = env.agent.predict(obs)
    
    reward = env.get_reward(act, actionResp)
    #obs, reward, done, info = env.step(action)
    env.act = act#上一次行动
    env.actionResp = actionResp#记录上一次的地图信息
    env.obs_list.append(obs)
    env.action_list.append(action)
    env.reward_list.append(reward)
    return obs, action, reward
def d_train():
    LEARNING_RATE = 0.001
    act_dim = 6
    modelPath = './pgmodel1.ckpt'
    env = Enviroment()
    model = PGModel(obs_dim=16*16, act_dim=act_dim)
    alg = parl.algorithms.PolicyGradient(model, lr=LEARNING_RATE)
    agent = PGAgent(alg, act_dim)
    action = 0
    frame = -1 #从FRAME 帧后开始接受包
    if os.path.exists(modelPath):
        agent.restore(modelPath)
    env.agent = agent
    env.obs_list, env.action_list, env.reward_list =[],[],[]
    #acts = get_act()

    for f,s in enumerate(getresp()):
        if f<=frame:
            continue
        packetResp = PacketResp()
        actionResp = packetResp.from_json(s).data
        obs, action, reward = run_train_episode(env,action,actionResp)

    batch_reward = calc_reward_to_go(env.reward_list)
    agent.learn(env.obs_list, env.action_list, batch_reward)
    #     model.resp = actionResp
    #     model.character = actionResp.characters
    #     model.map = actionResp.map
    #     action = model.output()
    #     print(action)
    agent.save(modelPath)
    return 'ok'

if __name__ == "__main__":
    d_train()

