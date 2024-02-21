import pygame


class Item:

    def __init__(self, x, y, health, happiness, image_name):
        # Set up basic fields
        self.x = x
        self.y = y
        self.health = health
        self.happiness = happiness
        # Load and store the image
        self.image = pygame.image.load(image_name)
        # Shift the image rect so the x and y are at the center of the image instead of the top left
        rect = self.image.get_rect()
        self.image_rect = pygame.Rect(x - rect.width / 2, y - rect.height / 2,
                                      rect.width, rect.height)


class Pet:

    def __init__(self, x, y, health, max_health, happiness, max_happiness):
        # set basic fields
        self.x = x
        self.y = y
        # health = radius
        self.health = health
        self.max_health = max_health
        # happiness = green color
        self.happiness = happiness
        self.max_happiness = max_happiness
        self.color = pygame.Color(0, happiness, 0)

    # return x and y position (center of circle) as 2D vector
    def get_pos(self):
        return pygame.Vector2(self.x, self.y)

    # return a rect surround the circle where x and y are center - radius. width and height are radius * 2
    def get_rect(self):
        return pygame.Rect(self.x - self.health, self.y - self.health, self.health * 2, self.health * 2)

    def move(self, x_amount, y_amount):
        self.x += x_amount
        self.y += y_amount

    def consume_item(self, item):
        self.update_happiness(item.happiness)
        self.update_health(item.health)

    def update_health(self, d_h):
        self.health += d_h
        if self.health > self.max_health:
            self.health = self.max_health
        elif self.health < 0:
            self.health = 0

    def update_happiness(self, d_h):
        self.happiness += d_h
        if self.happiness > self.max_happiness:
            self.happiness = self.max_happiness
        elif self.happiness < 0:
            self.happiness = 0
        self.color = pygame.Color(0, self.happiness, 0)

    def check_if_dead(self):
        return self.health <= 0 or self.happiness <= 0


class Game:

    def __init__(self):
        # display variables
        self.width = 500
        self.length = 500
        self.background_color = "white"
        self.buttons_bar_height = 100
        self.buttons_bar_color = "purple"
        # Pygame specific variables
        self.screen = pygame.display.set_mode((self.width, self.length))
        pygame.display.set_caption("Virtual Pet")
        self.clock_tick = 60
        self.clock = pygame.time.Clock()
        # Item variables
        self.image_names = ["apple.png", "icecream.png", "toy.png"]
        self.item_mode_index = 0
        self.item = None
        # Button variables
        self.apple_button = Item(self.width / 4, self.buttons_bar_height / 2, 0, 0,
                                 self.image_names[0])
        self.icecream_button = Item(self.width / 2, self.buttons_bar_height / 2, 0,
                                    0, self.image_names[1])
        self.toy_button = Item(self.width / 4 * 3, self.buttons_bar_height / 2, 0,
                               0, self.image_names[2])
        # Pet variables
        self.pet = Pet(self.width / 2, self.length / 2, 50, 100, 180, 255)
        self.speed = 2
        self.d_x = 0
        self.d_y = 0
        self.decay_rate = -1
        self.current_tick = 0
        self.size_update_rate = self.clock_tick / 3
        self.color_update_rate = self.clock_tick / 10

    # select an item or place an item depending on the area clicked
    def handle_mouse_click(self):
        pos = pygame.mouse.get_pos()
        # check for button click
        if self.apple_button.image_rect.collidepoint(pos):
            self.item_mode_index = 0
        elif self.icecream_button.image_rect.collidepoint(pos):
            self.item_mode_index = 1
        elif self.toy_button.image_rect.collidepoint(pos):
            self.item_mode_index = 2
        # nothing if user clicks in the button bar but not on a button
        elif pos[1] < self.buttons_bar_height:
            return
        # create an item at current mouse position
        else:
            self.create_item(pos)

    # spawn an item at mouse position
    def create_item(self, pos):
        # get current image name
        image_name = self.image_names[self.item_mode_index]
        # create an item at the position
        if self.item_mode_index == 0:
            self.item = Item(pos[0], pos[1], 20, 0, image_name)
        elif self.item_mode_index == 1:
            self.item = Item(pos[0], pos[1], -10, 60, image_name)
        elif self.item_mode_index == 2:
            self.item = Item(pos[0], pos[1], 0, 40, image_name)
        # start moving the pet
        self.set_speed()

    def set_speed(self):
        d_x = abs(self.pet.x - self.item.x)
        d_y = abs(self.pet.y - self.item.y)
        if d_x >= d_y:
            self.d_x = self.speed
            self.d_y = self.speed * (d_y / d_x)
        else:
            self.d_x = self.speed * (d_x / d_y)
            self.d_y = self.speed
        if self.pet.x > self.item.x:
            self.d_x = -self.d_x
        if self.pet.y > self.item.y:
            self.d_y = -self.d_y

    def handle_item_collision(self):
        if self.item != None and self.item.image_rect.colliderect(self.pet.get_rect()):
            self.pet.consume_item(self.item)
            # remove item
            self.item = None
            self.d_x = 0
            self.d_y = 0

    def update_pet(self):
        self.pet.move(self.d_x, self.d_y)
        # update health and happiness
        self.current_tick += 1
        # decay health 3x per second
        if self.current_tick % self.size_update_rate == 0:
            self.pet.update_health(self.decay_rate)
        # decay happiness 10x per second
        if self.current_tick % self.color_update_rate == 0:
            self.pet.update_happiness(self.decay_rate)
        # reset tick if it becomes too large
        if self.current_tick == 60:
            self.current_tick = 0

    def draw_everything(self):
        # Screen
        self.screen.fill(self.background_color)
        # Item
        if self.item != None:
            self.screen.blit(self.item.image, self.item.image_rect)
        # Pet
        pygame.draw.circle(self.screen, self.pet.color, self.pet.get_pos(), self.pet.health)
        # Button bar
        pygame.draw.rect(self.screen, self.buttons_bar_color,
                         pygame.Rect(0, 0, self.width, self.buttons_bar_height))
        # Buttons
        self.screen.blit(self.apple_button.image, self.apple_button.image_rect)
        self.screen.blit(self.icecream_button.image,
                         self.icecream_button.image_rect)
        self.screen.blit(self.toy_button.image, self.toy_button.image_rect)
        # Update
        pygame.display.update()

    # Run game loop
    def run(self):
        while True:
            # Handle incoming events
            for event in pygame.event.get():
                # Quit event
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click()
            # detect pet collision
            self.handle_item_collision()
            # check if pet is dead
            if self.pet.check_if_dead():
                pygame.quit()
                return

            # update
            self.update_pet()

            # draw
            self.draw_everything()

            # tick clock
            self.clock.tick(self.clock_tick)


# initialize Pygame and start running game
pygame.init()
# Creates and instance of the game class
game = Game()
game.run()
