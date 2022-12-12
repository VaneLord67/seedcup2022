from resp import *
gContext = {
    "playerID": None,
    "characterID": [],
    "gameOverFlag": False,
    "prompt": (
        "Take actions!\n"
        "'s': move in current direction\n"
        "'w': turn up\n"
        "'e': turn up right\n"
        "'d': turn down right\n"
        "'x': turn down\n"
        "'z': turn down left\n"
        "'a': turn up left\n"
        "'u': sneak\n"
        "'i': unsneak\n"
        "'j': master weapon attack\n"
        "'k': slave weapon attack\n"
        "Please complete all actions within one frame! \n"
        "[example]: a12sdq2\n"
    ),
    "steps": ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"],
    "gameBeginFlag": False,
}
class Env():
    def __init__(self):
        self.map: Map = Map()
        self.us: list[Character] = []
        self.enemy: list[Character] = []

        self.dir = [0,0]

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
    