from resp import *
from base import *
from pg_model import PGModel
from pg_agent import PGAgent
from pg_env import Enviroment
import parl
import os
LEARNING_RATE = 0.001
act_dim = 6
modelPath = './pgmodel8.ckpt'
env = Enviroment()
model = PGModel(obs_dim=16*16, act_dim=act_dim)
alg = parl.algorithms.PolicyGradient(model, lr=LEARNING_RATE)
agent = PGAgent(alg, act_dim)

# train an episode
def run_train_episode(agent, env):
    obs_list, action_list, reward_list = [], [], []
    obs = env.reset()
    while True:
        obs_list.append(obs)
        action = agent.sample(obs)
        action_list.append(action)

        obs, reward, done, info = env.step(action)
        reward_list.append(reward)

        if done:
            break
    return obs_list, action_list, reward_list

def train(act, actionResp):
    if os.path.exists(modelPath):
        agent.restore(modelPath)
    env.agent = agent

    return 'ok'
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
if __name__ == "__main__":
    frame = -1 #从FRAME 帧后开始接受包
    acts = get_act()

    for f,s in enumerate(getresp()):
        if f<=frame:
            continue
        packetResp = PacketResp()
        actionResp = packetResp.from_json(s).data
        train(acts[f],actionResp)
    #     model.resp = actionResp
    #     model.character = actionResp.characters
    #     model.map = actionResp.map
    #     action = model.output()
    #     print(action)
    # agent.save(modelPath)