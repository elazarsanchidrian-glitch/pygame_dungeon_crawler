import random

from game.player import Player
from game.dungeon import Dungeon
from game.ui import ConsoleUI
from game.character import CharacterCreation
from game.save_system import SaveSystem


class Game:

    def __init__(self):

        self.ui = ConsoleUI()
        self.dungeon = Dungeon()
        self.game_won = False

        self.ui.show_welcome()

        # -------------------------
        # CHARACTER CREATION
        # -------------------------

        player_name = self.ui.get_player_name()

        character = CharacterCreation(player_name)

        character.choose_gender()
        character.choose_race()
        character.choose_class()

        character.show_character()

        # -------------------------
        # CREATE PLAYER
        # -------------------------

        self.player = Player(player_name)

        self.player.gender = character.gender
        self.player.race = character.race
        self.player.character_class = character.character_class
        self.player.passive = character.passive

        self.player.health = character.health
        self.player.max_health = character.health

        self.player.stamina = character.stamina
        self.player.magicka = character.magicka

        # -------------------------
        # CLASS STARTING INVENTORY
        # -------------------------

        self.player.setup_starting_inventory()
        self.player.auto_equip_starting_gear()

        self.player.health = character.health

        # -------------------------
        # STARTING ROOM
        # -------------------------

        self.player.current_room = self.dungeon.current_room

    # -------------------------
    # MONSTER ATTACK
    # -------------------------

    def monster_attack(self, monster):

        damage = monster.attack()

        self.player.take_damage(damage)

        self.ui.show_message(
            f"{monster.name} hits you for {damage} damage!"
        )

        self.ui.show_message(
            f"Your health: "
            f"{self.player.health}/{self.player.max_health}"
        )

        if self.player.health <= 0:

            self.ui.show_player_defeated()

            return False

        return True

    # -------------------------
    # DODGE
    # -------------------------

    def dodge(self, monster):

        # 50% chance to successfully dodge
        if random.random() < 0.50:

            self.ui.show_message(
                f"You dodge {monster.name}'s attack!"
            )

            return True

        self.ui.show_message(
            f"You try to dodge, but {monster.name} catches you!"
        )

        return self.monster_attack(monster)

    # -------------------------
    # ESCAPE
    # -------------------------

    def escape(self, monster):

        # 50% chance to escape
        if random.random() < 0.50:

            self.ui.show_message(
                f"You successfully escape from {monster.name}!"
            )

            # The monster loses track of you
            self.player.current_room.remove_monster(monster)

            return True

        self.ui.show_message(
            f"You try to escape, but {monster.name} catches you!"
        )

        return self.monster_attack(monster)


    # -------------------------
    # DIALOGUE / SPEECH CHECK
    # -------------------------

    def dialogue(self, monster):

        chance = monster.dialogue_success_chance

        self.ui.show_message(
            f"\nYou attempt to talk to {monster.name}..."
        )

        # Monster says something
        monster.speak()

        self.ui.show_message(
            f"Speech check: {chance}% chance of success."
        )

        roll = random.randint(1, 100)

        if roll <= chance:

            self.ui.show_message(
                f"You successfully convince {monster.name} "
                f"to leave you alone!"
            )

            self.ui.show_message(
                f"{monster.name}: Fine... leave me be."
            )

            # Remove the monster from the room
            self.player.current_room.remove_monster(monster)

            return True

        # -------------------------
        # FAILED SPEECH CHECK
        # -------------------------

        self.ui.show_message(
            f"Your attempt to reason with {monster.name} fails!"
        )

        self.ui.show_message(
            f"{monster.name}: Enough talk!"
        )

        self.ui.show_message(
            f"{monster.name} attacks you!"
        )

        # Failed dialogue costs a turn
        return self.monster_attack(monster)

    # -------------------------
    # VICTORY / EXIT
    # -------------------------

    def check_for_exit(self):
        """Return True when the player reaches the normal dungeon exit."""
        room = self.player.current_room

        if room.is_exit:
            self.ui.show_message(
                "\nYou have discovered the dungeon exit!"
            )
            self.ui.show_victory()
            return True

        return False

    # -------------------------
    # MOVEMENT
    # -------------------------

    def move_player(self, direction):

        old_room = self.player.current_room

        # Move through the infinite dungeon
        moved = self.dungeon.move(direction)

        if not moved:

            self.ui.show_error("Invalid direction.")

            return

        # Update player location
        self.player.current_room = self.dungeon.current_room

        # Reaching the normal exit immediately wins the run.
        if self.check_for_exit():
            self.game_won = True
            return

        # -------------------------
        # NEW ROOM
        # -------------------------

        if self.player.current_room is not old_room:

            x, y = self.dungeon.get_position()

            self.ui.show_message(
                f"\nYou travel {direction}..."
            )

            self.ui.show_message(
                f"You enter: {self.player.current_room.name}"
            )

            self.ui.show_message(
                f"Dungeon coordinates: ({x}, {y})"
            )

            # -------------------------
            # RANDOM ENCOUNTER
            # -------------------------

            room = self.player.current_room

            if room.monsters:

                for monster in room.monsters:

                    self.ui.show_combat_start(monster)

                    monster.speak()

                    while monster.is_alive() and monster in room.monsters:

                        self.ui.show_combat_options()

                        choice = self.ui.get_combat_choice()

                        # -------------------------
                        # ATTACK
                        # -------------------------

                        if choice in ("1", "attack"):

                            if not self.attack():

                                return

                        # -------------------------
                        # DODGE
                        # -------------------------

                        elif choice in ("2", "dodge"):

                            if not self.dodge(monster):

                                return

                        # -------------------------
                        # ESCAPE
                        # -------------------------

                        elif choice in ("3", "escape", "run"):

                            if not self.escape(monster):

                                return

                            # Successful escape
                            if monster not in room.monsters:

                                break

                        # -------------------------
                        # DIALOGUE
                        # -------------------------

                        elif choice in ("4", "dialogue", "talk", "speak"):

                            if self.dialogue(monster):

                                # Successful dialogue removes the monster
                                if monster not in room.monsters:

                                    break

                        elif choice in ("5", "ability", "skill"):

                            if not self.player.use_ability(monster):
                                continue
                            if not monster.is_alive():
                                room.remove_monster(monster)
                                self.ui.show_monster_defeated(monster)
                                self.player.gain_xp(max(10, monster.max_health // 3))
                                loot = monster.generate_loot()
                                for item in loot:
                                    room.add_item(item)
                                    self.ui.show_message(f" - {item.name}")
                            elif not self.monster_attack(monster):
                                return

                        elif choice in ("6", "use"):

                            item_name = input("Use which item? ").strip()
                            if self.player.use_item(item_name):
                                if not self.monster_attack(monster):
                                    return

                        else:

                            self.ui.show_error(
                                "Choose Attack, Dodge, Escape, Dialogue, Ability, or Use."
                            )


    # -------------------------
    # LOOK / EXPLORE
    # -------------------------

    def explore(self):

        room = self.player.current_room

        x, y = self.dungeon.get_position()

        print(
            f"\nDungeon coordinates: ({x}, {y})"
        )

        room.explore()

    # -------------------------
    # TAKE ITEM
    # -------------------------

    def take_item(self, item_name):

        room = self.player.current_room

        found_item = None

        for item in room.items:

            if item.name.lower() == item_name.lower():

                found_item = item

                break

        if found_item:

            room.remove_item(found_item)

            self.player.add_item(found_item)

            self.ui.show_message(
                f"You picked up {found_item.name}."
            )

        else:

            self.ui.show_error(
                "That item isn't here."
            )

    # -------------------------
    # TALK TO NPC
    # -------------------------

    def talk_to_npc(self, npc_name=None):
        room = self.player.current_room

        if not room.npcs:
            self.ui.show_error("There is nobody here to talk to.")
            return

        npc = None

        # If no name is provided, talk to the first NPC
        if npc_name is None:
            npc = room.npcs[0]

        else:
            for character in room.npcs:
                if character.name.lower() == npc_name.lower():
                    npc = character
                    break

        if npc is None:
            self.ui.show_error("That person isn't here.")
            return

        try:
            npc.talk(self.player)
        except TypeError:
            npc.talk()

    # -------------------------
    # ATTACK
    # -------------------------

    def attack(self):

        room = self.player.current_room

        if not room.monsters:

            self.ui.show_error(
                "There are no monsters here."
            )

            return True

        monster = room.monsters[0]

        # Player attacks
        attack_successful = self.player.attack(monster)

        # Player died
        if self.player.health <= 0:

            self.ui.show_player_defeated()

            return False

        # Player missed
        if not attack_successful:

            if not self.monster_attack(monster):

                return False

            return True

        # Monster died
        if not monster.is_alive():

            room.remove_monster(monster)

            self.ui.show_monster_defeated(
                monster
            )

            # -------------------------
            # ENEMY LOOT
            # -------------------------

            loot = monster.generate_loot()

            if loot:

                self.ui.show_message(
                    f"\n{monster.name} dropped:"
                )

                for item in loot:

                    room.add_item(item)

                    self.ui.show_message(
                        f" - {item.name}"
                    )

                self.ui.show_message(
                    "\nThe loot is lying on the ground."
                )

            else:

                self.ui.show_message(
                    f"{monster.name} dropped nothing."
                )

            self.player.gain_xp(max(10, monster.max_health // 3))

            # The dungeon boss has an exceptionally rare key drop.
            if getattr(monster, "is_dungeon_boss", False):
                if random.random() < self.dungeon.boss_key_drop_chance:
                    from game.item import Item

                    key = Item(
                        "Ancient Dungeon Key",
                        "A mysterious key dropped by the Dungeon Warden. "
                        "Its purpose is unknown... for now.",
                        500
                    )
                    room.add_item(key)
                    self.ui.show_message(
                        "\nRARE DROP! The Dungeon Warden dropped an Ancient Dungeon Key!"
                    )
                else:
                    self.ui.show_message(
                        "The Dungeon Warden did not drop the Ancient Dungeon Key."
                    )

            return True

        # Monster survived
        if not self.monster_attack(monster):

            return False

        return True

    # -------------------------
    # USE / EQUIP / INSPECT
    # -------------------------

    def use_item(self, item_name):
        if self.player.use_item(item_name):
            self.ui.show_message(f"Health: {self.player.health}/{self.player.max_health} | Magicka: {self.player.magicka}")

    def equip_item(self, item_name):
        self.player.equip_item(item_name)

    def inspect_item(self, item_name):
        item = next((i for i in self.player.inventory if i.name.lower() == item_name.lower()), None)
        if item:
            item.inspect()
        else:
            self.ui.show_error("That item is not in your inventory.")

    def load_game(self):
        data = SaveSystem.load()
        if not data:
            return

        player_data = data.get("player", {})
        dungeon_data = data.get("dungeon", {})

        self.player.name = player_data.get("name", self.player.name)
        self.player.gender = player_data.get("gender")
        self.player.race = player_data.get("race")
        self.player.character_class = player_data.get("character_class")
        self.player.passive = player_data.get("passive")
        self.player.health = player_data.get("health", self.player.health)
        self.player.max_health = player_data.get("max_health", self.player.max_health)
        self.player.stamina = player_data.get("stamina", self.player.stamina)
        self.player.magicka = player_data.get("magicka", self.player.magicka)
        self.player.gold = player_data.get("gold", self.player.gold)
        self.player.level = player_data.get("level", 1)
        self.player.xp = player_data.get("xp", 0)
        self.player.xp_to_next_level = player_data.get("xp_to_next_level", 100)

        from game.item import Item
        self.player.inventory = []
        for saved_item in player_data.get("inventory", []):
            self.player.inventory.append(
                Item(
                    saved_item.get("name", "Unknown Item"),
                    saved_item.get("description", ""),
                    saved_item.get("value", 0),
                    saved_item.get("item_type", "misc"),
                    saved_item.get("power", 0),
                    saved_item.get("defense", 0)
                )
            )

        # Restore dungeon seed data before rebuilding the current room.
        if "exit_x" in dungeon_data and "exit_y" in dungeon_data:
            self.dungeon.exit_x = dungeon_data["exit_x"]
            self.dungeon.exit_y = dungeon_data["exit_y"]
        self.dungeon.rooms = {}
        self.dungeon.current_x = dungeon_data.get("current_x", 0)
        self.dungeon.current_y = dungeon_data.get("current_y", 0)
        self.dungeon.current_room = self.dungeon.generate_room(
            self.dungeon.current_x, self.dungeon.current_y,
            starting_room=(self.dungeon.current_x == 0 and self.dungeon.current_y == 0)
        )
        self.player.current_room = self.dungeon.current_room

        self.player.equipped_weapon = None
        self.player.equipped_armor = None
        self.player.equipped_shield = None
        for item in self.player.inventory:
            if item.name == player_data.get("equipped_weapon"):
                self.player.equipped_weapon = item
            elif item.name == player_data.get("equipped_armor"):
                self.player.equipped_armor = item
            elif item.name == player_data.get("equipped_shield"):
                self.player.equipped_shield = item

        self.game_won = False
        self.ui.show_message(f"Game loaded. Welcome back, {self.player.name}!")

    # -------------------------
    # START GAME
    # -------------------------

    def start(self):

        self.ui.show_message(
            f"\nWelcome to the dungeon, "
            f"{self.player.name}!"
        )

        self.ui.show_message(
            "\nYou stand at the entrance of a vast dungeon."
        )

        self.ui.show_message(
            "Your goal is to explore the dungeon and find the exit."
        )

        self.ui.show_message(
            "A legendary guardian and its key may exist somewhere in the darkness, "
            "but finding them is extraordinarily unlikely."
        )

        self.ui.show_message(
            "Type 'look' to examine your surroundings."
        )

        while True:

            # -------------------------
            # COMMANDS
            # -------------------------

            self.ui.show_commands()

            command = self.ui.get_command()

            # -------------------------
            # MOVEMENT
            # -------------------------

            if command in (
                "north",
                "south",
                "east",
                "west"
            ):

                self.move_player(command)

                if self.player.health <= 0 or self.game_won:

                    break

            # -------------------------
            # LOOK
            # -------------------------

            elif command in (
                "look",
                "search",
                "explore",
                "observe"
            ):

                self.explore()

            # -------------------------
            # TAKE ITEM
            # -------------------------

            elif command.startswith("take "):

                item_name = command[5:].strip()

                self.take_item(item_name)

            elif command.startswith("use "):

                self.use_item(command[4:].strip())

            elif command.startswith("equip "):

                self.equip_item(command[6:].strip())

            elif command.startswith("inspect "):

                self.inspect_item(command[8:].strip())

            # -------------------------
            # ATTACK
            # -------------------------

            elif command == "talk":
                self.talk_to_npc()
            elif command.startswith("talk "):
                self.talk_to_npc(command[5:].strip())
            elif command == "attack":

                if not self.attack():

                    break

            # -------------------------
            # INVENTORY
            # -------------------------

            elif command == "inventory":

                self.ui.show_inventory(
                    self.player
                )

            # -------------------------
            # STATS
            # -------------------------

            elif command == "stats":

                self.ui.show_player_stats(
                    self.player
                )

            # -------------------------
            # OBJECTIVE
            # -------------------------

            elif command == "objective":

                self.ui.show_message(
                    "Your objective: explore the dungeon and find the normal exit."
                )
                self.ui.show_message(
                    "The exit is guaranteed to exist somewhere in the dungeon."
                )
                self.ui.show_message(
                    "A legendary boss chamber may very rarely appear, and the boss "
                    "has a very small chance to drop the Ancient Dungeon Key."
                )

            # -------------------------
            # QUIT
            # -------------------------

            elif command == "save":

                SaveSystem.save(self)

            elif command == "load":

                self.load_game()

            elif command == "quit":

                if self.ui.confirm_exit():

                    break

            # -------------------------
            # UNKNOWN COMMAND
            # -------------------------

            else:

                self.ui.show_error(
                    "Unknown command."
                )


if __name__ == "__main__":

    Game().start()