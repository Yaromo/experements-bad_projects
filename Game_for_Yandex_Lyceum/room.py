import pygame
from controller import use_sqlite, load_image, load_music, save, load_json
from items import Item
import random

from menu import DeathPause, Pause, Menu


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.mask = pygame.mask.from_surface(self.image)

        self.stop_animation = 0 # считать в тиках! НЕ В СЕКУНДАХ

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if not self.stop_animation:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


    def render(self, screen):
        screen.blit(self.image, self.rect)

class Player(AnimatedSprite):
    def __init__(self, speed, sheet, columns, rows, x, y):
        super().__init__(sheet, columns, rows, x, y)
        self.rect.centerx, self.rect.centery = self.rect.x, self.rect.y
        self.speed = speed
        self.d_speed = (speed * 2) ** 0.5 # скорость по диагонали
        self.max_speed = 5
        self.coins = 0
        self.max_hp = 3
        self.max_max_hp = 6
        self.hp = 3
        self.rocks = 0
        self.up = False
        self.down = False
        self.right = False
        self.left = False
        self.shooting = False
        self.life = 1
        self.item = False
        self.activ_item = False

        self.thrown_rock = load_image("./data/game/sprite/rock.png")

        self.stop_damage = 0
        self.stop_pick_up_items = 0
        self.stop_shooting = 0

    def update(self, all_sprites): # self.borders, self.danger, self.consumable, self.spike, self.buttons, doors

        if (self.up or self.down) and (self.left or self.right):
            self.walk(self.d_speed, all_sprites[0])
        else:
            self.walk(self.speed, all_sprites[0])

        if not self.stop_damage:
            self.can_get_damage(all_sprites[1], all_sprites[3])
        elif self.stop_damage:
            self.stop_damage -= 1

        if self.shooting:
            self.shot(all_sprites[1])

        if self.stop_shooting:
            self.stop_shooting -= 1

        self.can_consum_pick_up(all_sprites[2])
        self.button_click(all_sprites[4])

        if self.stop_shooting and self.shooting:
            self.shot(all_sprites[1])


    def walk(self, speed, borders):
        start_x, start_y = self.rect.x, self.rect.y

        if self.right:
            if 16 <= self.cur_frame + 1 < 24 and not self.stop_animation:
                self.cur_frame += 1
            elif not self.stop_animation and not (self.up or self.down):
                self.cur_frame = 16
            self.rect.centerx += speed
        if self.left:
            if 24 <= self.cur_frame + 1 < 32 and not self.stop_animation:
                self.cur_frame += 1
            elif not self.stop_animation and not (self.up or self.down):
                self.cur_frame = 24
            self.rect.centerx -= speed

        if self.can_walk(borders):
            self.rect.x = start_x

        if self.up:
            if 0 <= self.cur_frame + 1 < 6 and not self.stop_animation:
                self.cur_frame += 1
            elif not self.stop_animation:
                self.cur_frame = 0
            self.rect.centery -= speed
        if self.down:
            if 8 <= self.cur_frame + 1 < 14 and not self.stop_animation:
                self.cur_frame += 1
            elif not self.stop_animation:
                self.cur_frame = 8
            self.rect.centery += speed

        if self.can_walk(borders):
            self.rect.y = start_y

        if not self.stop_animation:
            self.stop_animation = 5
            if not any([self.left, self.right, self.up, self.down]):
                self.cur_frame = 8
        else:
            self.stop_animation -= 1

        self.image = self.frames[self.cur_frame]

    def button_click(self, buttons):
        for i in buttons:
            if pygame.sprite.collide_mask(self, i):
                i.update()

    def can_walk(self, borders):
        for i in borders:
            if pygame.sprite.collide_mask(self, i):
                return True
        return False

    def can_consum_pick_up(self, consum):
        for i in consum:
            if pygame.sprite.collide_mask(self, i):
                if isinstance(i, Coin):
                    i.kill()
                    if self.coins < 99:
                        self.coins += 1
                elif isinstance(i, Rock):
                    i.kill()
                    if self.rocks < 99:
                        self.rocks += 1
                elif isinstance(i, Hp):
                    i.kill()
                    if self.hp < self.max_hp:
                        self.hp += 1
                elif not self.stop_pick_up_items:
                    self.kick_item(consum)
                    self.item = i
                    self.stop_pick_up_items = 60
                    i.kill()

        if self.stop_pick_up_items:
            self.stop_pick_up_items -= 1

    def can_get_damage(self, danger, spike):
        for i in spike:
            if pygame.sprite.collide_mask(self, i):
                self.stop_damage = 60
                self.hp -= 1
                return True
        for i in danger:
            if pygame.sprite.collide_mask(self, i):
                self.stop_damage = 60
                self.hp -= 1
                return True

    def use_item(self):
        if self.item:
            self.item.use(self)

    def kick_item(self, consum):
        if self.item:
            self.item.kick(self.rect.x, self.rect.y, consum)
            self.item = False

    def move(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def shot(self, danger):
        if self.rocks and not self.stop_shooting:
            if self.up: # up
                x, y = self.rect.centerx, int(self.rect.centery - self.rect.width * 0.6)
                x_update, y_update = 0, -self.speed * 2
            elif self.right: # right
                x, y = int(self.rect.centerx + self.rect.height * 0.6), self.rect.centery
                x_update, y_update = self.speed * 2, 0
            elif self.left: # down
                x, y = int(self.rect.centerx - self.rect.height * 0.6), self.rect.centery
                x_update, y_update = -self.speed * 2, 0
            else:
                x, y = self.rect.centerx, int(self.rect.centery + self.rect.width * 0.6)
                x_update, y_update = 0, self.speed * 2
            self.stop_shooting = 20

            self.rocks -= 1

            rock = ThrownRock(self.thrown_rock, x, y, x_update, y_update)
            rock.add(danger)

    def new_run(self):
        self.speed = 2
        self.d_speed = (2 * 2) ** 0.5  # скорость по диагонали
        self.coins = 0
        self.max_hp = 3
        self.max_max_hp = 6
        self.hp = 3
        self.rocks = 0
        self.up = False
        self.down = False
        self.right = False
        self.left = False
        self.shooting = False
        self.life = 1
        self.item = False
        self.activ_item = False

        self.thrown_rock = load_image("./data/game/sprite/rock.png")

        self.stop_damage = 0
        self.stop_pick_up_items = 0
        self.stop_shooting = 0

class Button(AnimatedSprite):
    def __init__(self, sheet, x, y):
        super().__init__(sheet, 2, 1, x, y)
        self.cur_frame = 0

    def update(self):
        if not self.cur_frame:
            self.cur_frame = 1
            self.image = self.frames[self.cur_frame]

    def status(self):
        if self.cur_frame:
            return True
        return False


class Spike(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

    def render(self, screen):
        screen.blit(self.image, self.rect)


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        if x1 == x2:  # вертикальная стенка
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Wall(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

    def render(self, screen):
        screen.blit(self.image, self.rect)


class Door(AnimatedSprite):
    def __init__(self, x, y, sheet, status, angle):
        super().__init__(sheet, 2, 1, x, y)
        self.cur_frame = status
        self.angle = angle
        self.image = pygame.transform.rotate(self.frames[self.cur_frame], self.angle)
        self.mask = pygame.mask.from_surface(self.image)


    def change_status(self, status):
        self.cur_frame = status
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.rotate(self.frames[self.cur_frame], self.angle)
        self.mask = pygame.mask.from_surface(self.image)

    def render(self, screen):
        screen.blit(self.image, self.rect)


class Coin(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

    def render(self, screen):
        screen.blit(self.image, self.rect)


class Rock(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

    def render(self, screen):
        screen.blit(self.image, self.rect)


class Hp(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

    def render(self, screen):
        screen.blit(self.image, self.rect)


class ThrownRock(pygame.sprite.Sprite):
    def __init__(self, image, x, y, x_update, y_update):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.x_update = x_update
        self.y_update = y_update
        self.mask = pygame.mask.from_surface(self.image)

    def render(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, *sprites):
        self.rect.x += self.x_update
        self.rect.y += self.y_update
        if self.can_walk(sprites[2]):
            self.kill()

    def can_walk(self, borders):
        for i in borders:
            if pygame.sprite.collide_mask(self, i):
                return True
        return False


class Entity(AnimatedSprite):
    def __init__(self, sheet, columns, rows, x, y, speed):
        super().__init__(sheet, columns, rows, x, y)
        self.vector = [0, 0, 0, 0] # 1 - < 2 - up 3 - > 4 - down
        self.speed = speed
        self.hp = 1

    def new_vector(self, target_x, target_y):
        self.vector[0] = 1 if target_x < self.rect.x else 0
        self.vector[1] = 1 if target_y < self.rect.y else 0
        self.vector[2] = 1 if target_x > self.rect.x else 0
        self.vector[3] = 1 if target_y > self.rect.y else 0

    def walk(self, speed, borders):
        start_x, start_y = self.rect.x, self.rect.y

        if self.vector[2]:
            if 16 <= self.cur_frame + 1 < 24 and not self.stop_animation:
                self.cur_frame += 1
            elif not self.stop_animation and not (self.vector[1] or self.vector[3]):
                self.cur_frame = 16
            self.rect.x += speed
        if self.vector[0]:
            if 24 <= self.cur_frame + 1 < 32 and not self.stop_animation:
                self.cur_frame += 1
            elif not self.stop_animation and not (self.vector[1] or self.vector[3]):
                self.cur_frame = 24
            self.rect.x -= speed

        if self.can_walk(borders):
            self.rect.x = start_x

        if self.vector[1]:
            if 0 <= self.cur_frame + 1 < 6 and not self.stop_animation:
                self.cur_frame += 1
            elif not self.stop_animation:
                self.cur_frame = 0
            self.rect.y -= speed
        if self.vector[3]:
            if 8 <= self.cur_frame + 1 < 14 and not self.stop_animation:
                self.cur_frame += 1
            elif not self.stop_animation:
                self.cur_frame = 8
            self.rect.y += speed

        if self.can_walk(borders):
            self.rect.y = start_y

        if not self.stop_animation:
            self.stop_animation = 10
            if not any(self.vector):
                self.cur_frame = 8
        else:
            self.stop_animation -= 1

        self.image = self.frames[self.cur_frame]

    def can_walk(self, borders):
        for i in borders:
            if pygame.sprite.collide_mask(self, i):
                return True
        return False

    def take_damage(self, danger, spike):
        for i in danger:
            if pygame.sprite.collide_mask(self, i):
                if type(i) != Entity:
                    self.hp -= 1
        for i in spike:
            if pygame.sprite.collide_mask(self, i):
                self.hp -= 1


    def update(self, target_x, target_y, borders, danger, spike):
        self.new_vector(target_x, target_y)

        if (self.vector[1] or self.vector[3]) and (self.vector[0] or self.vector[2]):
            self.walk((self.speed ** 2 * 2) ** 0.5, borders)
        else:
            self.walk(self.speed, borders)

        self.take_damage(danger, spike)
        if self.hp <= 0:
            self.kill()


    def render(self, screen):
        screen.blit(self.image, self.rect)


class Game:
    def __init__(self, fps, sprites_room):

        self.consumable = pygame.sprite.Group()
        self.borders = pygame.sprite.Group()
        self.danger = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        self.spike = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()

        self.image = load_image("./data/game/sprite/room.png")
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 10

        self.player_image = load_image("./data/game/sprite/player.png")
        self.player = Player(3, self.player_image, 8, 4, self.rect.centerx, self.rect.centery)

        self.ngr = False
        self.number_room = -1

        self.coin_image = load_image("./data/game/sprite/coin.png")
        self.spike_image = load_image("./data/game/sprite/spike.png")
        self.wall_image = load_image("./data/game/sprite/wall.png")
        self.button_image = load_image("./data/game/sprite/button.png")
        self.item_image = load_image("./data/game/sprite/item.png")
        self.door_image = load_image("./data/game/sprite/door.png")
        self.no_hp_image = load_image("./data/game/sprite/no_hp.png")
        self.hp_image = load_image("./data/game/sprite/hp.png")
        self.rock_image = load_image("./data/game/sprite/rock.png")

        self.entity_image = load_image("./data/game/sprite/player.png")
        width, height = self.entity_image.get_size()

        # Изменение цвета пикселей
        for x in range(width):
            for y in range(height):
                current_color = self.entity_image.get_at((x, y))
                if current_color[3]:
                    self.entity_image.set_at((x, y), (current_color[0], 0, 0))

        self.generate_room(**sprites_room)

        self.doors_status = True
        self.stop_open_door = 0

        self.f1 = pygame.font.Font(None, 15)

        k = 0
        for i in ((335, 65), (65, 335), (335, 605), (605, 335)):
            door = Door(*i, self.door_image, self.doors_status, k)
            door.add(self.doors)
            k += 90

        self.menu = Menu()
        self.pause = Pause()
        self.death_pause = DeathPause()

        self.nr = False

    def generate_room(self, **sprites_room):

        self.consumable.empty()
        self.borders.empty()
        self.danger.empty()
        self.buttons.empty()
        self.spike.empty()
        self.number_room += 1

        for i in sprites_room['borders']:
            wall = Wall(self.wall_image, i[0], i[1])
            wall.add(self.borders)

        for i in sprites_room["buttons"]:
            button = Button(self.button_image, i[0], i[1])
            button.add(self.buttons)

        for i in sprites_room['consumable']: # сделать шанс для замены на предмет
            a = random.randint(1, 40)
            if a <= 10:
                consum = Coin(self.coin_image, i[0], i[1])
            elif a <= 20:
                consum = Rock(self.rock_image, i[0] + 17, i[1] + 17)
            elif a <= 30:
                consum = Item(self.item_image, i[0], i[1])
            else:
                consum = Hp(self.hp_image, i[0] + 17, i[1] + 17)

            consum.add(self.consumable)

        for i in sprites_room["spike"]:
            spike = Spike(self.spike_image, i[0], i[1])
            spike.add(self.spike)

        for i in sprites_room["entities"]:
            entity = Entity(self.entity_image,8, 4, i[0], i[1], 1)
            entity.add(self.danger)

        for i in ((110, 110, 610, 110), (110, 110, 110, 610), (110, 610, 610, 610), (610, 110, 610, 610)):
            border = Border(*i)
            border.add(self.borders)

        self.doors_status = False
        for i in self.doors:
            i.change_status(self.doors_status)

        self.ngr = False

    def update(self, screen, events, setting):
        running = True

        if not any([self.menu.run, self.pause.run, self.death_pause.run]):

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == setting["left"][0]:
                        self.player.left = True
                    if event.key == setting["up"][0]:
                        self.player.up = True
                    if event.key == setting["right"][0]:
                        self.player.right = True
                    if event.key == setting["down"][0]:
                        self.player.down = True
                    if event.key == setting['use_item'][0]:
                        self.player.use_item()
                    if event.key == setting['shot'][0]:
                        self.player.shooting = True
                if event.type == pygame.KEYUP:
                    if event.key == setting["left"][0]:
                        self.player.left = False
                    if event.key == setting["up"][0]:
                        self.player.up = False
                    if event.key == setting["right"][0]:
                        self.player.right = False
                    if event.key == setting["down"][0]:
                        self.player.down = False
                    if event.key == setting['shot'][0]:
                        self.player.shooting = False
                    if event.key == pygame.K_ESCAPE:
                        self.pause.run = not self.pause.run

            if not running:
                return False

            if self.stop_open_door == 0 and not self.doors_status:
                if self.buttons and all([i.status() for i in self.buttons]) or not self.buttons:
                    self.doors_status = True
                    self.stop_open_door = 30

            if self.stop_open_door > 0 and self.doors_status:
                self.stop_open_door -= 1

            if self.stop_open_door == 0 and self.doors_status:
                for i in self.doors:
                    i.change_status(self.doors_status)
                self.stop_open_door -= 1

            if self.doors_status and self.stop_open_door == -1:
                for i in self.doors:
                    if pygame.sprite.collide_mask(self.player, i):
                        self.ngr = True
                        self.stop_open_door = 0

            self.player.update([self.borders, self.danger, self.consumable, self.spike, self.buttons, self.doors])
            self.danger.update(self.player.rect.x, self.player.rect.y, self.borders, self.danger, self.spike)
            if self.player.hp == 0:
                self.death_pause.run = True

        if self.menu.run:
            a = self.menu.update(events, screen)

            if not a:
                running = False
                return False
        elif not all([self.menu.run,self.death_pause]):
            self.render(screen)

        if self.pause.run and not self.death_pause.run:
            a = self.pause.update(events, screen)
            if not a:
                running = False
                return False
            if a == 2:
                self.menu.run = True

        if self.death_pause.run:
            a = self.death_pause.update(events, screen)
            if not a:

                running = False
                return False
            if a == 2:
                self.menu.run = True
            if not self.death_pause.run:
                self.player.new_run()
                self.nr = True
                self.number_room = -1

        print(not self.menu.run and not self.death_pause)
        return True


    def render(self, screen):
        screen.blit(self.image, self.rect)
        for i in [self.buttons, self.consumable, self.spike, self.buttons, self.doors, self.danger]:
            for j in i:
                j.render(screen)
        for i in self.borders:
            if isinstance(i, Wall):
                i.render(screen)
        for i in range(self.player.max_hp):
            if i + 1 <= self.player.hp:
                rect = self.hp_image.get_rect()
                rect.x = 100 + (i + 1) * 11
                rect.y = 11
                screen.blit(self.hp_image, rect)
            else:
                rect = self.no_hp_image.get_rect()
                rect.x = 100 + (i + 1) * 11
                rect.y = 11
                screen.blit(self.no_hp_image, rect)
        text_coin = self.f1.render(f'{self.player.coins:02}', 1, (0, 0, 0))
        screen.blit(text_coin, (111, 26))
        screen.blit(self.coin_image, (115, 5))
        text_rock = self.f1.render(f'{self.player.rocks:02}', 1, (0, 0, 0))
        screen.blit(text_rock, (111, 45))
        screen.blit(self.rock_image, (130, 44))
        text_n_rooms = self.f1.render(f'Количество комнат: {self.number_room}', 1, (0, 0, 0))
        screen.blit(text_n_rooms, (310, 45))
        if self.player.item:
            screen.blit(self.player.item.image, (670, 670))

        self.player.render(screen)


