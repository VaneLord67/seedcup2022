from resp import *
from main import gContext

class Env():
    def __init__(self):
        self.map: Map = Map()
        self.us: list[Character] = []
        self.enemy: list[Character] = []

    def readEnv(self, actionResp: ActionResp):
        self.map = actionResp.map
        self.us = actionResp.characters
        self.enemy = []
        for block in actionResp.map.blocks:
            if len(block.objs) > 0:
                for obj in block.objs:
                    if obj.type == ObjType.Character:
                        character: Character = obj.status
                        if character.playerID != gContext['playerID']:
                            self.enemy.append(character)
        return self
    