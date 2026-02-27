import pygame
import json
import os
import sys


def use_sqlite(file):
    pass


def save(game):
    pass


def load_image(name, colorkey=None):
    if not os.path.isfile(name):
        print(f"Файл с изображением '{name}' не найден")
        sys.exit()
    image = pygame.image.load(name)
    return image


def load_music(name):
    if not os.path.isfile(name):
        print(f"Файл с изображением '{name}' не найден")
        sys.exit()
    music = pygame.mixer.load(name)
    return music


def load_json(name):
    pass

