import random
import pygame

from game.character import CharacterCreation
from game.player import Player
from game.dungeon import Dungeon
from game.save_system import SaveSystem
from game.item import Item


WIDTH, HEIGHT = 1100, 700
FPS = 60


class PygameGame:
    """Graphical front-end for the original dungeon crawler classes."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Cryptfall")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(None, 25)
        self.small = pygame.font.Font(None, 20)
        self.large = pygame.font.Font(None, 38)
        self.title = pygame.font.Font(None, 58)

        self.running = True
        self.state = "name"
        self.name = ""
        self.character = None
        self.player = None
        self.dungeon = None
        self.enemy = None
        self.messages = [
            "Welcome to Cryptfall.",
            "Create your character to begin."
        ]
        self.overlay = None

    # ---------- General UI ----------

    def message(self, text):
        self.messages.append(str(text))
        self.messages = self.messages[-7:]

    def draw_text(self, text, x, y, font=None):
        surface = (font or self.font).render(str(text), True, (225, 225, 225))
        self.screen.blit(surface, (x, y))

    def panel(self, rect, fill=(25, 25, 31), border=(85, 85, 98)):
        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=8)

    def bar(self, x, y, w, h, value, maximum, label):
        maximum = max(1, int(maximum))
        value = max(0, min(int(value), maximum))

        pygame.draw.rect(
            self.screen,
            (50, 50, 55),
            (x, y, w, h),
            border_radius=4
        )

        ratio = value / maximum

        pygame.draw.rect(
            self.screen,
            (155, 155, 165),
            (x, y, int(w * ratio), h),
            border_radius=4
        )

        self.draw_text(
            f"{label}: {value}/{maximum}",
            x + 7,
            y + 2,
            self.small
        )

    # ---------- Character creation ----------

    def handle_creation(self, event):
        if event.key == pygame.K_BACKSPACE:
            if self.state == "name":
                self.name = self.name[:-1]
            return

        if self.state == "name":
            if event.key == pygame.K_RETURN and self.name.strip():
                self.character = CharacterCreation(self.name.strip())
                self.state = "gender"

            elif event.unicode.isprintable() and len(self.name) < 20:
                self.name += event.unicode

            return

        if self.state == "gender":
            if event.key in (pygame.K_1, pygame.K_2):
                self.character.gender = (
                    "Male" if event.key == pygame.K_1 else "Female"
                )
                self.state = "race"
            return

        if self.state == "race":
            choices = {
                pygame.K_1: "Human",
                pygame.K_2: "Elf",
                pygame.K_3: "Dwarf",
                pygame.K_4: "Orc",
                pygame.K_5: "Halfling",
            }

            if event.key in choices:
                self.choose_race(choices[event.key])
                self.state = "class"

            return

        if self.state == "class":
            choices = {
                pygame.K_1: "Warrior",
                pygame.K_2: "Mage",
                pygame.K_3: "Rogue",
            }

            if event.key in choices:
                self.character.character_class = choices[event.key]
                self.apply_class_stats()
                self.start_adventure()

    def choose_race(self, race):
        self.character.race = race

        if race == "Human":
            self.character.passive = "Adaptable"
            self.character.health += 5
            self.character.stamina += 5
            self.character.magicka += 5

        elif race == "Elf":
            self.character.passive = "Arcane Affinity"
            self.character.stamina += 10
            self.character.magicka += 20

        elif race == "Dwarf":
            self.character.passive = "Tough"
            self.character.health += 30

        elif race == "Orc":
            self.character.passive = "Brutal"
            self.character.health += 25
            self.character.stamina += 20

        elif race == "Halfling":
            self.character.passive = "Lucky"
            self.character.stamina += 25

    def apply_class_stats(self):
        if self.character.character_class == "Warrior":
            self.character.health += 150
            self.character.stamina += 120
            self.character.magicka += 50

        elif self.character.character_class == "Mage":
            self.character.health += 80
            self.character.stamina += 80
            self.character.magicka += 150

        elif self.character.character_class == "Rogue":
            self.character.health += 100
            self.character.stamina += 150
            self.character.magicka += 75

    def start_adventure(self):
        self.player = Player(self.character.name)

        self.player.gender = self.character.gender
        self.player.race = self.character.race
        self.player.character_class = self.character.character_class
        self.player.passive = self.character.passive

        # CharacterCreation contains the final starting stats.
        # Keep those values as BOTH current and maximum resources.
        self.player.max_health = max(1, self.character.health)
        self.player.health = self.player.max_health

        self.player.max_stamina = max(1, self.character.stamina)
        self.player.stamina = self.player.max_stamina

        self.player.max_magicka = max(1, self.character.magicka)
        self.player.magicka = self.player.max_magicka

        self.player.setup_starting_inventory()
        self.player.auto_equip_starting_gear()

        self.dungeon = Dungeon()
        self.player.current_room = self.dungeon.current_room

        self.enemy = None
        self.overlay = None
        self.state = "play"

        self.message(f"Welcome, {self.player.name}.")
        self.message(
            "Find the dungeon exit. Move with WASD or arrow keys."
        )

    # ---------- Movement / exploration ----------

    def move(self, direction):
        if not self.player or not self.dungeon:
            return

        if self.enemy:
            self.message("You must deal with the enemy first.")
            return

        old_room = self.player.current_room

        if not self.dungeon.move(direction):
            self.message("You cannot go that way.")
            return

        self.player.current_room = self.dungeon.current_room
        room = self.player.current_room

        if room is old_room:
            return

        x, y = self.dungeon.get_position()

        self.message(f"You travel {direction}.")
        self.message(f"You enter: {room.name} ({x}, {y})")

        # The exit is now a proper objective:
        # reaching it with the Ancient Dungeon Key wins.
        if room.is_exit:
            self.check_exit()
            return

        if not getattr(room, "visited", False):
            room.generate_atmosphere()
            room.visited = True

        if room.monsters:
            self.enemy = room.monsters[0]
            self.message(f"A {self.enemy.name} appears!")

            if getattr(self.enemy, "dialogue", None):
                self.message(random.choice(self.enemy.dialogue))

        elif room.items:
            self.message(f"You notice: {room.items[0].name}")

        elif room.npcs:
            self.message(f"You notice {room.npcs[0].name}.")

    def has_exit_key(self):
        if not self.player:
            return False

        return any(
            item.name.lower() == "ancient dungeon key"
            for item in self.player.inventory
        )

    def check_exit(self):
        if not self.player.current_room.is_exit:
            return False

        if self.has_exit_key():
            self.state = "won"
            self.message("The Ancient Dungeon Key fits the lock.")
            self.message("The ancient doors slowly open.")
            self.message("You escaped Cryptfall!")
            return True

        self.message(
            "The ancient exit is sealed. "
            "Something seems to be missing..."
        )
        self.message(
            "A strange inscription mentions an ancient key."
        )
        return False

    # ---------- Combat ----------

    def monster_attack(self):
        if not self.enemy or not self.player:
            return

        raw_damage = self.enemy.attack()

        # Player.take_damage() already applies race passive and equipment
        # defense. Do not apply those reductions a second time here.
        damage = self.player.take_damage(raw_damage)

        self.message(
            f"{self.enemy.name} hits you for {damage} damage."
        )

        if self.player.health <= 0:
            self.enemy = None
            self.state = "dead"
            self.message("You have been defeated.")

    def player_attack(self):
        if not self.enemy or not self.player:
            return

        base = self.player.get_attack_damage()
        damage = random.randint(
            max(1, base - 5),
            base + 5
        )

        # get_attack_damage() already includes the Brutal passive.
        self.enemy.take_damage(damage)

        self.message(
            f"You attack {self.enemy.name} for {damage} damage."
        )

        if not self.enemy.is_alive():
            self.defeat_enemy()
        else:
            self.monster_attack()

    def use_ability(self):
        if not self.enemy or not self.player:
            return

        enemy = self.enemy

        # Let Player own the class ability logic so the console and Pygame
        # versions use the same resource costs and damage rules.
        success = self.player.use_ability(enemy)

        if not success:
            return

        if not enemy.is_alive():
            self.defeat_enemy()
        else:
            self.monster_attack()

    def dodge(self):
        if not self.enemy:
            return

        if random.random() < 0.50:
            self.message(f"You dodge {self.enemy.name}'s attack!")
        else:
            self.message("Your dodge fails!")
            self.monster_attack()

    def escape(self):
        if not self.enemy:
            return

        if random.random() < 0.50:
            self.message(f"You escape from {self.enemy.name}.")

            self.player.current_room.remove_monster(self.enemy)
            self.enemy = None

        else:
            self.message("You fail to escape!")
            self.monster_attack()

    def dialogue(self):
        if not self.enemy:
            return

        if getattr(self.enemy, "dialogue", None):
            self.message(random.choice(self.enemy.dialogue))

        chance = getattr(
            self.enemy,
            "dialogue_success_chance",
            0
        )

        if random.randint(1, 100) <= chance:
            self.message(f"{self.enemy.name} backs away.")
            self.player.current_room.remove_monster(self.enemy)
            self.enemy = None

        else:
            self.message("Your words fail.")
            self.monster_attack()

    def defeat_enemy(self):
        if not self.enemy:
            return

        enemy = self.enemy
        room = self.player.current_room

        room.remove_monster(enemy)

        xp = max(
            10,
            getattr(enemy, "max_health", 0) // 3
        )

        old_level = self.player.level
        self.player.gain_xp(xp)

        self.message(
            f"{enemy.name} defeated! +{xp} XP."
        )

        if self.player.level > old_level:
            self.message(
                f"LEVEL UP! You are now level "
                f"{self.player.level}."
            )

        # Normal monster loot.
        loot = enemy.generate_loot()

        if loot:
            for item in loot:
                room.add_item(item)
                self.message(f"Dropped: {item.name}")

        # Special Dungeon Warden key.
        if getattr(enemy, "is_dungeon_boss", False):
            if random.random() < self.dungeon.boss_key_drop_chance:
                key = Item(
                    "Ancient Dungeon Key",
                    "A mysterious key dropped by the Dungeon Warden.",
                    500
                )
                room.add_item(key)
                self.message(
                    "RARE DROP: Ancient Dungeon Key!"
                )
            else:
                self.message(
                    "The Dungeon Warden did not drop the key."
                )

        self.enemy = None

    # ---------- Items / NPC ----------

    def take_item(self):
        if not self.player:
            return

        room = self.player.current_room

        if not room.items:
            self.message("There are no items here.")
            return

        item = room.items.pop(0)

        # Gold is immediately added to the player's gold rather than
        # occupying an inventory slot.
        if item.name.lower() == "pile of gold":
            amount = max(0, getattr(item, "value", 0))
            self.player.gold += amount
            self.message(f"You picked up {amount} gold.")
            return

        self.player.add_item(item)
        self.message(f"You picked up {item.name}.")

    def use_item(self, index=0):
        if not self.player:
            return

        consumables = [
            (i, item)
            for i, item in enumerate(self.player.inventory)
            if getattr(item, "item_type", None) == "consumable"
        ]

        if not consumables:
            self.message("You have no usable items.")
            return

        # Cycle through available consumables using the supplied index.
        _, item = consumables[index % len(consumables)]

        # Use the Player implementation so max_health/max_magicka stay
        # consistent between the graphical and text interfaces.
        used = self.player.use_item(item.name)

        if not used:
            return

        self.message(f"Used {item.name}.")

        if self.enemy:
            self.monster_attack()

    def equip_first(self, item_type):
        if not self.player:
            return

        for item in self.player.inventory:
            if getattr(item, "item_type", None) == item_type:
                if self.player.equip_item(item.name):
                    self.message(f"Equipped {item.name}.")
                return

        self.message("No matching equipment found.")

    def talk(self):
        if not self.player:
            return

        room = self.player.current_room

        if not room.npcs:
            self.message("There is nobody here to talk to.")
            return

        npc = room.npcs[0]

        self.message(
            f"{npc.name}: {npc.description}"
        )

        try:
            npc.talk(self.player)
        except TypeError:
            npc.talk()

    # ---------- Save / load ----------

    def save(self):
        if not self.player:
            return

        try:
            SaveSystem.save(self)
            self.message("Game saved.")
        except Exception as exc:
            self.message(f"Save failed: {exc}")

    def load(self):
        try:
            data = SaveSystem.load()
        except Exception as exc:
            self.message(f"Load failed: {exc}")
            return

        if not data:
            self.message("No save file found.")
            return

        p = data.get("player", {})

        self.player = Player(
            p.get("name", "Adventurer")
        )

        # Restore all player fields supported by the current save format.
        for key in (
            "gender",
            "race",
            "character_class",
            "passive",
            "health",
            "max_health",
            "stamina",
            "magicka",
            "max_stamina",
            "max_magicka",
            "gold",
            "level",
            "xp",
            "xp_to_next_level"
        ):
            if key in p:
                setattr(self.player, key, p[key])

        # Older save files may not contain the max resource fields.
        # Derive sensible values instead of crashing or showing 0.
        if "max_stamina" not in p:
            self.player.max_stamina = max(
                self.player.stamina,
                100 + max(0, self.player.level - 1) * 10
            )

        if "max_magicka" not in p:
            self.player.max_magicka = max(
                self.player.magicka,
                100 + max(0, self.player.level - 1) * 10
            )

        self.player.inventory = []

        for saved in p.get("inventory", []):
            self.player.inventory.append(
                Item(
                    saved.get("name", "Unknown Item"),
                    saved.get("description", ""),
                    saved.get("value", 0),
                    saved.get("item_type", "misc"),
                    saved.get("power", 0),
                    saved.get("defense", 0),
                )
            )

        # Rebuild the dungeon using the saved exit/current position.
        self.dungeon = Dungeon()

        d = data.get("dungeon", {})

        self.dungeon.exit_x = d.get(
            "exit_x",
            self.dungeon.exit_x
        )
        self.dungeon.exit_y = d.get(
            "exit_y",
            self.dungeon.exit_y
        )

        self.dungeon.current_x = d.get(
            "current_x",
            0
        )
        self.dungeon.current_y = d.get(
            "current_y",
            0
        )

        self.dungeon.rooms = {}

        self.dungeon.current_room = (
            self.dungeon.generate_room(
                self.dungeon.current_x,
                self.dungeon.current_y,
                starting_room=(
                    self.dungeon.current_x == 0
                    and self.dungeon.current_y == 0
                )
            )
        )

        self.player.current_room = self.dungeon.current_room

        # Restore equipped items by name.
        self.player.equipped_weapon = next(
            (
                item
                for item in self.player.inventory
                if item.name == p.get("equipped_weapon")
            ),
            None
        )

        self.player.equipped_armor = next(
            (
                item
                for item in self.player.inventory
                if item.name == p.get("equipped_armor")
            ),
            None
        )

        self.player.equipped_shield = next(
            (
                item
                for item in self.player.inventory
                if item.name == p.get("equipped_shield")
            ),
            None
        )

        self.enemy = None
        self.overlay = None
        self.state = "play"

        self.message(
            f"Game loaded. Welcome back, {self.player.name}."
        )

    # ---------- Drawing ----------

    def draw_creation(self):
        self.screen.fill((11, 11, 16))

        self.draw_text(
            "CRYPTFALL",
            80,
            55,
            self.title
        )

        self.draw_text(
            "A dungeon crawler",
            84,
            115,
            self.large
        )

        self.panel((80, 190, 940, 350))

        if self.state == "name":
            self.draw_text(
                "Enter your name:",
                120,
                235,
                self.large
            )

            self.draw_text(
                self.name + "_",
                120,
                300,
                self.large
            )

            self.draw_text(
                "ENTER to continue",
                120,
                390
            )

        elif self.state == "gender":
            self.draw_text(
                f"Name: {self.character.name}",
                120,
                220
            )

            self.draw_text(
                "Choose your gender",
                120,
                270,
                self.large
            )

            self.draw_text(
                "1  Male",
                150,
                340
            )

            self.draw_text(
                "2  Female",
                150,
                380
            )

        elif self.state == "race":
            self.draw_text(
                "Choose your race",
                120,
                220,
                self.large
            )

            for i, race in enumerate(
                ("Human", "Elf", "Dwarf", "Orc", "Halfling"),
                1
            ):
                self.draw_text(
                    f"{i}  {race}",
                    150,
                    270 + i * 42
                )

        else:
            self.draw_text(
                "Choose your class",
                120,
                220,
                self.large
            )

            for i, cls in enumerate(
                ("Warrior", "Mage", "Rogue"),
                1
            ):
                self.draw_text(
                    f"{i}  {cls}",
                    150,
                    280 + i * 50
                )

    def draw_play(self):
        self.screen.fill((13, 14, 18))

        room = self.player.current_room

        self.draw_text(
            "CRYPTFALL",
            30,
            20,
            self.large
        )

        self.draw_text(
            room.name,
            30,
            65,
            self.font
        )

        # ---------- Map ----------

        self.panel((25, 105, 520, 335))

        self.draw_text(
            "DUNGEON MAP",
            45,
            125,
            self.font
        )

        cx, cy = 270, 275
        size = 48
        px, py = self.dungeon.get_position()

        for (x, y), r in self.dungeon.rooms.items():
            sx = cx + (x - px) * size
            sy = cy + (y - py) * size

            if 45 <= sx <= 500 and 155 <= sy <= 405:
                pygame.draw.rect(
                    self.screen,
                    (55, 55, 63),
                    (sx, sy, 40, 40),
                    border_radius=4
                )

                if r.monsters:
                    pygame.draw.circle(
                        self.screen,
                        (185, 185, 190),
                        (sx + 20, sy + 20),
                        7
                    )

                if getattr(r, "is_boss_room", False):
                    pygame.draw.rect(
                        self.screen,
                        (200, 200, 210),
                        (sx + 7, sy + 7, 26, 26),
                        2
                    )

                if r.is_exit:
                    pygame.draw.rect(
                        self.screen,
                        (210, 210, 215),
                        (sx + 9, sy + 9, 22, 22),
                        2
                    )

        pygame.draw.rect(
            self.screen,
            (235, 235, 240),
            (cx + 2, cy + 2, 36, 36),
            2
        )

        self.draw_text(
            "YOU",
            cx + 3,
            cy + 11,
            self.small
        )

        # ---------- Player panel ----------

        self.panel((570, 20, 505, 420))

        self.draw_text(
            self.player.name,
            595,
            42,
            self.large
        )

        self.draw_text(
            f"Lv {self.player.level}  "
            f"{self.player.race}  "
            f"{self.player.character_class}",
            595,
            85,
            self.font
        )

        self.bar(
            595,
            125,
            450,
            25,
            self.player.health,
            self.player.max_health,
            "HP"
        )

        self.bar(
            595,
            165,
            450,
            25,
            self.player.stamina,
            self.player.max_stamina,
            "STA"
        )

        self.bar(
            595,
            205,
            450,
            25,
            self.player.magicka,
            self.player.max_magicka,
            "MAG"
        )

        self.draw_text(
            f"XP: {self.player.xp}/{self.player.xp_to_next_level}",
            595,
            250
        )

        self.draw_text(
            f"Gold: {self.player.gold}",
            595,
            280
        )

        self.draw_text(
            f"Attack: {self.player.get_attack_damage()}",
            595,
            310
        )

        self.draw_text(
            f"Defense: {self.player.get_damage_reduction()}%",
            595,
            340
        )

        self.draw_text(
            "WASD / arrows: move",
            595,
            385,
            self.small
        )

        # ---------- Bottom log ----------

        self.panel((25, 460, 1050, 215))

        self.draw_text(
            "LOG",
            45,
            480,
            self.font
        )

        y = 515

        for msg in self.messages[-6:]:
            self.draw_text(
                msg,
                45,
                y,
                self.small
            )
            y += 24

        if room.items:
            self.draw_text(
                "E: pick up item",
                750,
                480,
                self.small
            )

        self.draw_text(
            "I: inventory   C: stats   "
            "F5: save   F9: load   T: talk",
            45,
            640,
            self.small
        )

        if self.enemy:
            self.draw_combat()

        if self.overlay == "inventory":
            self.draw_inventory()

        elif self.overlay == "stats":
            self.draw_stats()

    def draw_combat(self):
        self.panel(
            (260, 120, 580, 350),
            (20, 20, 26),
            (175, 175, 185)
        )

        self.draw_text(
            f"ENEMY: {self.enemy.name}",
            300,
            145,
            self.large
        )

        self.bar(
            300,
            200,
            500,
            28,
            self.enemy.health,
            self.enemy.max_health,
            "HP"
        )

        self.draw_text(
            "1 Attack     2 Dodge     3 Escape",
            300,
            260
        )

        self.draw_text(
            "4 Dialogue   5 Ability   6 Potion",
            300,
            300
        )

        self.draw_text(
            "Combat pauses movement until resolved.",
            300,
            365,
            self.small
        )

    def draw_inventory(self):
        self.panel(
            (150, 75, 800, 545),
            (18, 18, 24),
            (170, 170, 180)
        )

        self.draw_text(
            "INVENTORY",
            185,
            105,
            self.title
        )

        if not self.player.inventory:
            self.draw_text(
                "Inventory is empty.",
                190,
                180
            )

        else:
            y = 180

            for i, item in enumerate(
                self.player.inventory[:13],
                1
            ):
                equipped = ""

                if (
                    item is self.player.equipped_weapon
                    or item is self.player.equipped_armor
                    or item is self.player.equipped_shield
                ):
                    equipped = " [EQUIPPED]"

                self.draw_text(
                    f"{i}. {item.name}{equipped}",
                    190,
                    y
                )

                self.draw_text(
                    f"{item.item_type}  "
                    f"power {getattr(item, 'power', 0)}  "
                    f"defense {getattr(item, 'defense', 0)}%",
                    560,
                    y,
                    self.small
                )

                y += 30

        self.draw_text(
            "1-9: equip/use item   ESC / I closes inventory",
            190,
            575,
            self.small
        )

    def draw_stats(self):
        self.panel(
            (250, 95, 600, 500),
            (18, 18, 24),
            (170, 170, 180)
        )

        self.draw_text(
            "CHARACTER",
            285,
            125,
            self.title
        )

        rows = [
            f"Name: {self.player.name}",
            f"Gender: {self.player.gender}",
            f"Race: {self.player.race}",
            f"Class: {self.player.character_class}",
            f"Passive: {self.player.passive}",
            f"Level: {self.player.level}",
            f"Health: {self.player.health}/{self.player.max_health}",
            f"Stamina: {self.player.stamina}/{self.player.max_stamina}",
            f"Magicka: {self.player.magicka}/{self.player.max_magicka}",
            f"Attack: {self.player.get_attack_damage()}",
            f"Defense: {self.player.get_damage_reduction()}%",
            f"Gold: {self.player.gold}",
        ]

        y = 195

        for row in rows:
            self.draw_text(
                row,
                290,
                y
            )
            y += 32

        self.draw_text(
            "ESC / C closes stats",
            290,
            555,
            self.small
        )

    def draw_end(self):
        self.screen.fill((9, 9, 13))

        title = (
            "YOU ESCAPED!"
            if self.state == "won"
            else "YOU DIED"
        )

        self.draw_text(
            title,
            350,
            220,
            self.title
        )

        self.draw_text(
            "Press ENTER to begin a new adventure.",
            350,
            310
        )

    # ---------- Overlay controls ----------

    def handle_inventory_key(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_i):
            self.overlay = None
            return

        if not self.player.inventory:
            return

        # Number keys 1-9 correspond to visible inventory entries.
        number_keys = {
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
            pygame.K_4: 3,
            pygame.K_5: 4,
            pygame.K_6: 5,
            pygame.K_7: 6,
            pygame.K_8: 7,
            pygame.K_9: 8,
        }

        if event.key not in number_keys:
            return

        index = number_keys[event.key]

        if index >= len(self.player.inventory):
            self.message("That inventory slot is empty.")
            return

        item = self.player.inventory[index]

        if item.item_type in ("weapon", "armor", "shield"):
            if self.player.equip_item(item.name):
                self.message(f"Equipped {item.name}.")

        elif item.item_type == "consumable":
            used = self.player.use_item(item.name)

            if used:
                self.message(f"Used {item.name}.")

        else:
            self.message(
                f"{item.name} cannot be equipped or used."
            )

    # ---------- Events / loop ----------

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.state in (
            "name",
            "gender",
            "race",
            "class"
        ):
            self.handle_creation(event)
            return

        if self.state in ("dead", "won"):
            if event.key == pygame.K_RETURN:
                self.__init__()
            return

        # ESC closes overlays first. Only a second ESC quits.
        if event.key == pygame.K_ESCAPE:
            if self.overlay:
                self.overlay = None
            else:
                self.running = False
            return

        if self.overlay == "inventory":
            self.handle_inventory_key(event)
            return

        if self.overlay == "stats":
            if event.key == pygame.K_c:
                self.overlay = None
            return

        if event.key == pygame.K_i:
            self.overlay = "inventory"
            return

        if event.key == pygame.K_c:
            self.overlay = "stats"
            return

        if event.key == pygame.K_F5:
            self.save()
            return

        if event.key == pygame.K_F9:
            self.load()
            return

        if self.enemy:
            actions = {
                pygame.K_1: self.player_attack,
                pygame.K_2: self.dodge,
                pygame.K_3: self.escape,
                pygame.K_4: self.dialogue,
                pygame.K_5: self.use_ability,
                pygame.K_6: self.use_item,
            }

            action = actions.get(event.key)

            if action:
                action()

            return

        directions = {
            pygame.K_w: "north",
            pygame.K_UP: "north",
            pygame.K_s: "south",
            pygame.K_DOWN: "south",
            pygame.K_a: "west",
            pygame.K_LEFT: "west",
            pygame.K_d: "east",
            pygame.K_RIGHT: "east",
        }

        if event.key in directions:
            self.move(directions[event.key])

        elif event.key == pygame.K_e:
            self.take_item()

        elif event.key == pygame.K_t:
            self.talk()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_event(event)

            if self.state in (
                "name",
                "gender",
                "race",
                "class"
            ):
                self.draw_creation()

            elif self.state in ("dead", "won"):
                self.draw_end()

            else:
                self.draw_play()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    PygameGame().run()
