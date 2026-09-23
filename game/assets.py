import os
import pygame


class AssetManager:

    def __init__(self):
        self.graphics = {}
        self.sounds = {}

    def sounds_path(self, *parts):
        return os.path.join(
            "assets",
            "sounds",
            *parts
        )

    def load_image(self, path, size=None):
        print(f"Loading image: {path}")

        image = pygame.image.load(path).convert_alpha()

        if size:
            image = pygame.transform.smoothscale(
                image,
                size
            )

        return image

    def get_image(self, name):
        return self.graphics.get(name)

    def get_sound(self, name):
        return self.sounds.get(name)

    # ---------- Sound & Music Methods ----------

    def play_sound(self, name):
        """Play a short sound effect."""

        sound = self.sounds.get(name)

        if sound is None:
            return

        # If a music path is passed accidentally
        if isinstance(sound, str):
            self.play_music(name)
            return

        try:
            sound.play()
        except pygame.error:
            print(f"Could not play sound: {name}")

    def play_music(self, name):
        """Load and loop background music."""

        path = self.sounds.get(name)

        if path and isinstance(path, str):
            if os.path.exists(path):
                try:
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play(-1)

                except pygame.error:
                    print(
                        f"Could not play music track: {name}"
                    )

    def stop_music(self):
        """Stop background music."""

        pygame.mixer.music.stop()

    # ---------- Asset Loading ----------

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

            if os.path.exists(path):

                try:
                    self.graphics[name] = self.load_image(
                        path,
                        (180, 180)
                    )

                except pygame.error:
                    print(
                        f"Invalid monster image, "
                        f"skipping: {path}"
                    )

            else:
                print(
                    f"Monster image not found, "
                    f"skipping: {path}"
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

            if os.path.exists(path):

                try:
                    self.graphics[name] = self.load_image(
                        path,
                        (160, 160)
                    )

                except pygame.error:
                    print(
                        f"Invalid player image, "
                        f"skipping: {path}"
                    )

            else:
                print(
                    f"Player image not found, "
                    f"skipping: {path}"
                )

        # ---------- NPCs ----------

        npc_images = {
            "lost_traveler": "lost_traveler.png",
            "merchant": "merchant.png",
        }

        for name, filename in npc_images.items():

            path = os.path.join(
                base,
                "npcs",
                filename
            )

            if os.path.exists(path):

                try:
                    self.graphics[name] = self.load_image(
                        path,
                        (220, 220)
                    )

                    print(
                        f"Loaded NPC image: {path}"
                    )

                except pygame.error:
                    print(
                        f"Invalid NPC image, "
                        f"skipping: {path}"
                    )

            else:
                print(
                    f"NPC image not found, "
                    f"skipping: {path}"
                )

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

            print(
                f"Music path stored: {music_path}"
            )

        else:
            print(
                f"Dungeon music not found, "
                f"skipping: {music_path}"
            )

        # ---------- Monster Sounds ----------

        monsters = [
            "bandit",
            "demon",
            "dragon",
            "goblin",
            "orc",
            "skeleton",
            "spirit",
            "troll",
            "vampire",
        ]

        for monster in monsters:

            for sound_type in (
                "attack",
                "wound",
                "death"
            ):

                filename = (
                    f"{monster}_{sound_type}.wav"
                )

                path = os.path.join(
                    base,
                    "monsters",
                    filename
                )

                if os.path.exists(path):

                    try:
                        key = (
                            f"{monster}_{sound_type}"
                        )

                        self.sounds[key] = (
                            pygame.mixer.Sound(path)
                        )

                        print(
                            f"Sound loaded: {path}"
                        )

                    except pygame.error:
                        print(
                            f"Invalid sound, "
                            f"skipping: {path}"
                        )

                else:
                    print(
                        f"Sound not found, "
                        f"skipping: {path}"
                    )