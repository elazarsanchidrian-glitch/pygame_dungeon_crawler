import random
import pygame

from game.character import CharacterCreation
from game.player import Player
from game.dungeon import Dungeon
from game.save_system import SaveSystem
from game.item import Item
from game.assets import AssetManager


WIDTH, HEIGHT = 1100, 700
FPS = 60


class PygameGame:
    """Graphical front-end for the original dungeon crawler classes."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        pygame.display.set_caption("Cryptfall")
        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )
        self.clock = pygame.time.Clock()

        # -----------------------------------------------------
        # FONTS
        # -----------------------------------------------------

        self.font = pygame.font.Font(None, 25)
        self.small = pygame.font.Font(None, 20)
        self.large = pygame.font.Font(None, 38)
        self.title = pygame.font.Font(None, 58)

        # -----------------------------------------------------
        # ASSETS
        # -----------------------------------------------------

        self.assets = AssetManager()

        self.assets.load_graphics()
        self.assets.load_sounds()

        # -----------------------------------------------------
        # MUSIC
        # -----------------------------------------------------

        music_path = self.assets.sounds_path(
            "music",
            "dungeon_theme.ogg"
        )

        if pygame.mixer.music:

            try:
                pygame.mixer.music.load(
                    music_path
                )

                pygame.mixer.music.set_volume(
                    0.4
                )

                pygame.mixer.music.play(-1)

            except pygame.error as exc:
                print(
                    f"[AUDIO] Could not load "
                    f"dungeon music: {exc}"
                )

        # -----------------------------------------------------
        # GAME STATE
        # -----------------------------------------------------

        self.running = True

        self.state = "name"

        self.name = ""

        self.character = None

        self.player = None

        self.dungeon = None

        self.enemy = None

        self.active_merchant = None
        self.active_npc = None

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

        monster_sound_name = (
            self.enemy.name.lower()
            + "_attack"
        )

        monster_sound = self.assets.get_sound(
            monster_sound_name
        )

        if monster_sound:
            monster_sound.play()
        else:
            self.assets.play_sound(
                "enemy_hit"
            )

        raw_damage = self.enemy.attack()
        damage = self.player.take_damage(raw_damage)

        self.assets.play_sound(
            "player_hurt"
        )

        self.message(
            f"{self.enemy.name} "
            f"hits you for {damage} damage."
        )

        if self.player.health <= 0:
            self.enemy = None
            self.state = "dead"
            self.message(
                "You have been defeated."
            )

    def player_attack(self):
        if not self.enemy or not self.player:
            return

        enemy = self.enemy

        self.assets.play_sound(
            "player_attack"
        )

        base = self.player.get_attack_damage()
        damage = random.randint(
            max(1, base - 5),
            base + 5
        )

        enemy.take_damage(damage)
        monster_name = enemy.name.lower()

        if enemy.is_alive():
            self.assets.play_sound(
                f"{monster_name}_wound"
            )
        else:
            self.assets.play_sound(
                f"{monster_name}_death"
            )

        self.message(
            f"You attack "
            f"{enemy.name} "
            f"for {damage} damage."
        )

        if not enemy.is_alive():
            self.defeat_enemy()
        else:
            self.monster_attack()

    def use_ability(self):
        if not self.enemy or not self.player:
            return

        enemy = self.enemy
        success = self.player.use_ability(enemy)

        if not success:
            return

        monster_name = enemy.name.lower()

        if enemy.is_alive():
            self.assets.play_sound(
                f"{monster_name}_wound"
            )
        else:
            self.assets.play_sound(
                f"{monster_name}_death"
            )

        if not enemy.is_alive():
            self.defeat_enemy()
        else:
            self.monster_attack()

    def dodge(self):
        if not self.enemy:
            return

        if random.random() < 0.50:
            self.assets.play_sound(
                "player_dodge"
            )
            self.message(
                f"You dodge "
                f"{self.enemy.name}'s attack!"
            )
        else:
            self.message(
                "Your dodge fails!"
            )
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

        loot = enemy.generate_loot()

        if loot:
            for item in loot:
                room.add_item(item)
                self.message(f"Dropped: {item.name}")

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

        _, item = consumables[index % len(consumables)]
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

        self.active_npc = npc

        self.message(
            f"{npc.name}: {npc.description}"
        )

        # Merchant
        if hasattr(npc, "stock"):
            self.active_merchant = npc
            self.overlay = "shop"

        # Other NPCs, such as the Lost Traveler
        else:
            self.overlay = "npc"

    def handle_shop_event(self, event):
        if not self.active_merchant:
            self.overlay = None
            return

        if event.key in (pygame.K_ESCAPE, pygame.K_0):
            self.message("Merchant: Safe travels, friend.")
            self.overlay = None
            self.active_merchant = None
            return

        key_mapping = {
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
            pygame.K_4: 3,
            pygame.K_5: 4,
            pygame.K_6: 5,
        }

        if event.key in key_mapping:
            index = key_mapping[event.key]

            if index < len(self.active_merchant.stock):
                item = self.active_merchant.stock[index]

                if self.player.gold < item.value:
                    self.message("Merchant: You don't have enough gold.")
                    return

                self.player.gold -= item.value
                self.player.add_item(item)
                self.active_merchant.stock.pop(index)

                self.message(f"You bought {item.name} for {item.value} gold.")
                self.message(f"Gold remaining: {self.player.gold}")
            else:
                self.message("Merchant: That's not something I have.")

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
                
                if r.npcs:
                    pygame.draw.circle(
                        self.screen,
                        (80, 190, 120),
                        (sx + 20, sy + 20),
                        6
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

        elif self.overlay == "shop":
            self.draw_shop()
        elif self.overlay == "npc":
            self.draw_npc_dialogue()

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

        enemy_image = self.assets.get_image(
            self.enemy.name.lower()
        )

        if enemy_image:
            image_rect = enemy_image.get_rect(
                center=(735, 235)
            )
            self.screen.blit(
                enemy_image,
                image_rect
            )

        self.bar(
            300,
            200,
            300,
            28,
            self.enemy.health,
            self.enemy.max_health,
            "HP"
        )

        self.draw_text(
            "1 Attack     2 Dodge     3 Escape",
            300,
            270
        )

        self.draw_text(
            "4 Dialogue   5 Ability   6 Potion",
            300,
            310
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

    def draw_shop(self):
        self.panel(
            (150, 75, 800, 545),
            (18, 18, 24),
            (170, 170, 180)
        )

        self.draw_text(
            "WANDERING MERCHANT",
            185,
            105,
            self.title
        )

        # Merchant image
        merchant_image = self.assets.get_image(
            "merchant"
        )

        if merchant_image:
            image_rect = merchant_image.get_rect(
                center=(800, 245)
            )

            self.screen.blit(
                merchant_image,
                image_rect
            )

        self.draw_text(
            f"Your Gold: {self.player.gold}",
            185,
            180,
            self.font
        )

        self.draw_text(
            "For sale:",
            185,
            220,
            self.font
        )

        if (
                not self.active_merchant
                or not self.active_merchant.stock
        ):
            self.draw_text(
                "Nothing. The merchant is sold out.",
                185,
                260
            )

        else:
            y = 260

            for i, item in enumerate(
                    self.active_merchant.stock[:6],
                    1
            ):
                self.draw_text(
                    f"{i}. {item.name} - "
                    f"{item.value} gold",
                    185,
                    y,
                    self.small
                )

                y += 35

        self.draw_text(
            "1-6: Buy item   ESC / 0: Leave shop",
            185,
            570,
            self.small
        )


    def draw_npc_dialogue(self):
        self.panel(
            (150, 75, 800, 545),
            (18, 18, 24),
            (170, 170, 180)
        )

        if not self.active_npc:
            return

        self.draw_text(
            self.active_npc.name,
            185,
            110,
            self.title
        )

        # NPC image
        npc_image = None

        if self.active_npc.name.lower() == "lost traveler":
            npc_image = self.assets.get_image(
                "lost_traveler"
            )

        if npc_image:
            image_rect = npc_image.get_rect(
                center=(760, 280)
            )

            self.screen.blit(
                npc_image,
                image_rect
            )

        # NPC description
        description = getattr(
            self.active_npc,
            "description",
            "The traveler remains silent."
        )

        self.draw_text(
            description,
            185,
            210,
            self.small
        )

        self.draw_text(
            "The traveler speaks with you.",
            185,
            300,
            self.font
        )

        self.draw_text(
            "ESC / T: Close dialogue",
            185,
            570,
            self.small
        )

    def draw_stats(self):
        self.panel((250, 95, 600, 500), (18, 18, 24), (170, 170, 180))
        self.draw_text("CHARACTER STATS", 285, 125, self.title)

        stats = [
            f"Name: {self.player.name}",
            f"Race: {self.player.race}",
            f"Gender: {self.player.gender}",
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

        y = 190
        for line in stats:
            self.draw_text(line, 300, y)
            y += 27

        self.draw_text("ESC / C: close", 300, 545, self.small)

    # ---------- Input handling ----------

    def handle_play_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.overlay == "shop":
            self.handle_shop_event(event)
            return
        if self.overlay == "npc":
            if event.key in (
                pygame.K_ESCAPE,
                pygame.K_t
            ):
                self.overlay = None
                self.active_npc = None

            return

        if self.overlay in ("inventory", "stats"):
            if event.key in (pygame.K_ESCAPE, pygame.K_i, pygame.K_c):
                self.overlay = None
                return

            if self.overlay == "inventory" and pygame.K_1 <= event.key <= pygame.K_9:
                index = event.key - pygame.K_1
                if index < len(self.player.inventory):
                    item = self.player.inventory[index]
                    if getattr(item, "item_type", "") == "consumable":
                        self.player.use_item(item.name)
                        self.message(f"Used {item.name}.")
                    elif getattr(item, "item_type", "") in ("weapon", "armor", "shield"):
                        if self.player.equip_item(item.name):
                            self.message(f"Equipped {item.name}.")
                    else:
                        self.message(f"{item.name} cannot be equipped or used.")
                else:
                    self.message("There is no item in that slot.")
            return

        if self.enemy:
            combat_keys = {
                pygame.K_1: self.player_attack,
                pygame.K_2: self.dodge,
                pygame.K_3: self.escape,
                pygame.K_4: self.dialogue,
                pygame.K_5: self.use_ability,
                pygame.K_6: lambda: self.use_item(0),
            }
            action = combat_keys.get(event.key)
            if action:
                action()
            return

        movement = {
            pygame.K_w: "north",
            pygame.K_UP: "north",
            pygame.K_s: "south",
            pygame.K_DOWN: "south",
            pygame.K_a: "west",
            pygame.K_LEFT: "west",
            pygame.K_d: "east",
            pygame.K_RIGHT: "east",
        }

        if event.key in movement:
            self.move(movement[event.key])
        elif event.key == pygame.K_e:
            self.take_item()
        elif event.key == pygame.K_t:
            self.talk()
        elif event.key == pygame.K_i:
            self.overlay = "inventory"
        elif event.key == pygame.K_c:
            self.overlay = "stats"
        elif event.key == pygame.K_F5:
            self.save()
        elif event.key == pygame.K_F9:
            self.load()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if self.state in ("name", "gender", "race", "class"):
            if event.type == pygame.KEYDOWN:
                self.handle_creation(event)
            return

        if self.state == "play":
            self.handle_play_event(event)
            return

        if self.state in ("dead", "won"):
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    self.running = False

    # ---------- Drawing state screens ----------

    def draw_end_screen(self):
        self.screen.fill((10, 10, 14))
        heading = "YOU ESCAPED!" if self.state == "won" else "YOU DIED"
        self.draw_text(heading, 350, 180, self.title)

        y = 290
        for message in self.messages[-5:]:
            self.draw_text(message, 180, y, self.font)
            y += 30
        self.draw_text("Press ENTER or ESC to exit.", 350, 560, self.small)

    def draw(self):
        if self.state in ("name", "gender", "race", "class"):
            self.draw_creation()
        elif self.state == "play":
            self.draw_play()
        elif self.state in ("dead", "won"):
            self.draw_end_screen()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)

            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
