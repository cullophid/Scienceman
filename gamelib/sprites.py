#! /usr/bin/env python

import pygame, random, math
from pygame.locals import *
from pygame.color import *
import pymunk

from data import *
import math

TOP_SIDE	= 0
BOTTOM_SIDE = 2
LEFT_SIDE	= 3
RIGHT_SIDE	= 1

def to_pymunk():
	return (p[0],480-p[1])

def speed_to_side(dx,dy):
	if abs(dx) > abs(dy):
		dy = 0
	else:
		dx = 0
	if dy < 0:
		return 0
	elif dx > 0:
		return 1
	elif dy > 0:
		return 2
	elif dx < 0:
		return 3
	else:
		return 0, 0
	
class Collidable(pygame.sprite.Sprite):

	def __init__(self, *groups):
		pygame.sprite.Sprite.__init__(self, groups)
		self.collision_groups = []
		self.xoffset = 0
		self.yoffset = 0

	def collide(self, group):
		if group not in self.collision_groups:
			self.collision_groups.append(group)

	def move(self, dx, dy, collide=True):
		if collide:
			if dx!=0:
				dx, dummy = self.__move(dx,0)
			if dy!=0:
				dummy, dy = self.__move(0,dy)
		else:
			self.rect.move_ip(dx, dy)
		return dx, dy

	def clamp_off(self, sprite, side):
		if side == TOP_SIDE:
			self.rect.top = sprite.rect.bottom
		if side == RIGHT_SIDE:
			self.rect.right = sprite.rect.left
		if side == BOTTOM_SIDE:
			self.rect.bottom = sprite.rect.top
		if side == LEFT_SIDE:
			self.rect.left = sprite.rect.right



		for group in self.collision_groups:
			for spr in group:
				if spr.rect.colliderect(self.rect):
					self.on_collision(side, spr, group)

		return self.rect.left-oldr.left,self.rect.top-oldr.top

	#def on_collision(self, side, sprite, group):
	#	self.clamp_off(sprite, side)

	def draw(self, surf):
		surf.blit(self.image, (self.rect[0]+self.xoffset, self.rect[1]+self.yoffset))

class Player(Collidable):

	def __init__(self, pos):
		Collidable.__init__(self, self.groups)
		self.left_images = []
		for i in self.right_images:
			self.left_images.append(pygame.transform.flip(i, 1, 0))
		self.image = self.right_images[0]
		self.rect = self.image.get_rect()
		self.jump_speed = 0
		self.jump_accel = 0.3
		self.jumping = False
		self.frame = 0
		self.facing = 1
		self.still_timer = 0
		self.hit_timer = 0
		self.health = 5
		self.heat = 100
		
		w = self.rect.width/2 - 20
		h = self.rect.height/2 - 10
		
		poly = [(-w,-h),(w,-h),(w,h),(-w,h)]
		mass = 1000
		moment = pymunk.moment_for_poly(mass, poly)
		self.body = pymunk.Body(mass, pymunk.inf)
		
		self.shape = pymunk.Poly(self.body, poly)
		self.shape.color = THECOLORS["blue"]
		self.shape.friction = 3
		
		self.rect.topleft = pos
		self.body.position = (self.rect.center[0],480-self.rect.center[1])
		self.jumping = False

	def damage(self, damage):
		self.health -= damage

	def kill(self):
		#pygame.mixer.music.stop()
		pygame.sprite.Sprite.kill(self)
		

	def on_collision(self, side, sprite, group):
		pass
