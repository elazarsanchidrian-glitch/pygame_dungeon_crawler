from game.npc import NPC


class LostTraveler(NPC):
    """NPC who gives the player a directional hint toward the dungeon exit."""

    def __init__(self):
        super().__init__(
            "Lost Traveler",
            "A disheveled wanderer looking exhausted from roaming the dark corridors.",
        )

    def talk(self, game_instance):
        """Give a directional hint based on the current dungeon position."""
        print(f"\n{self.name}: 'Oh, thank the heavens, another living soul!'")
        print(
            f"{self.name}: 'Are you looking for a way out of this nightmare? "
            "I've mapped out parts of these halls.'"
        )

        current_x, current_y = game_instance.dungeon.get_position()
        exit_x = game_instance.dungeon.exit_x
        exit_y = game_instance.dungeon.exit_y

        directions = []

        if exit_y > current_y:
            directions.append("south")
        elif exit_y < current_y:
            directions.append("north")

        if exit_x > current_x:
            directions.append("east")
        elif exit_x < current_x:
            directions.append("west")

        direction_hint = " and ".join(directions) if directions else "right here nearby"

        print(
            f"{self.name}: 'If my bearings are correct, the exit lies roughly "
            f"to the {direction_hint} from here.'"
        )
        print(
            f"{self.name}: 'Beware, though—you'll need a special key to open "
            "that door, rumored to be guarded by a powerful warden!'"
        )
