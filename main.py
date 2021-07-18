import pygame
import random

# Import pygame.locals for easier access to key coordinates

from pygame.locals import (
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
)

# Define constants for the screen width and height
NAYTTO_LEVEYS = 800
NAYTTO_KORKEUS = 600

TAUSTA_VARI = (34, 34, 34)
REUNA_VARI = (28, 98, 215)
REUNA_LEVEYS = 5
PELIKENTTA_LEVEYS = 498

MAILA_LEVEYS = 75
MAILA_KORKEUS = 15
MAILA_NOPEUS = 10

PALLO_RADIUS = 6 # note radius should be bigger than nopeus! Otherwise collisions will not work
PALLO_NOPEUS = 5

PALIKKA_LEVEYS = 48
PALIKKA_KORKEUS = 20
PALIKKA_COLOR = (random.randint(32, 128), random.randint(32, 128), random.randint(32, 128))
PALIKKA_VALI = 2
PALIKKA_SARAKKEET = 10
PALIKKA_RIVIT = 5
PALIKAT_ALOITUS_Y = 100

FONT_FAMILY = "Comic Sans MS"
FONT_SIZE = 30


# Define a player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Maila(pygame.sprite.Sprite):
    def __init__(self):
        super(Maila, self).__init__()
        self.surf = pygame.Surface((MAILA_LEVEYS, MAILA_KORKEUS))
        self.surf.fill(TAUSTA_VARI)
        pygame.draw.rect(self.surf, (255, 0, 0), pygame.Rect(0, 0, MAILA_LEVEYS, MAILA_KORKEUS), border_radius=10)
        self.rect = self.surf.get_rect()
        self.rect.centerx = (PELIKENTTA_LEVEYS + REUNA_LEVEYS * 2) / 2
        self.rect.y = NAYTTO_KORKEUS - MAILA_KORKEUS

    # Move the sprite based on user keypresses
    def paivita(self, pressed_keys, pallo):
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-MAILA_NOPEUS, 0)
            if pallo.liikkuu == False:
                pallo.rect.move_ip(-MAILA_NOPEUS, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(MAILA_NOPEUS, 0)
            if pallo.liikkuu == False:
                pallo.rect.move_ip(MAILA_NOPEUS, 0)

        # Keep player on the screen
        if self.rect.left < REUNA_LEVEYS:
            self.rect.left = REUNA_LEVEYS
        if self.rect.right > PELIKENTTA_LEVEYS + REUNA_LEVEYS:
            self.rect.right = PELIKENTTA_LEVEYS + REUNA_LEVEYS

class Pallo(pygame.sprite.Sprite):
    def __init__(self):
        super(Pallo, self).__init__()
        self.surf = pygame.Surface((2 * PALLO_RADIUS, 2 * PALLO_RADIUS))
        self.surf.fill(TAUSTA_VARI)
        pygame.draw.circle(self.surf, (0, 255, 0), (PALLO_RADIUS, PALLO_RADIUS), PALLO_RADIUS)
        self.rect = self.surf.get_rect()
        self.rect.centerx = (PELIKENTTA_LEVEYS + REUNA_LEVEYS * 2) / 2
        self.rect.y = NAYTTO_KORKEUS - MAILA_KORKEUS - 2 * PALLO_RADIUS
        self.nopeus_x = 0
        self.nopeus_y = 0
        self.liikkuu = False
        self.score = 0

    # Move the sprite based on user keypresses
    def paivita(self, pressed_keys, maila, palikat):
        if pressed_keys[K_SPACE] and self.liikkuu == False:
            self.liikkuu = True
            self.nopeus_x = PALLO_NOPEUS
            self.nopeus_y = -PALLO_NOPEUS

        # attempt to move, then we will check for collisions
        muuta_suuntaa_x = False
        muuta_suuntaa_y = False
        self.rect.move_ip(self.nopeus_x, self.nopeus_y)

        # Check if ball have collided with the board
        if pygame.sprite.collide_rect(self, maila):
            collision_board_sound.play()

            # from side
            if (maila.rect.collidepoint(self.rect.midleft) or maila.rect.collidepoint(self.rect.midright)):
                muuta_suuntaa_x = True
                self.rect.move_ip(-self.nopeus_x, 0)    
            # from top (from any bottom corner of the ball)
            else:
                muuta_suuntaa_y = True
                self.rect.move_ip(0, -self.nopeus_y)       

        # Check if any blocks have collided with the ball
        if pygame.sprite.spritecollideany(self, palikat):
            collision_blocks_sound.play()
            palikat_tormasivat = pygame.sprite.spritecollide(self, palikat, False)

            # go through every collision and decide if direction is changed
            for p in palikat_tormasivat :

                # from side
                if (p.rect.collidepoint(self.rect.midleft) or p.rect.collidepoint(self.rect.midright)):
                    muuta_suuntaa_x = True
                    self.rect.move_ip(-self.nopeus_x, 0)    
                # from top (from any bottom corner of the ball)
                else:
                    muuta_suuntaa_y = True
                    self.rect.move_ip(0, -self.nopeus_y)

                # remove layer from breakable palika
                if p.kerroksia > 0:
                    p.kerroksia -= 1

                # remove palikkat from all groups and increase score
                if p.kerroksia == 0:
                    self.score += 1
                    p.kill()

        # Keep ball on the screen
        if self.rect.top < REUNA_LEVEYS:
            self.rect.top = REUNA_LEVEYS
            muuta_suuntaa_y = True
        if self.rect.left < REUNA_LEVEYS:
            self.rect.left = REUNA_LEVEYS
            muuta_suuntaa_x = True
        if self.rect.right > PELIKENTTA_LEVEYS + REUNA_LEVEYS:
            self.rect.right = PELIKENTTA_LEVEYS + REUNA_LEVEYS
            muuta_suuntaa_x = True

        # Change direction if needed
        if muuta_suuntaa_x == True:
             self.nopeus_x = -self.nopeus_x
        if muuta_suuntaa_y == True:
             self.nopeus_y = -self.nopeus_y

class Palikka(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Palikka, self).__init__()
        self.surf = pygame.Surface((PALIKKA_LEVEYS, PALIKKA_KORKEUS))
        self.kerroksia = random.choices([-1, 1, 2], [0.1, 0.8, 0.1])[0]
        if self.kerroksia == -1:
            # unbreakable -> white
            self.surf.fill((255, 255, 255))
        elif self.kerroksia == 2:
            # 2 layers -> grey
            self.surf.fill((96, 96, 96))
        else:
            self.surf.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            #self.surf.fill(PALIKKA_COLOR) 
        self.rect = self.surf.get_rect()
        self.rect.x = x
        self.rect.y = y

class Teksti():
    def __init__(self, text, x, y):
        self.font = pygame.font.SysFont(FONT_FAMILY, FONT_SIZE)
        self.surf = self.font.render(text, True, (255, 255, 0))
        self.x = x
        self.y = y
        self.rect = self.surf.get_rect()
        self.rect.x = x
        self.rect.y = y

    def paivita(self, text):
        self.surf = self.font.render(text, True, (255, 255, 0))
        self.rect = self.surf.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


# Initialize pygame
pygame.init()

# Load all sound files
collision_board_sound = pygame.mixer.Sound("./res/collision_board.ogg")
collision_blocks_sound = pygame.mixer.Sound("./res/collision_blocks.ogg")

# Setup the clock for a decent framerate
kello = pygame.time.Clock()

# Init drawing texts
pygame.font.init()

# Create the screen object
# The size is determined by the constant NAYTTO_LEVEYS and NAYTTO_KORKEUS
naytto = pygame.display.set_mode((NAYTTO_LEVEYS, NAYTTO_KORKEUS))
pygame.display.set_caption("Breakanoid")

# Instantiate player and other game objects
maila = Maila()
pallo = Pallo()
palikat = pygame.sprite.Group()
for i in range(PALIKKA_RIVIT):
    for j in range(PALIKKA_SARAKKEET):
        palikat.add(Palikka(REUNA_LEVEYS + (PALIKKA_LEVEYS + PALIKKA_VALI) * j, PALIKAT_ALOITUS_Y + (PALIKKA_KORKEUS + PALIKKA_VALI) * i))

# Kaikki objektit
kaikki_objektit = pygame.sprite.Group()
kaikki_objektit.add(maila)
kaikki_objektit.add(pallo)
kaikki_objektit.add(palikat)

# Static texts
score_text = Teksti("Score: " + str(pallo.score), PELIKENTTA_LEVEYS + 50, NAYTTO_KORKEUS - 100)

# Variable to keep the main loop running
running = True
turn = 0

# Main loop
while running:
    # for loop through the event queue
    for tapahtuma in pygame.event.get():
        # Check for KEYDOWN event
        if tapahtuma.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if tapahtuma.key == K_ESCAPE:
                running = False
        # Check for QUIT event. If QUIT, then set running to false.
        elif tapahtuma.type == QUIT:
            running = False

    # Get the set of keys pressed and check for user input
    pressed_keys = pygame.key.get_pressed()

    # Update the player sprite based on user keypresses
    maila.paivita(pressed_keys, pallo)
    pallo.paivita(pressed_keys, maila, palikat)

    # Fill the screen
    naytto.fill(TAUSTA_VARI)

    # draw the field
    pygame.draw.rect(naytto, REUNA_VARI, (0, 0, REUNA_LEVEYS, NAYTTO_KORKEUS), border_radius=REUNA_LEVEYS)
    pygame.draw.rect(naytto, REUNA_VARI, (0, 0, PELIKENTTA_LEVEYS + REUNA_LEVEYS, REUNA_LEVEYS), border_radius=REUNA_LEVEYS)
    pygame.draw.rect(naytto, REUNA_VARI, (PELIKENTTA_LEVEYS + REUNA_LEVEYS, 0, REUNA_LEVEYS, NAYTTO_KORKEUS), border_radius=REUNA_LEVEYS)

    # Draw all sprites
    for objekti in kaikki_objektit:
        naytto.blit(objekti.surf, objekti.rect)

    # Draw score text
    score_text.paivita("Score: " + str(pallo.score))
    naytto.blit(score_text.surf, score_text.rect)

    # Update the display
    pygame.display.flip()

    # if ball falls down -> game over
    if pallo.rect.bottom > NAYTTO_KORKEUS:
        maila.kill()
        pallo.kill()
        for palikka in palikat:
            palikka.kill()
        running = False

    # Ensure program maintains a rate of 30 frames per second
    kello.tick(30)
