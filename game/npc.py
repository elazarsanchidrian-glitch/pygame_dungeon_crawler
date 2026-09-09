class NPC:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def talk(self):
        print(f"{self.name}: Hello, traveler.")

    def idle(self):
        print(f"{self.name} looks around nervously.")






