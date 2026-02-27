import pygame
import json
from room import Game
import random


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption('<3')

    size = width, height = 720, 720
    screen = pygame.display.set_mode(size)

    running = True
    game_running = False

    setting_file = open("./data/game/settings.json", 'r')
    setting = json.load(setting_file)


    rooms_file = open("./data/game/rooms.json", 'r')
    roms = json.load(rooms_file)

    fps = 60
    game = Game(fps, roms['1'])
    clock = pygame.time.Clock()

    while running:
        screen.fill((0, 0, 0))
        if game.ngr:
            a = str(random.randint(1, 20))
            game.generate_room(**roms[a])
        if not game.update(screen, pygame.event.get(), setting):
            running = False
        if game.nr:
            game.generate_room(**roms["1"])
            game.nr = False
        pygame.display.flip()
        clock.tick(fps)
    setting_file.close()
    rooms_file.close()