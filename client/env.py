from resp import *

# record the context of global data
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

class Env(JsonBase):
    def __init__(self):
        super().__init__()
        self.map: Map = Map()
        self.map.blocks = [
            [Block(x=x, y=-y) for y in range(24)]
            for x in range(24)
        ]
        self.us: list[Character] = []
        self.enemy: list[Character] = []
        self.frame: int = -1

        self.dir = [0,0]

    def readEnv(self, actionResp: ActionResp):
        self.frame = actionResp.frame
        for block in actionResp.map.blocks:
            self.map.blocks[block.x][-block.y] = block
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
    
    def from_json(self, j: str):
        d = json.loads(j)
        for key, value in d.items():
            if key in self.__dict__:
                if hasattr(self.__dict__[key], "from_json"):
                    setattr(self, key, self.__dict__[key].from_json(json.dumps(value)))
                else:
                    setattr(self, key, value)
        value = d.pop("us")
        self.us = [Character().from_json(json.dumps(v)) for v in value]
        value = d.pop("enemy")
        self.enemy = [Character().from_json(json.dumps(v)) for v in value]
        return self