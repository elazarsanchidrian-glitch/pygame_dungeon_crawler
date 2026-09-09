class ConsoleUI:

    # -------------------------
    # WELCOME
    # -------------------------

    def show_welcome(self):

        print("=" * 40)

        print(" Welcome to the Dungeon Game!")

        print("=" * 40)

    def get_player_name(self):

        return input("Enter your name: ")

    # -------------------------
    # MAIN MENU
    # -------------------------

    def show_menu(self):

        print("\nMain Menu")

        print("1. Start Game")

        print("2. Show Stats")

        print("3. Inventory")

        print("4. Quit")

    def get_menu_choice(self):

        return input("Choose an option: ")

    # -------------------------
    # ROOM
    # -------------------------

    def show_room(self, room):

        room.display()

    # -------------------------
    # COMMANDS
    # -------------------------

    def show_commands(self):

        print("\nCommands:")

        print("north")
        print("south")
        print("east")
        print("west")

        print("take <item>")
        print("use <item>")
        print("equip <item>")
        print("inspect <item>")

        print("attack")

        print("inventory")
        print("stats")
        print("save")
        print("load")
        print("quit")

    def get_command(self):

        return input("> ").lower().strip()

    # -------------------------
    # DIRECTIONS
    # -------------------------

    def get_direction(self, exits):

        print(
            f"Available directions: "
            f"{', '.join(exits)}"
        )

        return input(
            "Which direction? "
        ).lower().strip()

    # -------------------------
    # MESSAGES
    # -------------------------

    def show_message(self, message):

        print(message)

    def show_error(self, message):

        print(f"\n[ERROR] {message}")

    # -------------------------
    # INVENTORY
    # -------------------------

    def show_inventory(self, player):

        player.show_inventory()

    # -------------------------
    # PLAYER STATS
    # -------------------------

    def show_player_stats(self, player):

        print("\nPlayer Stats")

        print(f"Name: {player.name}")
        print(f"Gender: {player.gender}")
        print(f"Race: {player.race}")
        print(f"Class: {player.character_class}")
        print(f"Passive: {player.passive}")

        print(f"Health: {player.health}/{player.max_health}")
        print(f"Stamina: {player.stamina}")
        print(f"Magicka: {player.magicka}")

        print(f"Gold: {player.gold}")
        print(f"Level: {player.level}")
        print(f"XP: {player.xp}/{player.xp_to_next_level}")
        print(f"Weapon: {player.equipped_weapon.name if player.equipped_weapon else 'None'}")
        print(f"Armor: {player.equipped_armor.name if player.equipped_armor else 'None'}")
        print(f"Shield: {player.equipped_shield.name if player.equipped_shield else 'None'}")

    # -------------------------
    # COMBAT
    # -------------------------

    def show_combat_start(self, monster):

        print(
            f"\nA {monster.name} appears!"
        )

    def show_combat_options(self):

        print("\nWhat do you do?")
        print("1. Attack")
        print("2. Dodge")
        print("3. Escape")
        print("4. Dialogue")
        print("5. Ability")
        print("6. Use Item")

    def get_combat_choice(self):

        return input("> ").lower().strip()

    def show_attack(
            self,
            attacker,
            defender,
            damage
    ):

        print(
            f"{attacker.name} attacks "
            f"{defender.name} "
            f"for {damage} damage!"
        )

    def show_monster_defeated(self, monster):

        print(
            f"{monster.name} has been defeated!"
        )

    def show_player_defeated(self):

        print("Game Over!")
    # -------------------------
    # ITEMS
    # -------------------------

    def show_items_found(self, items):

        if items:

            print("\nItems found:")

            for item in items:

                print(f"- {item}")

        else:

            print("No items found.")

    def confirm_pickup(self, item):

        choice = input(
            f"Pick up {item}? (y/n): "
        )

        return choice.lower() == "y"

    # -------------------------
    # VICTORY
    # -------------------------

    def show_victory(self):

        print(
            "Congratulations! "
            "You escaped the dungeon!"
        )

    # -------------------------
    # EXIT
    # -------------------------

    def confirm_exit(self):

        choice = input(
            "Are you sure you want to quit? (y/n): "
        )

        return choice.lower() == "y"