#		self.clamp_off(sprite, side)
#		if side == TOP_SIDE:
#			self.jump_speed = 0
#		if side == BOTTOM_SIDE:
#			self.jump_speed = 0
#			self.jumping = False
#			self.springing = False
			
			
	def hit(self):
		if self.hit_timer <= 0:
			self.hit_timer = 20
			self.health -= 1
			if self.health <= 0:
				self.kill()
			
			
	def jump(self):
		if not self.jumping:
			self.jumping = True
			self.shape.body.apply_impulse((0,600000))
	
	def landed(self):
		self.jumping = False

	def move(self, dx):
		limit = 800
		#accelerate movement, iff. not exceeding max speed in that direction... allows for braking when over the limit
		if (dx > 0 and self.body.velocity[0] < limit) or (dx < 0 and self.body.velocity[0] > -limit):
			#self.body.velocity[0] += 100*dx
			self.body.apply_impulse((40000*dx,0))
			if self.body.velocity[0] > limit:
				self.body.velocity[0] = limit
			elif self.body.velocity[0] < -limit:
				self.body.velocity[0] = -limit
				

	def update(self):
		self.frame += 1
		self.still_timer -= 1
		self.hit_timer -= 1
		dx = 0
		key = pygame.key.get_pressed()			
		
		if self.still_timer <= 0:
			if key[K_LEFT] or key[K_a]:
				dx = -1
				self.facing = dx
			if key[K_RIGHT] or key[K_d]:
				dx = 1
				self.facing = dx

		if self.facing > 0:
			self.image = self.right_images[0]
		if self.facing < 0:
			self.image = self.left_images[0]
		if dx > 0:
			self.image = self.right_images[1+self.frame/8%6]
		if dx < 0:
			self.image = self.left_images[1+self.frame/8%6]
		if self.facing > 0 and self.jumping:
			self.image = self.right_images[1]
		if self.facing < 0 and self.jumping:
			self.image = self.left_images[1]
		if self.hit_timer > 0:
			if not self.frame % 2:
				if self.facing > 0:
					self.image = self.right_images[2]
				if self.facing < 0:
					self.image = self.left_images[2]

		if self.rect.left < 0:
			self.rect.left = 0
		if self.rect.top >= 475:
			pygame.sprite.Sprite.kill(self)
		
		self.move(dx)
				
	def push(self, space, pos):
		self.forcePower(pos, 20000, 100, 800, space)
		pass
		
	def pull(self, space, pos):
		self.forcePower(pos, -8000, 100, 600, space)
		pass

	def forcePower(self, pos, force, width, dist, space):
		origo = self.body.position
		direction = (pos-origo).normalized()
		
		p5 = origo + dist*direction
		p1 = origo + direction.rotated(90)*width/2
		p2 = origo + direction.rotated(-90)*width/2
		p3 = p1 + dist*direction
		p4 = p2 + dist*direction
		poly = (p1, p3, p4, p2, p1)
		for shape in space.shapes:
			if shape == self.shape:
				continue
			
			if self.point_inside_polygon(shape.body.position, poly):
				shape.body.apply_impulse(direction*force)

	def gravityWell(self, crates, pos):
		for shape in crates:
			shape.body.reset_forces()
			if shape == self.shape:
				continue
			shape.body.velocity *= 0.99
			shape.body.apply_force(self.gravity(shape, pos, 10))

	def gravity(self, shape, pos, force):
		a = 200.0
		c = 0.001
		
		f = shape.body.mass * force * max(a - c * pos.get_dist_sqrd(shape.body.position), 0)
		return (pos - shape.body.position).normalized() * f

	def gravityWellEnd(self, space):
		for shape in space.shapes:
			shape.body.reset_forces()

	def point_inside_polygon(self, point, poly):
		"""Shameless copy of utility function.
		Checks of a point is inside a closed polygon"""
		n = len(poly)
		x, y = point
		inside = False
		
		p1x,p1y = poly[0]
		for i in range(n+1):
			p2x,p2y = poly[i % n]
			if y > min(p1y,p2y):
				if y <= max(p1y,p2y):
					if x <= max(p1x,p2x):
						if p1y != p2y:
							xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
						if p1x == p2x or x <= xinters:
							inside = not inside
			p1x,p1y = p2x,p2y
			p1x,p1y = p2x,p2y
		return inside	

