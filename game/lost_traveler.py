from game.npc import NPC


class LostTraveler:
    def __init__(self):
        self.name = "Lost Traveler"
        self.description = "A disheveled wanderer looking exhausted from roaming the dark corridors."

    def talk(self, game_instance):
        """Talk to the traveler to receive a directional hint toward the exit."""
        print(f"\n{self.name}: 'Oh, thank the heavens, another living soul!'")
        print(f"{self.name}: 'Are you looking for a way out of this nightmare? I've mapped out parts of these halls.'")

        # Get current coordinates from dungeon and compare with exit coordinates
        current_x, current_y = game_instance.dungeon.get_position()
        exit_x = game_instance.dungeon.exit_x
        exit_y = game_instance.dungeon.exit_y

        # Give a useful directional hint
        hint_x = "east" if exit_x > current_x else ("west" if exit_x < current_x else "")
        hint_y = "south" if exit_y > current_y else ("north" if exit_y < current_y else "")

        direction_hint = f"{hint_y} and {hint_x}".strip(" and ")
        if not direction_hint:
            direction_hint = "right here nearby"

        print(
            f"{self.name}: 'If my bearings are correct, the exit lies roughly to the **{direction_hint}** from here.'")
        print(
            f"{self.name}: 'Beware, though—you'll need a special key to open that door, rumored to be guarded by a powerful warden!'")