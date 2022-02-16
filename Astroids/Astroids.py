import pygame
import random
import os
from math import radians, sin, cos

class Settings(object):

    window = {'width':1500, 'height':900}
    fps = 60
    title = "Astroids"  

    Ship_size = (50,50)
    

    astreoids_load = ['Astroids1.png']

    astreoids_size = (100,150,230)

    astreoids_speed = (-4, 4)

    path = {}
    path['file'] = os.path.dirname(os.path.abspath(__file__))
    path['image'] = os.path.join(path['file'], "image")


    @staticmethod
    def dim():
        return (Settings.window['width'], Settings.window['height'])

    @staticmethod
    def filepath(name):
        return os.path.join(Settings.path['file'], name)

    @staticmethod
    def imagepath(name):
        return os.path.join(Settings.path['image'], name)

    

class Background(pygame.sprite.Sprite):
    def __init__(self, image) -> None:
        super().__init__()
        self.image = image
        self.image = pygame.image.load(Settings.imagepath(self.image)).convert_alpha()
        self.image = pygame.transform.scale(self.image, Settings.dim())
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, (0,0))

class Timer(object):
    def __init__(self, duration, with_start = True):
        self.duration = duration
        if with_start:
            self.next = pygame.time.get_ticks()
        else:
            self.next = pygame.time.get_ticks() + self.duration

    def is_next_stop_reached(self):
        if pygame.time.get_ticks() > self.next:
            self.next = pygame.time.get_ticks() + self.duration
            return True
        return False

    def change_duration(self, delta=10):
        self.duration += delta
        if self.duration < 0:
            self.duration = 0


class Ship(pygame.sprite.Sprite):
    def __init__(self, filename, boost_filename):
        super().__init__()
        self.normal_filename = filename
        self.boost_filename = boost_filename
        self.filename = self.normal_filename
        self.update_sprite(self.filename)
        self.setposition(Settings.dim()[0] // 2 - self.rect.width // 2, Settings.dim()[1] // 2 - self.rect.height // 2)
        self.speed_x = 0
        self.speed_y = 0
        self.angle = 0
    # Rotation des Bildes
    def update_sprite(self, filename, angle=None):
        self.image = pygame.image.load(Settings.imagepath(filename)).convert_alpha()
        self.image = pygame.transform.scale(self.image, Settings.Ship_size)
        if angle != None:
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def setposition(self, x, y):
        self.rect.left = x
        self.rect.top = y

    def accelerating(self):
        self.filename = self.boost_filename
        angle = radians(self.angle)
        new_speed_x = self.speed_x - sin(angle)
        new_speed_y = self.speed_y - cos(angle)

        if abs(new_speed_x) < 10 and abs(new_speed_y) < 10:
            self.speed_x = new_speed_x
            self.speed_y = new_speed_y

    def rotate(self, direction):
        if direction == 'right':
            self.angle -= 5
            
        elif direction == 'left':
            self.angle += 5

        old_center = self.rect.center
        self.update_sprite(self.filename, self.angle)
        self.rect.center = old_center

    def check_wall_collision(self):
        if self.rect.left > Settings.window['width']:
            self.rect.right = 0

        if self.rect.top > Settings.window['height']:
            self.rect.bottom = 0

        if self.rect.right < 0:
            self.rect.left = Settings.window['width']

        if self.rect.bottom < 0:
            self.rect.top = Settings.window['height']

    def move(self):
        self.rect.move_ip(self.speed_x, self.speed_y)

    def colision_ship(self):
        if pygame.sprite.spritecollide(self, game.asteroids, False, pygame.sprite.collide_mask):
           game.running = False

    def update(self):
        self.move()
        self.check_wall_collision()
        self.colision_ship()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, image, game):
        super().__init__()
        self.game = game
        self.image = image
        self.image = pygame.image.load(Settings.imagepath(self.image)).convert_alpha()
        self.image = pygame.transform.scale(self.image, Settings.Ship_size)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.find_spawn_position()
        self.speed = (random.randint(*Settings.astreoids_speed), random.randint(*Settings.astreoids_speed))
        
    def move(self): 
        self.rect.move_ip(self.speed)
        # Spawn schutz
    def check_wall_collision(self):
        if self.rect.left > Settings.window['width']:
            self.rect.right = 0

        if self.rect.top > Settings.window['height']:
            self.rect.bottom = 0

        if self.rect.right < 0:
            self.rect.left = Settings.window['width']

        if self.rect.bottom < 0:
            self.rect.top = Settings.window['height']
    
    def find_spawn_position(self):
        position = (random.randint(0, Settings.window['width'] - self.rect.width), random.randint(0, Settings.window['height'] - self.rect.height))
        self.set_position(*position)
        self.check_new_position()

    def check_new_position(self):
        collisions = pygame.sprite.spritecollide(self, self.game.ship, False, pygame.sprite.collide_circle_ratio(2.5)) # Ganz Komische sache hier
        if len(collisions) > 0:
            self.find_spawn_position()
        
    def set_position(self, x, y):
        self.rect.left = x
        self.rect.top = y

    def update(self):
        self.move()
        self.check_wall_collision()
 
    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Game():
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.display.set_caption(Settings.title)

        self.screen = pygame.display.set_mode(Settings.dim())
        self.clock = pygame.time.Clock()
        self.astreoids_size = random.randint(Settings.astreoids_size[0], Settings.astreoids_size[2])
        self.ship = pygame.sprite.GroupSingle(Ship('Ship1.png', 'Ship2.png'))
        self.background = Background('background.jpg')
        self.asteroids = pygame.sprite.Group()
        self.astreoids_size = random.randint(Settings.astreoids_size[0], Settings.astreoids_size[2])
        for i in range (5):
            self.asteroids.add(Asteroid(Settings.astreoids_load[0], self))

        self.running = True

    def run(self) -> None:
        while self.running:
            self.clock.tick(Settings.fps)
            self.watch_for_events()
            self.update()
            self.draw()
        pygame.quit()

    def watch_for_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

        press = pygame.key.get_pressed()
        if press[pygame.K_UP] or press[pygame.K_w]:
            self.ship.sprite.accelerating()
        else:
            self.ship.sprite.filename = self.ship.sprite.normal_filename

        if press[pygame.K_RIGHT] or press[pygame.K_d]:
            self.ship.sprite.rotate('right')
            
        if press[pygame.K_LEFT] or press[pygame.K_a]:
            self.ship.sprite.rotate('left')
                    
    def update(self):
        self.ship.sprite.update()
        self.asteroids.update()

    def draw(self):
        self.background.draw(self.screen)
        self.ship.sprite.draw(self.screen)
        self.asteroids.draw(self.screen)
        pygame.display.flip()
        
if __name__ == '__main__':
    game = Game()
    game.run()
