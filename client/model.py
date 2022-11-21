from resp import *

class Model(object):
    def __init__(self):
        pass

    def output():
        return "dsj"

    def input(self, resp: PacketResp):
        fileName='log_player.txt'
        with open(fileName, 'a+')as file:
            print("resp = ", resp, file=file)

        
