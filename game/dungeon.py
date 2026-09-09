import random

from game.room import Room
from game.item import Item
from game.monster import Monster
from game.lost_traveler import LostTraveler
from game.merchant import Merchant


class Dungeon:

    def __init__(self):
        # Rooms are stored by coordinates.
        # Example:
        # (0, 0) = starting room
        # (1, 0) = east
        # (-1, 0) = west
        # (0, 1) = south
        # (0, -1) = north
        self.rooms = {}

        self.current_x = 0
        self.current_y = 0

        # -------------------------
        # DUNGEON OBJECTIVES
        # -------------------------
        # Every dungeon has a normal exit. Its location is randomized
        # when the dungeon starts, but it is never placed in the entrance.
        self.exit_min_distance = 5
        self.exit_max_distance = 12
        self.exit_x, self.exit_y = self._choose_exit_location()

        # The boss encounter is intentionally extremely rare.
        # These values are easy to tune later.
        self.special_room_chance = 0.01      # 1% of newly discovered rooms
        self.boss_spawn_chance = 0.10        # 10% if the rare room occurs
        self.boss_key_drop_chance = 0.05     # 5% after defeating the boss

        # Create the starting room
        self.current_room = self.generate_room(0, 0, starting_room=True)

    # -------------------------
    # EXIT LOCATION
    # -------------------------

    def _choose_exit_location(self):
        """Choose a guaranteed normal exit somewhere away from the entrance."""
        while True:
            x = random.randint(-self.exit_max_distance, self.exit_max_distance)
            y = random.randint(-self.exit_max_distance, self.exit_max_distance)
            distance = abs(x) + abs(y)

            if self.exit_min_distance <= distance <= self.exit_max_distance:
                return x, y

    # -------------------------
    # ROOM GENERATION
    # -------------------------

    def generate_room(self, x, y, starting_room=False):

        # If this room already exists, return it.
        if (x, y) in self.rooms:
            return self.rooms[(x, y)]

        # -------------------------
        # ROOM TYPES
        # -------------------------

        room_types = [
            (
                "Dark Hallway",
                "A long stone hallway disappears into the darkness."
            ),
            (
                "Cavern",
                "A damp natural cavern surrounds you."
            ),
            (
                "Crypt",
                "Ancient tombs line the walls."
            ),
            (
                "Abandoned Armory",
                "Broken weapons and rusty armor litter the floor."
            ),
            (
                "Forgotten Library",
                "Dusty bookshelves disappear into the darkness."
            ),
            (
                "Underground Shrine",
                "An ancient shrine stands silently in the darkness."
            ),
            (
                "Collapsed Chamber",
                "Broken stone blocks cover parts of the floor."
            ),
            (
                "Underground Lake",
                "Dark water stretches into the shadows."
            ),
            (
                "Bloodstained Chamber",
                "The floor is stained with old, dark blood."
            ),
            (
                "Ancient Prison",
                "Rusty cells line the walls of this forgotten prison."
            ),
            (
                "Mysterious Chamber",
                "You cannot tell what this chamber was once used for."
            ),
            (
                "Torchlit Corridor",
                "Old torches burn weakly along the walls."
            )
        ]

        # Starting room is always safe.
        if starting_room:
            name = "Dungeon Entrance"
            description = (
                "The entrance to the dungeon. "
                "Cold air flows in from behind you."
            )

        else:
            name, description = random.choice(room_types)

        room = Room(name, description)

        # The normal exit is guaranteed to exist at the randomized
        # coordinates chosen when this dungeon was created.
        if not starting_room and (x, y) == (self.exit_x, self.exit_y):
            room.name = "Dungeon Exit"
            room.description = (
                "A massive ancient doorway stands before you. "
                "Cold air flows from beyond it. This must be the way out."
            )
            room.is_exit = True

        # Generate atmosphere
        room.generate_atmosphere()

        # -------------------------
        # RANDOM ITEMS
        # -------------------------

        # Exit rooms and the starting room are kept free of random clutter.
        if not starting_room and not room.is_exit:
            self.generate_items(room)

        # -------------------------
        # EXTREMELY RARE BOSS ROOM
        # -------------------------

        if not starting_room and not room.is_exit:
            self.generate_special_boss_room(room)

        # -------------------------
        # RANDOM ENEMIES
        # -------------------------

        if not room.is_boss_room and not room.is_exit:
            self.generate_monsters(room)

        # -------------------------
        # RANDOM NPC
        # -------------------------

        if not room.is_boss_room and not room.is_exit:
            self.generate_npc(room)

        # Save room
        self.rooms[(x, y)] = room

        return room

        # Save room
        self.rooms[(x, y)] = room

        return room

    # -------------------------
    # RARE BOSS ENCOUNTER
    # -------------------------

    def generate_special_boss_room(self, room):
        """Occasionally turn a newly discovered room into a rare boss room."""
        if random.random() >= self.special_room_chance:
            return

        room.name = "Forbidden Boss Chamber"
        room.description = (
            "The air is unnaturally still. Ancient symbols cover the walls, "
            "and a huge sealed chamber dominates the room."
        )
        room.is_boss_room = True

        # Even after finding the exceptionally rare chamber, the boss itself
        # has another very small chance to actually be present.
        if random.random() >= self.boss_spawn_chance:
            return

        boss = Monster(
            "Dungeon Warden",
            300,
            35,
            dialogue=[
                "Dungeon Warden: You were never meant to find this chamber.",
                "Dungeon Warden: Turn back, intruder.",
                "Dungeon Warden: The dungeon itself has chosen your grave.",
                "Dungeon Warden: Few ever reach me. Fewer survive.",
                "Dungeon Warden: YOU WILL NOT LEAVE!"
            ],
            dialogue_success_chance=5,
            attack_sounds=[
                "Dungeon Warden: RAAAAAAAH!",
                "Dungeon Warden: TRESPASSER!",
                "Dungeon Warden: DIE!",
                "Dungeon Warden: *the chamber shakes with a roar*",
                "Dungeon Warden: YOU CANNOT ESCAPE!"
            ],
            reactions=[
                "Dungeon Warden: Impressive... but futile.",
                "Dungeon Warden: You dare wound me?",
                "Dungeon Warden: *the Warden roars in fury*"
            ],
            death_sounds=[
                "Dungeon Warden: No... the key...",
                "Dungeon Warden: *the ancient guardian collapses*",
                "Dungeon Warden: You... actually defeated me..."
            ]
        )

        # Mark the boss so Game can give it the special key-drop rule.
        boss.is_dungeon_boss = True
        room.add_monster(boss)

    # -------------------------
    # ITEM GENERATION
    # -------------------------

    def generate_items(self, room):

        # 45% chance of an item
        if random.random() > 0.45:
            return

        item_types = [
            Item(
                "Rusty Sword",
                "An old sword. Better than fighting with your fists.",
                10
            ),

            Item(
                "Leather Armor",
                "Simple armor that offers basic protection.",
                20
            ),

            Item(
                "Health Potion",
                "Restores a little health.",
                25
            ),

            Item(
                "Pile of Gold",
                "A small pile of shiny gold coins.",
                100
            ),

            Item(
                "Ancient Coin",
                "An old coin from a forgotten civilization.",
                50
            ),

            Item(
                "Silver Ring",
                "A small silver ring. It may be worth something.",
                75
            )
        ]

        # Usually one item, occasionally two
        number_of_items = random.choices(
            [1, 2],
            weights=[85, 15]
        )[0]

        selected_items = random.sample(
            item_types,
            min(number_of_items, len(item_types))
        )

        for item in selected_items:
            room.add_item(item)

    # -------------------------
    # MONSTER GENERATION
    # -------------------------

    def generate_monsters(self, room):

        # Starting room is always safe.
        if room.name == "Dungeon Entrance":
            return

        # 55% chance that NO enemy appears.
        if random.random() < 0.55:
            return

        monster_types = [

            Monster(
                "Goblin",
                50,
                10,
                dialogue=[
                    "Goblin: Hehehe... shiny!",
                    "Goblin: You got gold?",
                    "Goblin: GOBLIN HUNGRY!",
                    "Goblin: Stupid human!",
                    "Goblin: Get out of my cave!"
                ],
                dialogue_success_chance=65,
                attack_sounds=[
                    "Goblin: YAAAA!",
                    "Goblin: STAB!",
                    "Goblin: GRAAA!",
                    "Goblin: DIE!",
                    "Goblin: *high-pitched screech*"
                ]
            ),

            Monster(
                "Skeleton",
                75,
                15,
                dialogue=[
                    "Skeleton: ...You disturb the dead.",
                    "Skeleton: Your bones will join ours.",
                    "Skeleton: *rattles ominously*",
                    "Skeleton: There is no escape from death.",
                    "Skeleton: We have waited for you..."
                ],
                dialogue_success_chance=40,
                attack_sounds=[
                    "Skeleton: *rattling scream*",
                    "Skeleton: DIE, MORTAL!",
                    "Skeleton: *CLACK CLACK CLACK*",
                    "Skeleton: HAAAA!",
                    "Skeleton: *bone-rattling roar*"
                ]
            ),

            Monster(
                "Bandit",
                65,
                18,
                dialogue=[
                    "Bandit: Drop your weapons and hand over the gold.",
                    "Bandit: Wrong place, friend.",
                    "Bandit: This road belongs to us.",
                    "Bandit: Your money or your life!",
                    "Bandit: I've killed better fighters than you."
                ],
                dialogue_success_chance=55,
                attack_sounds=[
                    "Bandit: HYAA!",
                    "Bandit: Take this!",
                    "Bandit: GOTCHA!",
                    "Bandit: *draws blade*",
                    "Bandit: DIE!"
                ]
            ),

            Monster(
                "Troll",
                150,
                22,
                dialogue=[
                    "Troll: Little thing... why you enter troll cave?",
                    "Troll: Troll smell fear.",
                    "Troll: YOU LOOK LIKE DINNER!",
                    "Troll: Leave cave!",
                    "Troll: Troll crush you!"
                ],
                dialogue_success_chance=30,
                attack_sounds=[
                    "Troll: RAAAAAAARGH!",
                    "Troll: CRUSH!",
                    "Troll: SMASH!",
                    "Troll: *thunders forward*",
                    "Troll: DIE, LITTLE THING!"
                ]
            ),

            Monster(
                "Orc",
                120,
                20,
                dialogue=[
                    "Orc: You have entered the territory of the Orcs.",
                    "Orc: Prove your strength!",
                    "Orc: Weakness will be your death.",
                    "Orc: I will grind your bones beneath my axe.",
                    "Orc: COME! FIGHT!"
                ],
                dialogue_success_chance=40,
                attack_sounds=[
                    "Orc: WAAAAAGH!",
                    "Orc: FOR GLORY!",
                    "Orc: RAAAAH!",
                    "Orc: *war cry*",
                    "Orc: DIE!"
                ]
            ),

            Monster(
                "Demon",
                175,
                28,
                dialogue=[
                    "Demon: Your soul smells delicious.",
                    "Demon: You should not have crossed this threshold.",
                    "Demon: The darkness welcomes you.",
                    "Demon: I have waited centuries for a soul like yours.",
                    "Demon: SCREAM, MORTAL!"
                ],
                dialogue_success_chance=20,
                attack_sounds=[
                    "Demon: RAAAAAAAH!",
                    "Demon: BURN IN HELL!",
                    "Demon: *infernal roar*",
                    "Demon: YOUR SOUL IS MINE!",
                    "Demon: DIE, MORTAL!"
                ]
            ),

            Monster(
                "Spirit",
                90,
                17,
                dialogue=[
                    "Spirit: Leave this place...",
                    "Spirit: Why have you awakened me?",
                    "Spirit: You cannot escape death.",
                    "Spirit: *whispers from the darkness*",
                    "Spirit: Join us..."
                ],
                dialogue_success_chance=35,
                attack_sounds=[
                    "Spirit: *ghostly scream*",
                    "Spirit: AAAAAAAAH!",
                    "Spirit: *whispers* DIE...",
                    "Spirit: *unnatural shriek*",
                    "Spirit: COME WITH US!"
                ]
            ),

            Monster(
                "Vampire",
                130,
                24,
                dialogue=[
                    "Vampire: Such warm blood...",
                    "Vampire: You have no idea what hunts you.",
                    "Vampire: I can hear your heart beating.",
                    "Vampire: How fortunate. Dinner has arrived.",
                    "Vampire: Your blood will sustain me."
                ],
                dialogue_success_chance=25,
                attack_sounds=[
                    "Vampire: *hisses*",
                    "Vampire: DIE!",
                    "Vampire: *vicious snarl*",
                    "Vampire: YOUR BLOOD!",
                    "Vampire: *fangs snap*"
                ]
            )
        ]

        # Rare enemies should be rarer.
        weights = [
            25,  # Goblin
            20,  # Skeleton
            20,  # Bandit
            12,  # Troll
            10,  # Orc
            5,   # Demon
            5,   # Spirit
            3    # Vampire
        ]

        monster = random.choices(
            monster_types,
            weights=weights,
            k=1
        )[0]

        room.add_monster(monster)


    # -------------------------
    # NPC GENERATION
    # -------------------------

    def generate_npc(self, room):
        # 10% chance of a neutral NPC appearing
        if random.random() > 0.10:
            return

        npc_types = [
            LostTraveler,
            Merchant
        ]

        npc_class = random.choice(npc_types)
        npc = npc_class()

        room.add_npc(npc)





    # -------------------------
    # MOVEMENT
    # -------------------------

    def move(self, direction):

        x = self.current_x
        y = self.current_y

        if direction == "north":
            y -= 1

        elif direction == "south":
            y += 1

        elif direction == "east":
            x += 1

        elif direction == "west":
            x -= 1

        else:
            return False

        # Generate the room if we have never visited it.
        self.current_room = self.generate_room(x, y)

        self.current_x = x
        self.current_y = y

        return True

    # -------------------------
    # CURRENT ROOM
    # -------------------------

    def get_current_room(self):
        return self.current_room

    # -------------------------
    # POSITION
    # -------------------------

    def get_position(self):
        return self.current_x, self.current_y