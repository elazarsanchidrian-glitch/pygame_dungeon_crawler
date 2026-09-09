import random


class Player:

    def __init__(self, name):

        self.name = name
        self.gender = None

        self.health = 100
        self.max_health = 100

        self.stamina = 100
        self.magicka = 100

        self.race = None
        self.character_class = None
        self.passive = None

        self.inventory = []

        self.gold = 0

        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100

        self.equipped_weapon = None
        self.equipped_armor = None
        self.equipped_shield = None

        self.current_room = None

    # -------------------------
    # CLASS STARTING INVENTORY
    # -------------------------

    def setup_starting_inventory(self):

        from game.item import Item

        # Clear inventory first
        self.inventory = []

        # -------------------------
        # WARRIOR
        # -------------------------

        if self.character_class == "Warrior":

            self.add_item(
                Item(
                    "Iron Sword",
                    "A sturdy sword made for close combat.",
                    50,
                    "weapon",
                    10
                )
            )

            self.add_item(
                Item(
                    "Wooden Shield",
                    "A simple shield that offers basic protection.",
                    30,
                    "shield",
                    0,
                    10
                )
            )

            self.add_item(
                Item(
                    "Chainmail",
                    "Basic metal armor offering decent protection.",
                    75,
                    "armor",
                    0,
                    15
                )
            )

            self.add_item(
                Item(
                    "Health Potion",
                    "Restores some health.",
                    25,
                    "consumable",
                    40
                )
            )

            self.add_item(
                Item(
                    "Health Potion",
                    "Restores some health.",
                    25,
                    "consumable",
                    40
                )
            )

        # -------------------------
        # MAGE
        # -------------------------

        elif self.character_class == "Mage":

            self.add_item(
                Item(
                    "Apprentice Staff",
                    "A wooden staff used to channel magical energy.",
                    50,
                    "weapon",
                    6
                )
            )

            self.add_item(
                Item(
                    "Mage Robes",
                    "Light robes designed for spellcasters.",
                    60,
                    "armor",
                    0,
                    5
                )
            )

            self.add_item(
                Item(
                    "Spellbook",
                    "A book containing the mage's magical knowledge.",
                    100
                )
            )

            self.add_item(
                Item(
                    "Mana Potion",
                    "Restores some magicka.",
                    30
                )
            )

            self.add_item(
                Item(
                    "Mana Potion",
                    "Restores some magicka.",
                    30
                )
            )

        # -------------------------
        # ROGUE
        # -------------------------

        elif self.character_class == "Rogue":

            self.add_item(
                Item(
                    "Iron Dagger",
                    "A quick and lightweight dagger.",
                    35,
                    "weapon",
                    7
                )
            )

            self.add_item(
                Item(
                    "Throwing Knife",
                    "A small knife designed to be thrown.",
                    25,
                    "weapon",
                    4
                )
            )

            self.add_item(
                Item(
                    "Leather Armor",
                    "Light armor that allows freedom of movement.",
                    40,
                    "armor",
                    0,
                    8
                )
            )

            self.add_item(
                Item(
                    "Lockpicks",
                    "A set of tools used to open locked containers.",
                    20
                )
            )

            self.add_item(
                Item(
                    "Health Potion",
                    "Restores some health.",
                    25,
                    "consumable",
                    40
                )
            )

        # -------------------------
        # DEFAULT
        # -------------------------

        else:

            self.add_item(
                Item(
                    "Simple Dagger",
                    "A basic weapon.",
                    15,
                    "weapon",
                    3
                )
            )

            self.add_item(
                Item(
                    "Health Potion",
                    "Restores some health.",
                    25,
                    "consumable",
                    40
                )
            )

    # -------------------------
    # AUTO EQUIP STARTING GEAR
    # -------------------------

    def auto_equip_starting_gear(self):
        for item in self.inventory:
            if item.item_type == "weapon" and self.equipped_weapon is None:
                self.equipped_weapon = item
            elif item.item_type == "armor" and self.equipped_armor is None:
                self.equipped_armor = item
            elif item.item_type == "shield" and self.equipped_shield is None:
                self.equipped_shield = item

    # -------------------------
    # MOVEMENT
    # -------------------------

    def move(self, room):

        self.current_room = room

    # -------------------------
    # ATTACK DAMAGE
    # -------------------------

    def get_attack_damage(self):
        if self.character_class == "Warrior":
            damage = 30
        elif self.character_class == "Mage":
            damage = 25
        elif self.character_class == "Rogue":
            damage = 28
        else:
            damage = 20

        if self.passive == "Brutal":
            damage = int(damage * 1.15)
        elif self.passive == "Arcane Affinity":
            damage = int(damage * 1.10)

        if self.equipped_weapon:
            damage += self.equipped_weapon.power

        return damage

    # -------------------------
    # EQUIPMENT
    # -------------------------

    def equip_item(self, item_name):
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if item is None:
            print("That item is not in your inventory.")
            return False

        if item.item_type == "weapon":
            self.equipped_weapon = item
        elif item.item_type == "armor":
            self.equipped_armor = item
        elif item.item_type == "shield":
            self.equipped_shield = item
        else:
            print("You cannot equip that item.")
            return False

        print(f"You equipped {item.name}.")
        return True

    def get_damage_reduction(self):
        reduction = 0
        if self.equipped_armor:
            reduction += self.equipped_armor.defense
        if self.equipped_shield:
            reduction += self.equipped_shield.defense
        return min(reduction, 50)

    # -------------------------
    # CONSUMABLES
    # -------------------------

    def use_item(self, item_name):
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if item is None:
            print("That item is not in your inventory.")
            return False

        if item.item_type != "consumable":
            print("That item cannot be used.")
            return False

        if "health" in item.name.lower():
            old = self.health
            self.health = min(self.max_health, self.health + item.power)
            restored = self.health - old
            print(f"You use {item.name} and restore {restored} health.")
        elif "mana" in item.name.lower():
            old = self.magicka
            self.magicka = min(100 + self.max_health // 2, self.magicka + item.power)
            restored = self.magicka - old
            print(f"You use {item.name} and restore {restored} magicka.")
        else:
            print("Nothing happens.")
            return False

        self.inventory.remove(item)
        return True

    # -------------------------
    # EXPERIENCE / LEVELS
    # -------------------------

    def gain_xp(self, amount):
        self.xp += amount
        print(f"You gain {amount} XP.")

        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = int(self.xp_to_next_level * 1.35)
            self.max_health += 20
            self.health = self.max_health
            self.stamina += 10
            self.magicka += 10
            print(f"\n*** LEVEL UP! You are now level {self.level}! ***")
            print("Your maximum health increases by 20.")

    # -------------------------
    # CLASS ABILITIES
    # -------------------------

    def use_ability(self, monster):
        if self.character_class == "Warrior":
            cost = 20
            if self.stamina < cost:
                print("Not enough stamina for Power Strike.")
                return False
            self.stamina -= cost
            damage = int(self.get_attack_damage() * 1.8)
            ability_name = "Power Strike"

        elif self.character_class == "Mage":
            cost = 30
            if self.magicka < cost:
                print("Not enough magicka for Fireball.")
                return False
            self.magicka -= cost
            damage = int(self.get_attack_damage() * 1.7)
            ability_name = "Fireball"

        elif self.character_class == "Rogue":
            cost = 25
            if self.stamina < cost:
                print("Not enough stamina for Backstab.")
                return False
            self.stamina -= cost
            damage = int(self.get_attack_damage() * 2.0)
            if random.random() < 0.25:
                damage *= 2
                print("Critical Backstab!")
            ability_name = "Backstab"

        else:
            print("Your character has no special ability.")
            return False

        print(f"{self.name} uses {ability_name} on {monster.name} for {damage} damage!")
        monster.take_damage(damage)
        return True

    # -------------------------
    # TAKE DAMAGE
    # -------------------------

    def take_damage(self, damage):

        # Dwarf Tough passive
        if self.passive == "Tough":

            reduced_damage = int(damage * 0.90)

            print(
                f"{self.name}'s Tough passive reduces "
                f"the damage from {damage} to "
                f"{reduced_damage}!"
            )

            damage = reduced_damage

        reduction = self.get_damage_reduction()
        if reduction:
            reduced_damage = max(1, int(damage * (1 - reduction / 100)))
            print(f"Equipment reduces damage from {damage} to {reduced_damage}.")
            damage = reduced_damage

        self.health -= damage

        if self.health < 0:

            self.health = 0

    # -------------------------
    # INVENTORY
    # -------------------------

    def add_item(self, item):

        self.inventory.append(item)

    def show_inventory(self):

        if not self.inventory:

            print("\nInventory is empty.")

            return

        print("\n" + "=" * 40)
        print(" INVENTORY")
        print("=" * 40)

        # -------------------------
        # EQUIPMENT
        # -------------------------

        equipment = []

        equipment_keywords = [
            "sword",
            "axe",
            "dagger",
            "staff",
            "shield",
            "armor",
            "robes",
            "throwing knife"
        ]

        for item in self.inventory:

            if item.item_type in ("weapon", "armor", "shield") or any(
                keyword in item.name.lower()
                for keyword in equipment_keywords
            ):

                equipment.append(item)

        if equipment:

            print("\nEquipment:")

            for item in equipment:

                print(
                    f" - {item.name}"
                )

        # -------------------------
        # CONSUMABLES
        # -------------------------

        consumables = []

        for item in self.inventory:

            if (
                "potion" in item.name.lower()
                or "scroll" in item.name.lower()
            ):

                consumables.append(item)

        if consumables:

            print("\nConsumables:")

            for item in consumables:

                print(
                    f" - {item.name}"
                )

        # -------------------------
        # MISCELLANEOUS
        # -------------------------

        miscellaneous = []

        for item in self.inventory:

            if (
                item not in equipment
                and item not in consumables
            ):

                miscellaneous.append(item)

        if miscellaneous:

            print("\nMiscellaneous:")

            for item in miscellaneous:

                print(
                    f" - {item.name}"
                )

        print("\n" + "=" * 40)