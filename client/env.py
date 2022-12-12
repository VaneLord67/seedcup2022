from resp import Map,Character
from typing import List
class Env(object):
    def __init__(self) -> None:
        self.map: Map = Map(),
        self.us: List[Character] = [],
        self.ememy: List[Character] = []
    