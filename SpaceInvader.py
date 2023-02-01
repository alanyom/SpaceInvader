#############################################################################
# Alan Yom                                                                  #
# Mr. Millard                                                               #
# 11 AP CSP                                                                 #
# Jan 27, 2023                                                              #
# SpaceInvader                                                              #
# This code creates a spaceinvadergame in pygames however the twist is that #
# instead of traditional left and right movements, the player is able to 	#
# move forward and backwards. There are also multiple waves of aliens once  #
# all of them are cleared from the screen and finally, when the player 		#
# presses r, a shield is summoned which stays in place, blocking all alien  #
# bullets, but disappears after 5 seconds						            #
#############################################################################


import pygame
from pygame import mixer
from pygame.locals import *
import random


pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()



#create sprite groups
shield_group = pygame.sprite.Group()
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


#define fps
clock = pygame.time.Clock()
fps = 60


screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invanders')


#define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)


#load sounds
explosion_fx = pygame.mixer.Sound("img/img_explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("img/img_explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("img/img_laser.wav")
laser_fx.set_volume(0.25)


#define game variables
defaultSize = (150, 150)
rows = 5
cols = 5
alien_cooldown = 800#bullet cooldown in milliseconds
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0#0 is no game over, 1 means player has won, -1 means player has lost

#define colours
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)



#load image
bg = pygame.image.load("img/bg.png")

def draw_bg():
	screen.blit(bg, (0, 0))


#define function for creating text
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


#create spaceship class 
class Spaceship(pygame.sprite.Sprite):
	def __init__(self, x, y, health):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/spaceship.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.health_start = health
		self.health_remaining = health
		self.last_shot = pygame.time.get_ticks()
		self.last_shield = pygame.time.get_ticks()


	def update(self):
		#set movement speed
		speed = 7
		#set a cooldown variable
		cooldown = 100 #milliseconds
		shield_cooldown = 7500 
		game_over = 0


		#get key press
		key = pygame.key.get_pressed()
		if key[pygame.K_a] and self.rect.left > 0:
			self.rect.x -= speed
		if key[pygame.K_d] and self.rect.right < screen_width:
			self.rect.x += speed
		if key[pygame.K_w] and self.rect.top > 0:
			self.rect.y -= speed
		if key[pygame.K_s] and self.rect.bottom < screen_height:
			self.rect.y += speed

		#record current time
		time_now = pygame.time.get_ticks()
		shield_time = pygame.time.get_ticks()
		#shoot
		if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
			laser_fx.play()
			bullet = Bullets(self.rect.centerx, self.rect.top)
			bullet_group.add(bullet)
			self.last_shot = time_now

		#r summons a shield every 5000 milliseconds
		if key[pygame.K_r] and shield_time - self.last_shield > shield_cooldown:
			shield = Shield(self.rect.centerx, self.rect.centery)
			shield_group.add(shield)
			self.last_shield = shield_time



		#update mask
		self.mask = pygame.mask.from_surface(self.image)


		#draw health bar
		pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
		if self.health_remaining > 0:
			pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
		elif self.health_remaining <= 0:
			explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
			explosion_group.add(explosion)
			self.kill()
			game_over = -1
		return game_over



#create Bullets class
class Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/bullet.png")

		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y -= 5
		if self.rect.bottom < 0:
			self.kill()
		if pygame.sprite.spritecollide(self, alien_group, True):
			self.kill()
			explosion_fx.play()
			explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
			explosion_group.add(explosion)




#create Aliens class
class Aliens(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/alien" + str(random.randint(1, 5)) + ".png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.move_counter = 0
		self.move_direction = 1

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 75:
			self.move_direction *= -1
			self.move_counter *= self.move_direction



#create Alien Bullets class
class Alien_Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/alien_bullet.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y += 2
		if self.rect.top > screen_height:
			self.kill()
		if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
			self.kill()
			explosion2_fx.play()
			#reduce spaceship health
			spaceship.health_remaining -= 1
			explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
			explosion_group.add(explosion)
		if pygame.sprite.spritecollide(self, shield_group, False, pygame.sprite.collide_mask):
			self.kill()
			explosion2_fx.play()
			explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
			explosion_group.add(explosion)




#create Explosion class
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, size):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f"img/exp{num}.png")
			if size == 1:
				img = pygame.transform.scale(img, (20, 20))
			if size == 2:
				img = pygame.transform.scale(img, (40, 40))
			if size == 3:
				img = pygame.transform.scale(img, (160, 160))
			#add the image to the list
			self.images.append(img)
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.counter = 0


	def update(self):
		explosion_speed = 3
		#update explosion animation
		self.counter += 1

		if self.counter >= explosion_speed and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]

		#if the animation is complete, delete explosion
		if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
			self.kill()

#create Shield class
class Shield(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/shield.png")
		self.image = pygame.transform.scale(self.image, defaultSize)
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.create_time = pygame.time.get_ticks()

	#shield disappears automatically in 5 seconds
	def update(self):
		if pygame.time.get_ticks() - self.create_time > 5000:
 			shield_group.remove(self)

# ... existing code ...


def create_aliens():
	#generate aliens
	for row in range(rows):
		for item in range(cols):
			alien = Aliens(75 + item * 100, 75 + row * 75)
			alien_group.add(alien)

create_aliens()


#create player
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)



run = True
while run:

	clock.tick(fps)

	#draw background
	draw_bg()


	if countdown == 0:
		#create random alien bullets
		#record current time
		time_now = pygame.time.get_ticks()
		#shoot
		if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
			attacking_alien = random.choice(alien_group.sprites())
			alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
			alien_bullet_group.add(alien_bullet)
			last_alien_shot = time_now

		#check if all the aliens have been killed
		if len(alien_group) == 0:
			#if all aliens are killed, summon new wave
			create_aliens()

		if game_over == 0:
			#update spaceship
			game_over = spaceship.update()

			#update sprite groups
			bullet_group.update()
			alien_group.update()
			alien_bullet_group.update()
		else:
			if game_over == -1:
				draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
			if game_over == 1:
				draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))

	if countdown > 0:
		draw_text('GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
		draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
		count_timer = pygame.time.get_ticks()
		if count_timer - last_count > 1000:
			countdown -= 1
			last_count = count_timer


	#update explosion group	
	explosion_group.update()
	shield_group.update()


	#draw sprite groups
	spaceship_group.draw(screen)
	shield_group.draw(screen)
	bullet_group.draw(screen)
	alien_group.draw(screen)
	alien_bullet_group.draw(screen)
	explosion_group.draw(screen)


	#event handlers
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False


	pygame.display.update()

pygame.quit()