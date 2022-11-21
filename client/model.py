from resp import *
import time

class Model(object):
    def __init__(self):
        pass

    def output(self):
        time.sleep(0.1)
        return 'dsj'

    def input(self, resp: PacketResp):
        fileName='log_player.txt'
        with open(fileName, 'a+')as file:
            print("resp = ", resp, file=file)

        