class Platform(Collidable):
	def __init__(self, pos, tile):
		Collidable.__init__(self, self.groups)
		self.image = self.images["platform-%s.png" % tile]
		self.rect = self.image.get_rect()
		self.body = pymunk.Body(pymunk.inf,pymunk.inf)
		w = self.rect.w/2
		h = self.rect.h/2
		self.shape = pymunk.Poly(self.body,[(-w,-h),(w,-h),(w,h),(-w,h)])
		self.shape.friction = 0.5
		self.rect.topleft = pos
		self.body.position = (self.rect.center[0],480-self.rect.center[1])

class Crate(Collidable):
	def __init__(self, pos, size):
		Collidable.__init__(self, self.groups)
		self.image = load_image("crate1.png")
		self.rect = self.image.get_rect()
		mass = 10
		inertia = pymunk.moment_for_poly(mass, [self.rect.topleft,self.rect.topright,self.rect.bottomright,self.rect.bottomleft])
		self.body = pymunk.Body(mass,inertia)
		w = self.rect.w/2
		h = self.rect.h/2
		self.shape= pymunk.Poly(self.body,[(-w,-h),(w,-h),(w,h),(-w,h)])
		self.shape.friction = 1
		self.rect.topleft = pos
		self.body.position = (self.rect.center[0],480-self.rect.center[1])
		#print self.shape.body.position
		
		
class Badguy(Collidable):
	def __init__(self, pos):
		self.left_images = []
		self.left_draw_images = []
		for i in self.right_images:
			self.left_images.append(pygame.transform.flip(i, 1, 0))
		for i in self.right_draw_images:
			self.left_draw_images.append(pygame.transform.flip(i,1,0))
		Collidable.__init__(self, self.groups)
		self.image = self.left_images[0]
		self.health = 100
		self.frame = 0
		self.dead = False
		self.alert = False
		
		self.rect = self.image.get_rect()
		mass = 100
		inertia = pymunk.moment_for_poly(mass, [self.rect.topleft,self.rect.topright,self.rect.bottomright,self.rect.bottomleft])
		self.body = pymunk.Body(mass, pymunk.inf)
		w = self.rect.w/2
		h = self.rect.h/2 -10
		self.shape= pymunk.Poly(self.body,[(-w,-h),(w,-h),(w,h),(-w,h)])
		self.shape.friction = 0.5
		self.rect.topleft = pos
		self.body.position = (self.rect.center[0],480-self.rect.center[1])
	
	def damage(self, damage):
		self.health -= damage
		print damage, self.health
		if self.health <=0:
			self.dead = True
		
	def update(self):
		if self.frame <= 32:
			if self.rect.topleft[0] > self.player.rect.topleft[0]:
				self.image = self.left_draw_images[self.frame/8]
			else:
				self.image = self.right_draw_images[self.frame/8]
		else:	
			if self.rect.topleft[0] > self.player.rect.topleft[0]:
				self.image = self.left_images[0]
				if not self.frame % 100:
					Bullet((self.rect.topleft[0],self.rect.topleft[1]+15))
			else:
				self.image = self.right_images[0]
				if not self.frame % 100:
					Bullet((self.rect.topright[0],self.rect.topright[1]+15))
		self.frame +=1
	
		
		
		
class Bullet(Collidable):
	def __init__(self, pos):
		Collidable.__init__(self,self.groups)
		self.image = self.images[0]
		self.rect = self.image.get_rect(topleft=pos)
		self.x,self.y=self.rect.center
		self.frame =0
		x = self.x - self.player.rect.centerx
		y = self.y - self.player.rect.centery	
		angle = math.atan2(y, x)
		self.angle = int(270.0 - (angle * 180) / math.pi)
		
	def update(self):
		self.image = self.images[self.frame%2]
		self.rect.center = (self.x,self.y)
		speed = 6
		self.x += math.sin(math.radians(self.angle))*speed
		self.y += math.cos(math.radians(self.angle))*speed
		self.frame +=1
		
		
		
			
		
		
