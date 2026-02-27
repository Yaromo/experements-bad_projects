import pygame

from controller import load_image


class Menu:
    def __init__(self):
        self.image = load_image("./data/menu/sprites/menu.png")
        self.image_rect = self.image.get_rect()
        self.image_rect = 10, 10

        self.play_btn_image = load_image("./data/menu/sprites/play_btn.png")
        self.play_btn_rect = self.play_btn_image.get_rect()
        self.play_btn_rect.x, self.play_btn_rect.y = 275, 300

        self.setting_btn_image = load_image("./data/menu/sprites/setting_btn.png")
        self.setting_btn_rect = self.setting_btn_image.get_rect()
        self.setting_btn_rect.x, self.setting_btn_rect.y = 250, 400

        self.quit_btn_image = load_image("./data/menu/sprites/quit_btn.png")
        self.quit_btn_rect = self.quit_btn_image.get_rect()
        self.quit_btn_rect.x, self.quit_btn_rect.y = 285, 500

        self.run = True
        self.setting_run = False
        self.setting = Setting(self.image)

    def render(self, screen):
        screen.blit(self.image, self.image_rect)
        screen.blit(self.play_btn_image, self.play_btn_rect)
        screen.blit(self.setting_btn_image, self.setting_btn_rect)
        screen.blit(self.quit_btn_image, self.quit_btn_rect)

    def click(self, x, y):
        if self.play_btn_rect.collidepoint(x, y):
            return 1
        elif self.setting_btn_rect.collidepoint(x, y):
            return 2
        elif self.quit_btn_rect.collidepoint(x, y):
            return 3
        return 0


    def update(self, events, screen):
        running = True
        if not self.setting.run:
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        result = self.click(*event.pos)
                        if result == 1:
                            self.run = False
                        elif result == 2:
                            self.setting_run = True
                        elif result == 3:
                            running = False
            self.render(screen)
        else:
            if self.setting.update(events, screen):
                running = False

        return running


class Pause:
    def __init__(self):
        self.run = False

        self.play_btn_image = load_image("./data/menu/sprites/play_btn.png")
        self.play_btn_rect = self.play_btn_image.get_rect()
        self.play_btn_rect.x, self.play_btn_rect.y = 275, 300

        self.menu_btn_image = load_image("./data/menu/sprites/menu_btn.png")
        self.menu_btn_rect = self.menu_btn_image.get_rect()
        self.menu_btn_rect.x, self.menu_btn_rect.y = 250, 400

        self.quit_btn_image = load_image("./data/menu/sprites/quit_btn.png")
        self.quit_btn_rect = self.quit_btn_image.get_rect()
        self.quit_btn_rect.x, self.quit_btn_rect.y = 285, 500

        self.stop = 1

    def click(self, x, y):
        if self.play_btn_rect.collidepoint(x, y):
            return 1
        elif self.menu_btn_rect.collidepoint(x, y):
            return 2
        elif self.quit_btn_rect.collidepoint(x, y):
            return 3
        return 0

    def update(self, events, screen):
        running = True
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.stop -= 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    if self.stop <= 0:
                        self.run = False
                        self.stop = 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    result = self.click(*event.pos)
                    if result == 1:
                        self.run = False
                    elif result == 2:
                        self.run = False
                        return 2
                    elif result == 3:
                        self.run = False
                        running = False
        self.render(screen)
        return running

    def render(self, screen):

        screen.blit(self.play_btn_image, self.play_btn_rect)
        screen.blit(self.menu_btn_image, self.menu_btn_rect)
        screen.blit(self.quit_btn_image, self.quit_btn_rect)

class DeathPause:
    def __init__(self):
        self.run = False
        self.f1 = pygame.font.Font(None, 15)
        self.text = self.f1.render(f'Вы проиграли', 1, (0, 0, 0))
        self.play_btn_image = load_image("./data/menu/sprites/play_btn.png")
        self.play_btn_rect = self.play_btn_image.get_rect()
        self.play_btn_rect.x, self.play_btn_rect.y = 275, 300

        self.menu_btn_image = load_image("./data/menu/sprites/menu_btn.png")
        self.menu_btn_rect = self.menu_btn_image.get_rect()
        self.menu_btn_rect.x, self.menu_btn_rect.y = 250, 400

        self.quit_btn_image = load_image("./data/menu/sprites/quit_btn.png")
        self.quit_btn_rect = self.quit_btn_image.get_rect()
        self.quit_btn_rect.x, self.quit_btn_rect.y = 285, 500

        self.stop = 1

        self.image = load_image("./data/menu/sprites/menu.png")
        self.image_rect = self.image.get_rect()
        self.image_rect = 10, 10

    def click(self, x, y):
        if self.play_btn_rect.collidepoint(x, y):
            return 1
        elif self.menu_btn_rect.collidepoint(x, y):
            return 2
        elif self.quit_btn_rect.collidepoint(x, y):
            return 3
        return 0

    def update(self, events, screen):
        running = True
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    result = self.click(*event.pos)
                    if result == 1:
                        self.run = False
                    elif result == 2:
                        self.run = False
                        return 2
                    elif result == 3:
                        self.run = False
                        running = False
        self.render(screen)
        return running

    def render(self, screen):
        screen.blit(self.image, self.image_rect)
        screen.blit(self.play_btn_image, self.play_btn_rect)
        screen.blit(self.menu_btn_image, self.menu_btn_rect)
        screen.blit(self.quit_btn_image, self.quit_btn_rect)
        screen.blit(self.text, (300, 100))

class Setting:
    def __init__(self, image):
        self.run = False
        self.image = image
        self.image_rect = self.image.get_rect()
        self.image_rect = 10, 10

    def click(self, x, y):
        pass

    def update(self, events, update):
        pass

    def render(self, screen):
        pass