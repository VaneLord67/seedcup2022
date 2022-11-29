import socket
import subprocess
import json
from threading import Thread
import time
from main import *


def isPortAvailable(port: int) -> bool:
    '''判断端口是否可用'''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    # result == 0代表端口没有被占用 result !=0 代表端口被占用
    return result == 0

def runSeedcupServer():
    subprocess.getoutput("./seedcupServer")

def runBot():
    subprocess.getoutput("./bot")

def runServerAndBot():
    port: int = getConfigPort() - 1
    ok = isPortAvailable(port)
    if not ok:
        port = port - 1
        if port < 9000:
            port = 9999
        print("change port to", port)
        changeConfigPort(port)
    seedcupServerThread = Thread(target=runSeedcupServer)
    seedcupServerThread.daemon = True
    seedcupServerThread.start()
    ok = isPortAvailable(port)
    if not ok:
        print("successfully run seedcupServer, port:", port)
    else:
        print("failed run seedcupServer")
        return None, False, port
    time.sleep(1)
    botThread = Thread(target=runBot)
    botThread.daemon = True
    botThread.start()
    return seedcupServerThread, True, port

def getConfigPort() -> int:
    with open('./config.json', 'r') as f:
        params = json.load(f)
        return params['Port']

def changeConfigPort(port: int):
    '''修改配置文件中的端口号'''
    with open('./config.json', 'r') as f:
        params = json.load(f)
        params["Port"] = port
    with open('./config.json', 'w') as f:
        json.dump(params, indent = 4, fp=f)

def killServerAndBot():
    subprocess.getoutput('''ps -ef |grep seedcupServer|grep -v grep|awk '{print $2}'|xargs kill -9''')

def model_train():
    epoch = 1
    for i in range(0, epoch):
        initGlobalContext()
        seedcupServerThread, ok, port = runServerAndBot()
        if not ok:
            print("run server failed")
            continue
        time.sleep(1)
        main(port,i)
        print("result = ", result)
        print("resultScore = ", resultScore)
        killServerAndBot()

if __name__ == '__main__':
    # epoch = 10
    # for i in range(0, epoch):
    #     initGlobalContext()
    #     seedcupServerThread, ok, port = runServerAndBot()
    #     if not ok:
    #         print("run server failed")
    #         continue
    #     time.sleep(1)
    #     main(port)
    # print("result = ", result)
    # print("resultScore = ", resultScore)
    model_train()