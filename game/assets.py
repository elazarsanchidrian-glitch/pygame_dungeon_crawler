import os
import pygame


class AssetManager:


    def play_sound(self, name):
        sound = self.sounds.get(name)

        if sound is None:
            return

        try:
            pygame.mixer.Sound(sound).play()
        except pygame.error:
            print(f"Could not play sound: {sound}")



    def sounds_path(self, *parts):
        return os.path.join(
            "assets",
            "sounds",
            *parts
        )

    def __init__(self):
        self.graphics = {}
        self.sounds = {}

    def load_image(self, path, size=None):
        print(f"Loading image: {path}")
        image = pygame.image.load(path).convert_alpha()

        if size:
            image = pygame.transform.smoothscale(image, size)

        return image

    def get_image(self, name):
        return self.graphics.get(name)



    def get_sound(self, name):
        return self.sounds.get(name)



    def load_graphics(self):

        base = os.path.join(
            "assets",
            "graphics"
        )

        # ---------- Monsters ----------

        monster_images = {
            "goblin": "goblin.png",
            "skeleton": "skeleton.png",
            "bandit": "bandit.png",
            "troll": "troll.png",
            "orc": "orc.png",
            "demon": "demon.png",
            "spirit": "spirit.png",
            "vampire": "vampire.png",
            "dragon": "dragon.png",
            "dungeon warden": "dungeon_warden.png",
        }

        for name, filename in monster_images.items():

            path = os.path.join(
                base,
                "monsters",
                filename
            )

            self.graphics[name] = self.load_image(
                path,
                (180, 180)
            )

        # ---------- Player ----------
        # Player artwork is optional until the PNGs are added.

        player_images = {
            "warrior": "warrior.png",
            "mage": "mage.png",
            "rogue": "rogue.png",
        }

        for name, filename in player_images.items():

            path = os.path.join(
                base,
                "player",
                filename
            )

            if os.path.exists(path):
                try:
                    self.graphics[name] = self.load_image(
                        path,
                        (160, 160)
                    )
                except pygame.error:
                    print(f"Invalid player image, skipping: {path}")
            else:
                print(f"Player image not found, skipping: {path}")

    def load_sounds(self):

        base = os.path.join(
            "assets",
            "sounds"
        )

        # ---------- Dungeon Music ----------

        music_path = os.path.join(
            base,
            "music",
            "dungeon_theme.ogg"
        )

        if os.path.exists(music_path):
            self.sounds["dungeon_theme"] = music_path
            print(f"Sound found: {music_path}")
        else:
            print(f"Dungeon music not found, skipping: {music_path}")

