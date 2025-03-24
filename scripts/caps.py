
# Co z bias i z refką?

default_map_mini: dict = {
    0: "F3",
    1: "F4",
    2: "C3",
    3: "C4",
    4: "P3",
    5: "P4",
    6: "O1",
    7: "O2"
}

class Cap:
    def __init__(self, cap_map: dict, device_name: str):
        self.mapping = cap_map
        self.name = device_name
    
mini_default_cap = Cap(default_map_mini, "BA MINI 0002") 


