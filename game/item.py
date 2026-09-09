class Item:

    def __init__(self, name, description, value=0, item_type="misc", power=0, defense=0):
        self.name = name
        self.description = description
        self.value = value
        inferred = self._infer_type(name)
        self.item_type = inferred if item_type == "misc" else item_type
        self.power = power
        self.defense = defense

    @staticmethod
    def _infer_type(name):
        lowered = name.lower()
        if "potion" in lowered or "scroll" in lowered:
            return "consumable"
        if any(word in lowered for word in ("sword", "dagger", "axe", "staff", "knife", "fang", "club")):
            return "weapon"
        if "shield" in lowered:
            return "shield"
        if any(word in lowered for word in ("armor", "armour", "mail", "robes")):
            return "armor"
        return "misc"

    def inspect(self):
        print(f"\n{self.name}")
        print(self.description)
        if self.value > 0:
            print(f"Value: {self.value} gold")
        if self.item_type == "weapon":
            print(f"Attack bonus: +{self.power}")
        elif self.item_type == "armor":
            print(f"Damage reduction: {self.defense}%")
        elif self.item_type == "shield":
            print(f"Damage reduction: {self.defense}%")
        elif self.item_type == "consumable" and self.power:
            print(f"Effect: +{self.power}")

    def __str__(self):
        return self.name
