from game.item import Item
from game.npc import NPC


class Merchant(NPC):
    """Merchant NPC that sells each stock item once."""

    def __init__(self):
        super().__init__(
            "Wandering Merchant",
            "A strange merchant carrying a heavy pack of supplies.",
        )

        self.stock = [
            Item("Health Potion", "Restores a little health.", 25),
            Item(
                "Rusty Sword",
                "An old sword. Better than fighting with your fists.",
                10,
            ),
            Item(
                "Leather Armor",
                "Simple armor that offers basic protection.",
                20,
            ),
        ]

    def talk(self, player=None):
        print("\nWandering Merchant: Welcome, traveler!")
        print("Wandering Merchant: Care to see my wares?")

        if player is not None:
            self.shop(player)
        else:
            print("Merchant: I need to speak with the player directly.")

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
                for index, item in enumerate(self.stock, start=1):
                    print(
                        f"{index}. {item.name} ({item.description}) "
                        f"- {item.value} gold"
                    )

            print("\n0. Leave shop")
            choice = input("\nBuy which item (enter number)? ").strip()

            if choice == "0":
                print("Merchant: Safe travels, friend.")
                break

            if not choice.isdigit():
                print("Merchant: I don't understand.")
                continue

            choice_index = int(choice)

            if choice_index < 1 or choice_index > len(self.stock):
                print("Merchant: That's not something I have.")
                continue

            item = self.stock[choice_index - 1]

            if player.gold < item.value:
                print("Merchant: You don't have enough gold.")
                continue

            if not hasattr(player, "add_item"):
                print("Merchant: You cannot carry items right now.")
                continue

            player.gold -= item.value
            player.add_item(item)
            self.stock.pop(choice_index - 1)

            print(f"\n[Success] You bought {item.name} for {item.value} gold.")
            print(f"Gold remaining: {player.gold}")
