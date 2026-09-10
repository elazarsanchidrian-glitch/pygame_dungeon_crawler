import json
from pathlib import Path


class SaveSystem:

    SAVE_FILE = "savegame.json"

    @staticmethod
    def save(game):

        player = game.player
        dungeon = game.dungeon

        inventory = []

        for item in player.inventory:
            inventory.append({
                "name": getattr(item, "name", "Unknown Item"),
                "description": getattr(item, "description", ""),
                "value": getattr(item, "value", 0),
                "item_type": getattr(item, "item_type", "misc"),
                "power": getattr(item, "power", 0),
                "defense": getattr(item, "defense", 0)
            })

        equipped_weapon = (
            player.equipped_weapon.name
            if player.equipped_weapon else None
        )

        equipped_armor = (
            player.equipped_armor.name
            if player.equipped_armor else None
        )

        equipped_shield = (
            player.equipped_shield.name
            if player.equipped_shield else None
        )

        player_data = {
            "name": player.name,
            "gender": player.gender,
            "race": player.race,
            "character_class": player.character_class,
            "passive": player.passive,

            "health": player.health,
            "max_health": player.max_health,
            "stamina": player.stamina,
            "max_stamina": getattr(player, "max_stamina", 100),
            "magicka": player.magicka,
            "max_magicka": getattr(player, "max_magicka", 100),

            "gold": player.gold,

            "level": player.level,
            "xp": player.xp,
            "xp_to_next_level": player.xp_to_next_level,

            "equipped_weapon": equipped_weapon,
            "equipped_armor": equipped_armor,
            "equipped_shield": equipped_shield,

            "inventory": inventory
        }

        dungeon_data = {
            "current_x": dungeon.current_x,
            "current_y": dungeon.current_y,
            "exit_x": dungeon.exit_x,
            "exit_y": dungeon.exit_y,
            "exit_min_distance": getattr(dungeon, "exit_min_distance", 5),
            "exit_max_distance": getattr(dungeon, "exit_max_distance", 12),
            "special_room_chance": getattr(dungeon, "special_room_chance", 0.03),
            "boss_spawn_chance": getattr(dungeon, "boss_spawn_chance", 0.25),
            "boss_key_drop_chance": getattr(dungeon, "boss_key_drop_chance", 0.50),
            "rooms": []
        }

        for coordinates, room in dungeon.rooms.items():

            x, y = coordinates

            room_data = {
                "x": x,
                "y": y,
                "name": getattr(room, "name", "Unknown Room"),
                "description": getattr(room, "description", ""),
                "is_exit": getattr(room, "is_exit", False),
                "is_boss_room": getattr(room, "is_boss_room", False),
                "visited": getattr(room, "visited", False),
                "items": [],
                "monsters": [],
                "npcs": []
            }

            for item in getattr(room, "items", []):
                room_data["items"].append({
                    "name": getattr(item, "name", "Unknown Item"),
                    "description": getattr(item, "description", ""),
                    "value": getattr(item, "value", 0),
                    "item_type": getattr(item, "item_type", "misc"),
                    "power": getattr(item, "power", 0),
                    "defense": getattr(item, "defense", 0)
                })

            for monster in getattr(room, "monsters", []):
                room_data["monsters"].append({
                    "name": getattr(monster, "name", "Unknown Monster"),
                    "health": getattr(monster, "health", 0),
                    "max_health": getattr(
                        monster,
                        "max_health",
                        getattr(monster, "health", 0)
                    ),
                    "attack_power": getattr(monster, "attack_power", 0),
                    "is_dungeon_boss": getattr(
                        monster,
                        "is_dungeon_boss",
                        False
                    ),
                    "defeated": getattr(monster, "health", 0) <= 0
                })

            for npc in getattr(room, "npcs", []):
                npc_data = {
                    "name": getattr(
                        npc,
                        "name",
                        npc.__class__.__name__
                    ),
                    "class_name": npc.__class__.__name__,
                    "dialogue": getattr(npc, "dialogue", None)
                }

                if hasattr(npc, "traded"):
                    npc_data["traded"] = npc.traded

                if hasattr(npc, "talked"):
                    npc_data["talked"] = npc.talked

                room_data["npcs"].append(npc_data)

            dungeon_data["rooms"].append(room_data)

        data = {
            "save_version": 2,
            "player": player_data,
            "dungeon": dungeon_data
        }

        save_path = Path(SaveSystem.SAVE_FILE)

        try:
            with save_path.open("w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            print("\nGame saved successfully!")
            return True

        except OSError as error:
            print(f"\nCould not save the game: {error}")
            return False

    @staticmethod
    def load():

        save_path = Path(SaveSystem.SAVE_FILE)

        try:
            with save_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                print("\nSave file is invalid.")
                return None

            if "player" not in data:
                print("\nSave file is missing player data.")
                return None

            if "dungeon" not in data:
                print("\nSave file is missing dungeon data.")
                return None

            player_data = data["player"]
            dungeon_data = data["dungeon"]

            if "max_stamina" not in player_data:
                player_data["max_stamina"] = max(
                    100,
                    player_data.get("stamina", 100)
                )

            if "max_magicka" not in player_data:
                player_data["max_magicka"] = max(
                    100,
                    player_data.get("magicka", 100)
                )

            if "max_health" not in player_data:
                player_data["max_health"] = max(
                    100,
                    player_data.get("health", 100)
                )

            if "xp_to_next_level" not in player_data:
                player_data["xp_to_next_level"] = 100

            if "inventory" not in player_data:
                player_data["inventory"] = []

            if "rooms" not in dungeon_data:
                dungeon_data["rooms"] = []

            player_data["health"] = min(
                max(0, player_data.get("health", 100)),
                player_data["max_health"]
            )

            player_data["stamina"] = min(
                max(0, player_data.get("stamina", 100)),
                player_data["max_stamina"]
            )

            player_data["magicka"] = min(
                max(0, player_data.get("magicka", 100)),
                player_data["max_magicka"]
            )

            player_data["gold"] = max(
                0,
                player_data.get("gold", 0)
            )

            player_data["level"] = max(
                1,
                player_data.get("level", 1)
            )

            player_data["xp"] = max(
                0,
                player_data.get("xp", 0)
            )

            print("\nGame loaded successfully!")
            return data

        except FileNotFoundError:
            print("\nNo save file found.")
            return None

        except json.JSONDecodeError:
            print("\nSave file is corrupted.")
            return None

        except OSError as error:
            print(f"\nCould not load the save file: {error}")
            return None

    @staticmethod
    def save_exists():
        return Path(SaveSystem.SAVE_FILE).exists()

    @staticmethod
    def delete_save():

        save_path = Path(SaveSystem.SAVE_FILE)

        try:
            if save_path.exists():
                save_path.unlink()
                print("\nSave file deleted.")
                return True

            print("\nNo save file to delete.")
            return False

        except OSError as error:
            print(f"\nCould not delete save file: {error}")
            return False
