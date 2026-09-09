import random


class Monster:

    def __init__(
        self,
        name,
        health=100,
        attack_damage=10,
        dialogue=None,
        attack_sounds=None,
        reactions=None,
        death_sounds=None,
        dialogue_success_chance=50
    ):
        self.name = name
        self.health = health
        self.max_health = health
        self.stamina = 100
        self.magicka = 100
        self.attack_damage = attack_damage
        self.dialogue_success_chance = dialogue_success_chance

        self.dialogue = dialogue or [
            f"{self.name}: Grrrr...",
            f"{self.name}: Who dares enter my dungeon?",
            f"{self.name}: You should not have come here...",
            f"{self.name}: Leave... while you still can.",
            f"{self.name}: RAAAAAGH!",
            f"{self.name}: Fresh meat!",
            f"{self.name}: You will regret this.",
            f"{self.name}: Intruder!"
        ]

        self.attack_sounds = attack_sounds or [
            f"{self.name}: RAAAH!",
            f"{self.name}: Grrrrr!",
            f"{self.name}: HAAA!",
            f"{self.name}: DIE!",
            f"{self.name}: *roars*"
        ]

        self.reactions = reactions or [
            f"{self.name}: GRAAAH!",
            f"{self.name}: You will pay for that!",
            f"{self.name}: *growls in pain*",
            f"{self.name}: Rrrrr...",
            f"{self.name}: Is that all you've got?"
        ]

        self.death_sounds = death_sounds or [
            f"{self.name}: Noooo...",
            f"{self.name}: *lets out a final roar*",
            f"{self.name}: Grrrr... *falls*",
            f"{self.name}: This... cannot be..."
        ]

    def speak(self):
        print(random.choice(self.dialogue))

    def attack(self):
        print(random.choice(self.attack_sounds))
        print(f"{self.name} attacks!")

        return self.attack_damage

    def take_damage(self, damage):
        self.health -= damage

        if self.health < 0:
            self.health = 0

        if self.health > 0:
            print(random.choice(self.reactions))

        else:
            print(random.choice(self.death_sounds))

    def generate_loot(self):
        """Generate random loot when this monster dies."""

        import random
        from game.item import Item

        loot = []

        loot_tables = {

            "Goblin": [
                ("Rusty Dagger", "A battered dagger.", 15),
                ("Small Pouch of Gold", "A small pouch of stolen coins.", 20),
                ("Old Ring", "A cheap old ring.", 10),
                ("Health Potion", "Restores some health.", 25)
            ],

            "Skeleton": [
                ("Rusty Sword", "An old sword recovered from the dead.", 20),
                ("Ancient Coin", "An old coin found among the bones.", 30),
                ("Bone Charm", "A strange charm made from bone.", 15),
                ("Small Pouch of Gold", "Gold carried by the dead.", 20)
            ],

            "Bandit": [
                ("Iron Dagger", "A well-used bandit's dagger.", 30),
                ("Leather Armor", "Basic leather armor.", 40),
                ("Pouch of Gold", "Gold stolen from travelers.", 50),
                ("Health Potion", "Restores some health.", 25)
            ],

            "Troll": [
                ("Troll Club", "A massive crude club.", 80),
                ("Large Pouch of Gold", "A surprisingly large amount of gold.", 100),
                ("Health Potion", "Restores some health.", 25)
            ],

            "Orc": [
                ("Orc Axe", "A heavy orcish axe.", 100),
                ("Heavy Armor", "Heavy armor taken from an orc warrior.", 120),
                ("Pouch of Gold", "Gold taken from defeated enemies.", 60)
            ],

            "Demon": [
                ("Demon Fang", "A terrifying fang from a demon.", 200),
                ("Dark Crystal", "A strange crystal radiating dark energy.", 300),
                ("Large Pouch of Gold", "Treasure accumulated by the demon.", 150)
            ],

            "Spirit": [
                ("Ghostly Charm", "A strange object that feels unnaturally cold.", 150),
                ("Ancient Coin", "A coin from a forgotten age.", 75)
            ],

            "Vampire": [
                ("Vampire Fang", "A sharp fang from an ancient vampire.", 250),
                ("Blood Ruby", "A dark red gemstone.", 400),
                ("Silver Ring", "An ornate silver ring.", 150),
                ("Pouch of Gold", "Gold accumulated over centuries.", 100)
            ],

            "Dragon": [
                ("Dragon Scale", "A powerful scale from a dragon.", 500),
                ("Dragon Fang", "A massive dragon fang.", 750),
                ("Dragon Treasure", "A piece of treasure from a dragon's hoard.", 1000),
                ("Ancient Gem", "A priceless ancient gemstone.", 800)
            ]
        }

        # 25% chance of dropping nothing
        if random.random() < 0.25:
            return loot

        possible_loot = loot_tables.get(self.name, [])

        if not possible_loot:
            return loot

        # Usually one item, sometimes two
        number_of_items = random.choices(
            [1, 2],
            weights=[80, 20]
        )[0]

        selected = random.sample(
            possible_loot,
            min(number_of_items, len(possible_loot))
        )

        for name, description, value in selected:

            loot.append(
                Item(
                    name,
                    description,
                    value
                )
            )

        return loot

    def is_alive(self):
        return self.health > 0

    def __str__(self):
        return self.name