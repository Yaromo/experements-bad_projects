import pygame
import random


class Item(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def use(self, player):
        a = random.randint(1, 4)
        if a == 1:
            player.max_hp += 1
            if player.max_hp > player.max_max_hp:
                player.max_hp = player.max_max_hp
        elif a == 2:
            if player.speed < player.max_speed:
                player.speed += 1
                player.d_speed = (player.speed * 2) ** 0.5
        elif a == 3:
            player.coins += 10
            if player.coins > 99:
                player.coins = 99
        else:
            player.rocks += 10
            if player.rocks > 99:
                player.rocks = 99
        player.item = False


    def kick(self, x, y, consum):
        self.rect.x = x
        self.rect.y = y
        self.add(consum)

    def render(self, screen):
        screen.blit(self.image, self.rect)