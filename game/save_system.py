import json


class SaveSystem:

    SAVE_FILE = "savegame.json"

    @staticmethod
    def save(game):

        data = {
            "player": {
                "name": game.player.name,
                "gender": game.player.gender,
                "race": game.player.race,
                "character_class": game.player.character_class,
                "passive": game.player.passive,

                "health": game.player.health,
                "max_health": game.player.max_health,
                "stamina": game.player.stamina,
                "magicka": game.player.magicka,
                "gold": game.player.gold,
                "level": game.player.level,
                "xp": game.player.xp,
                "xp_to_next_level": game.player.xp_to_next_level,
                "equipped_weapon": game.player.equipped_weapon.name if game.player.equipped_weapon else None,
                "equipped_armor": game.player.equipped_armor.name if game.player.equipped_armor else None,
                "equipped_shield": game.player.equipped_shield.name if game.player.equipped_shield else None,

                "inventory": [
                    {
                        "name": item.name,
                        "description": item.description,
                        "value": item.value,
                        "item_type": item.item_type,
                        "power": item.power,
                        "defense": item.defense
                    }
                    for item in game.player.inventory
                ]
            },

            "dungeon": {
                "current_x": game.dungeon.current_x,
                "current_y": game.dungeon.current_y,
                "exit_x": game.dungeon.exit_x,
                "exit_y": game.dungeon.exit_y
            }
        }

        with open(SaveSystem.SAVE_FILE, "w") as file:
            json.dump(data, file, indent=4)

        print("\nGame saved successfully!")

    @staticmethod
    def load():

        try:
            with open(SaveSystem.SAVE_FILE, "r") as file:
                return json.load(file)

        except FileNotFoundError:

            print("\nNo save file found.")

            return None

        except json.JSONDecodeError:

            print("\nSave file is corrupted.")

            return None