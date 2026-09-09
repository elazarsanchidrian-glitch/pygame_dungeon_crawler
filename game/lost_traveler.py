from game.npc import NPC


class LostTraveler(NPC):
    def __init__(self):
        super().__init__(
            "Lost Traveler",
            "A weary traveler covered in dust and scratches."
        )

    def talk(self):
        print("Lost Traveler: Thank the gods... another person.")
        print("Lost Traveler: I've been wandering these tunnels for hours.")