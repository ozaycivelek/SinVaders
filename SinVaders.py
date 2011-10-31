#!/usr/bin/env python
# encoding: utf-8
"""
space_invaders.py

Created by Ozay Civelek on 2011-10-29.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import pygame
import random
import math
import sys
import time

screen_resolution = [1024,768]
screen = pygame.display.set_mode(screen_resolution, pygame.FULLSCREEN, 32)
pygame.display.set_caption("SinVaders")
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

SHIP = 1
ALIEN = 2


SCORE = 0
LIVES = 3

class space_ship(object):
	
	def __init__(self):
		self.center = [screen_resolution[0]/2, screen_resolution[1] - 100]
		self.sliding = False
		self.last_fire = time.time()
		self.min_time_to_fire_again = 0.1
		self.alive = True
		self.collide_mask = [(-20, -20), (20, -20), (20, 20), (-20, 20)]
		self.velocity = 8
	
	def draw(self):
		if self.alive:
			pygame.draw.polygon(screen,[255, 255, 255], self.get_poly_dots())
		
	def get_poly_dots(self):
		if self.sliding:
			dots = [
					(0,-20),
					(15,20),
					(-15,20),
					]
		else:
			dots = [
					(0,-20),
					(20,20),
					(-20,20),
					]
		
		my_points = []
		
		for dot in dots:
			my_points.append((dot[0] + self.center[0], dot[1] + self.center[1]))
		
		return my_points
	
	def can_fire(self):
		now = time.time()
		delta = now - self.last_fire
		if self.alive and delta >= self.min_time_to_fire_again:
			self.last_fire = time.time()
			return True
		else:
			return False
		
	def handle_keys(self, keys):
		old_vel = self.velocity
		if keys[pygame.K_LEFT]:
			self.move(-1* self.velocity, 0)
			self.sliding = True
			self.velocity += 1
		if keys[pygame.K_UP]:
			self.move(0, -1*self.velocity)
			self.velocity += 1
		if keys[pygame.K_DOWN]:
			self.move(0, self.velocity)
			self.velocity += 1
		if keys[pygame.K_RIGHT]:
			self.sliding = True
			self.move(self.velocity, 0)
			self.velocity += 1
		if old_vel == self.velocity:
			self.velocity = 8
		if self.velocity > 16:
			self.velocity = 16
		
		if keys[pygame.K_SPACE] and self.can_fire():
			return [self.center[0], self.center[1]]
		
		return False
	
	def move(self, x, y):
		self.center[0] += x
		self.center[1] += y
		if self.center[0] > screen_resolution[0] - 20:
			self.center[0] = screen_resolution[0] - 20
		if self.center[1] > screen_resolution[1] - 30:
			self.center[1] = screen_resolution[1] - 30
		if self.center[0] < 60:
			self.center[0] = 60
		if self.center[1] < 60:
			self.center[1] = 60

class star(object):
	def __init__(self, x, y, size, color):
		self.x = x
		self.y = y
		self.color = color
		self.size = size
		self.active = True
		self.velocity = random.randrange(1,5)
	
	def move(self):
		self.y += self.velocity
		if self.y > screen_resolution[1] - 40:
			self.active = False
	
	def draw(self):
		pygame.draw.circle(screen,self.color,(self.x, self.y),self.size)
		
		

class background(object):
	def __init__(self, object_count):
		self.objects = []
		while object_count > 0:
			self.objects.append(self.make_object(inscreen=True))
			object_count -= 1
	
	def make_object(self, inscreen=False):
		if not inscreen:
			star_x = random.randrange(50, screen_resolution[0] - 90)
			star_y = 0
		else:
			star_x = random.randrange(50, screen_resolution[0] - 90)
			star_y = random.randrange(50, screen_resolution[1] - 90)
		
		star_size = random.randrange(1, 3)
		if random.randrange(0,1000) == 42:
			star_size = random.randrange(10, 50)
			
		color = random.randrange(30, 220)
		return star(star_x, star_y, star_size,[color,color,color])
	
	def draw(self):
		
		new_objects = []
		for obj in self.objects:
			obj.move()
			if obj.active:
				new_objects.append(obj)
				obj.draw()
			else:
				new_objects.append(self.make_object())
		
		self.objects = new_objects

class borders(object):
	def __init__(self):
		pass
	
	def draw(self):
		top = pygame.Rect(0,0,screen_resolution[0], 40)
		bottom = pygame.Rect(0, screen_resolution[0] - 40, screen_resolution[0], 40)
		left_pane = pygame.Rect(0,40,40, screen_resolution[1] - 80)
		right_pane = pygame.Rect(screen_resolution[0] - 40,40,40, screen_resolution[1] - 80)
		pygame.draw.rect(screen, [0,0,0], top)
		pygame.draw.rect(screen, [0,0,0], bottom)
		pygame.draw.rect(screen, [0,0,0], left_pane)
		pygame.draw.rect(screen, [0,0,0], right_pane)
		bounds = pygame.Rect(40,40,screen_resolution[0] - 40, screen_resolution[1] - 40)		
		pygame.draw.rect(screen, [255,100,60], bounds, 3)

class missle(object):
	def __init__(self, center, owner):
		self.active = True
		self.center = center
		# mock for screen objects
		self.fired = False
		self.owner = owner
		self.collide_mask = [(-1, -7), (1, -7), (-1, 7), (1, 7)]
		if self.owner == SHIP:
			self.move_y = -10
			self.color = [255,0,0]
		else:
			self.move_y = 10
			self.color = [255,255,0]
			self.score = 10
	
	def draw(self):
		pygame.draw.line(screen, self.color ,self.center, (self.center[0], self.center[1] - 14), 2)
	
	def move(self, ship):
		self.center[1] += self.move_y
		
		if self.center[1] < 0 and self.owner == SHIP:
			self.active = False
		if self.center[1] > screen_resolution[1] - 40 and self.owner == ALIEN:
			self.active = False
	

class alien(object):
	def __init__(self):
		self.owner = ALIEN
		self.active = True
		self.center = [random.randrange(40, screen_resolution[1] - 40), 0]
		self.move_y = 5
		self.velocity = 6
		self.color = [40,255,40]
		self.last_fire = time.time()
		self.min_time_to_fire_again = 2
		self.fired = False
		self.collide_mask = [(-5, -5), (5, -5), (5, -5), (5, 5)]
		self.score = 50
	
	def draw(self):
		pygame.draw.circle(screen,self.color,self.center,10)
	
	def move(self, ship):
		self.center[1] += self.move_y
		delta = self.center[0] - ship.center[0]
		if delta != 0:
			self.center[0] -= self.velocity if delta > 0 else -1*self.velocity
		
		if  time.time() - self.last_fire  >= self.min_time_to_fire_again:
			self.fired = True
			self.last_fire = time.time()

		if self.center[1] > screen_resolution[1] - 40:
			self.active = False


class alien_satellite(object):
	def __init__(self):
		self.owner = ALIEN
		self.active = True
		self.side = random.randrange(0,2)
		if self.side == 1: # LEFT to RIGHT
			self.center = [0, random.randrange(40, screen_resolution[1] - 40)]
			self.move_x = 5
		else:
			self.center = [screen_resolution[0] - 40, random.randrange(40, screen_resolution[1] - 40)]
			self.move_x = -5
		self.velocity = 2
		self.color = [180,10,130]
		self.last_fire = time.time()
		self.min_time_to_fire_again = 2
		self.fired = False
		self.collide_mask = [(-5, -5), (5, -5), (5, -5), (5, 5)]
		self.score = 150
		self.last_positions = []

	def draw(self):
		pygame.draw.circle(screen,[50,50,50],self.center,12)
		pygame.draw.circle(screen,self.color,self.center,10)


	def move(self, ship):
		self.center[0] += self.move_x
		if self.center[1] < ship.center[1] - 100:
			self.center[1] += self.velocity*5
		if self.center[1] > ship.center[1] - 100:
			self.center[1] -= self.velocity*5
	
		delta = self.center[0] - ship.center[0]
		if delta != 0:
			self.center[0] -= self.velocity if delta > 0 else -1*self.velocity

		if  time.time() - self.last_fire  >= self.min_time_to_fire_again:
			self.fired = True
			self.last_fire = time.time()

		if self.center[0] > screen_resolution[0] - 40:
			self.active = False

class explosion(object):
	
	def __init__(self, center):
		self.owner = None
		self.active = True
		self.center = center
		self.color = [255,255,0]
		self.radius = 1
		self.fired = False
		
	def draw(self):
		if self.active:
			pygame.draw.circle(screen, self.color, self.center, self.radius, 1)
			if self.radius > 10:
				pygame.draw.circle(screen, self.color, self.center, self.radius - 8)
		
	def move(self, ship):
		self.radius += 1
		self.color[1] -= 10
		self.color[0] -= 5
		if self.radius > 25:
			self.active = False


def darken_screen():
	global SCORE
	
	darken = pygame.Surface(pygame.display.get_surface().get_size())
	darken.fill((0,0,0))
	darken_factor = 64
	while darken_factor < 100:
		darken.set_alpha(darken_factor)
		screen.blit(darken, (0,0))
		pygame.display.flip()
		darken_factor += 5
		clock.tick(20)
		
	print "SCORE : ", SCORE
	sys.exit()

def is_point_in_rectangle(point, rectangle):
	if point[0] >= rectangle[0][0] and point[0] <= rectangle[1][0] and point[1] >= rectangle[0][1] and point[1] <= rectangle[3][1]:
		return True
	else:
		return False
	

def check_collision(screen_objects, ship):
	
	global SCORE
	
	ship_corners = [(x + ship.center[0],y + ship.center[1]) for x,y in ship.collide_mask]
	for obj in screen_objects:
		if obj.owner == ALIEN:
			alien_corners = [(x + obj.center[0],y + obj.center[1]) for x,y in obj.collide_mask]
			for point in alien_corners:
				if is_point_in_rectangle(point, ship_corners):
					ship.alive = False
					screen_objects.append(explosion(ship.center))
					darken_screen()
		
		if obj.owner == SHIP:
			obj_corners = [(x + obj.center[0],y + obj.center[1]) for x,y in obj.collide_mask]
			for point in obj_corners:
				for alien_object in screen_objects:
					if alien_object.owner == ALIEN:
						alien_object_corners = [(x + alien_object.center[0],y + alien_object.center[1]) for x,y in alien_object.collide_mask]
						if is_point_in_rectangle(point, alien_object_corners):
							SCORE += alien_object.score
							alien_object.active = False
							screen_objects.append(explosion(alien_object.center))
	return screen_objects		
		
def main():
	global SCORE
	
	pygame.init()
	black = [ 0, 0, 0]
	ship = space_ship()
	bg = background(100)
	border = borders()
	screen_objects = []
	done=False
	while done==False:
		
		for event in pygame.event.get(): # User did something
			if event.type == pygame.QUIT: # If user clicked close
				done=True # Flag that we are done so we exit this loop
			if event.type == pygame.KEYUP:
				ship.sliding = False
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit()
			
		keys = pygame.key.get_pressed()
		fired = ship.handle_keys(keys)
		if fired != False:
			screen_objects.append(missle(fired, SHIP))
		
		screen_objects = check_collision(screen_objects,ship)
		# Set the screen background
		screen.fill(black)
		bg.draw()
		
		score_factor = int(SCORE + 1 / 1000)
		if random.randrange(0, max(200 - score_factor, 10)) == 9:
			screen_objects.append(alien())
		if SCORE > 5000:
			if random.randrange(0, max(700 - score_factor * 4, 100)) == 99:
				screen_objects.append(alien_satellite())
		
		if len(screen_objects):
			new_objects = []
			for obj in screen_objects:
				obj.move(ship)
				if obj.fired:
					obj.fired = False
					new_objects.append(missle([obj.center[0], obj.center[1]], ALIEN))
					
				if obj.active:
					new_objects.append(obj)
					obj.draw()

			screen_objects = new_objects
		
		border.draw()
		ship.draw()
		# Go ahead and update the screen with what we've drawn.
		pygame.display.flip()
		clock.tick(20)

if __name__ == '__main__':
	main()

