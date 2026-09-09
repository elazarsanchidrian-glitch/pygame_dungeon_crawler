class CharacterCreation:

    def __init__(self, name):
        self.name = name

        self.gender = None
        self.race = None
        self.character_class = None
        self.passive = None

        self.health = 100
        self.stamina = 100
        self.magicka = 100

    def choose_gender(self):
        print("\nChoose your gender:")
        print("1. Male")
        print("2. Female")

        choice = input("Choice: ")

        if choice == "1":
            self.gender = "Male"

        elif choice == "2":
            self.gender = "Female"

        else:
            print("Invalid choice. Male selected.")
            self.gender = "Male"

    def choose_race(self):
        print("\nChoose your race:")
        print("1. Human")
        print("2. Elf")
        print("3. Dwarf")
        print("4. Orc")
        print("5. Halfling")

        choice = input("Choice: ")

        if choice == "1":
            self.race = "Human"
            self.passive = "Adaptable"

            self.health += 5
            self.stamina += 5
            self.magicka += 5

        elif choice == "2":
            self.race = "Elf"
            self.passive = "Arcane Affinity"

            self.stamina += 10
            self.magicka += 20

        elif choice == "3":
            self.race = "Dwarf"
            self.passive = "Tough"

            self.health += 30

        elif choice == "4":
            self.race = "Orc"
            self.passive = "Brutal"

            self.health += 25
            self.stamina += 20

        elif choice == "5":
            self.race = "Halfling"
            self.passive = "Lucky"

            self.stamina += 25

        else:
            print("Invalid choice. Human selected.")

            self.race = "Human"
            self.passive = "Adaptable"

            self.health += 5
            self.stamina += 5
            self.magicka += 5

    def choose_class(self):
        print("\nChoose your class:")
        print("1. Warrior")
        print("2. Mage")
        print("3. Rogue")

        choice = input("Choice: ")

        if choice == "1":
            self.character_class = "Warrior"

            self.health += 150
            self.stamina += 120
            self.magicka += 50

        elif choice == "2":
            self.character_class = "Mage"

            self.health += 80
            self.stamina += 80
            self.magicka += 150

        elif choice == "3":
            self.character_class = "Rogue"

            self.health += 100
            self.stamina += 150
            self.magicka += 75

        else:
            print("Invalid choice. Warrior selected.")

            self.character_class = "Warrior"

            self.health += 150
            self.stamina += 120
            self.magicka += 50

    def show_character(self):
        print("\n===== CHARACTER CREATED =====")
        print(f"Name: {self.name}")
        print(f"Gender: {self.gender}")
        print(f"Race: {self.race}")
        print(f"Class: {self.character_class}")
        print(f"Passive: {self.passive}")
        print(f"Health: {self.health}")
        print(f"Stamina: {self.stamina}")
        print(f"Magicka: {self.magicka}")