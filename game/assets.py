import os
import pygame


class AssetManager:

    def __init__(self):
        self.graphics = {}
        self.sounds = {}

    def load_image(self, path, size=None):
        image = pygame.image.load(path).convert_alpha()

        if size:
            image = pygame.transform.smoothscale(image, size)

        return image

    def get_image(self, name):
        return self.graphics.get(name)

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

            self.graphics[name] = self.load_image(
                path,
                (160, 160)
            )