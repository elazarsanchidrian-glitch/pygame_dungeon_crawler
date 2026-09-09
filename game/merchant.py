from game.npc import NPC
from game.item import Item


class Merchant(NPC):
    def __init__(self):
        super().__init__(
            "Wandering Merchant",
            "A strange merchant carrying a heavy pack of supplies."
        )

        self.stock = [
            Item("Health Potion", "Restores a little health.", 25),
            Item(
                "Rusty Sword",
                "An old sword. Better than fighting with your fists.",
                10
            ),
            Item(
                "Leather Armor",
                "Simple armor that offers basic protection.",
                20
            )
        ]

    def talk(self, player=None):
        print("\nWandering Merchant: Welcome, traveler!")
        print("Wandering Merchant: Care to see my wares?")

        if player:
            self.shop(player)

    def shop(self, player):
        while True:
            print("\n" + "=" * 40)
            print(" WANDERING MERCHANT")
            print("=" * 40)

            print(f"\nYour gold: {player.gold}")

            print("\nFor sale:")

            if not self.stock:
                print(" - Nothing. The merchant is sold out.")
            else:
                for i, item in enumerate(self.stock, 1):
                    print(f"{i}. {item.name} - {item.value} gold")

            print("\n0. Leave shop")

            choice = input("\nBuy which item? ").strip()

            if choice == "0":
                print("Merchant: Safe travels, friend.")
                break

            if not choice.isdigit():
                print("Merchant: I don't understand.")
                continue

            choice = int(choice)

            if choice < 1 or choice > len(self.stock):
                print("Merchant: That's not something I have.")
                continue

            item = self.stock[choice - 1]

            if player.gold < item.value:
                print("Merchant: You don't have enough gold.")
                continue

            player.gold -= item.value
            player.add_item(item)
            self.stock.remove(item)

            print(f"\nYou bought {item.name} for {item.value} gold.")
            print(f"Gold remaining: {player.gold}")
