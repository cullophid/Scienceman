#! /usr/bin/env python

import sys, os
import random

import pygame
from pygame.locals import *
from pygame.color import *
import pymunk

from data import *
from sprites import *
from level import *

global globalPlayer, globalBaddies, globalCrates

def collision_handler(shapeA, shapeB, contacts, normal_coef, screen):
	global globalPlayer, globalBaddies, globalCrates

	#if shapeA or shapeB is player.shape, other will contain the colliding shape, else None
	other = (shapeA == globalPlayer.shape and shapeB) or (shapeB == globalPlayer.shape and shapeB) or None
	if other != None:
		globalPlayer.landed()

	baddie, other = (globalBaddies.has_key(shapeA) and (shapeA, shapeB)) or (globalBaddies.has_key(shapeB) and (shapeB, shapeA)) or (None, None)
	if baddie != None:
		impact = math.fabs(contacts[0].jn_acc)
		if impact > 5:
			globalBaddies[baddie].damage(2*impact)
			# "badguy hit"
			
			if other == globalPlayer.shape:
				print "by me"
			elif globalCrates.has_key(other):
				print "by object", other.body.position
			
	return True

def to_pygame(p):
	return (p.x,480-p.y)
	
def RelRect(actor, camera):
	return Rect(actor.rect.x-camera.rect.x, actor.rect.y-camera.rect.y, actor.rect.w, actor.rect.h)

class Camera(object):
	def __init__(self, player, width):
		self.player = player
		self.rect = pygame.display.get_surface().get_rect()
		self.world = Rect(0, 0, width, 480)
		self.rect.center = self.player.rect.center
	def update(self):
		if self.player.rect.centerx > self.rect.centerx+64:
			self.rect.centerx = self.player.rect.centerx-64
		if self.player.rect.centerx < self.rect.centerx-64:
			self.rect.centerx = self.player.rect.centerx+64
		if self.player.rect.centery > self.rect.centery+64:
			self.rect.centery = self.player.rect.centery-64
		if self.player.rect.centery < self.rect.centery-64:
			self.rect.centery = self.player.rect.centery+64
		self.rect.clamp_ip(self.world)
				
	def draw_platforms(self, surf, platforms):
		for p in platforms:
			p.rect.center = to_pygame(p.shape.body.position)
			if p.rect.colliderect(self.rect):
				surf.blit(p.image, RelRect(p, self))
				
	def draw_crates(self, surf, crates):
		for c in crates:
			c.rect.center = to_pygame(c.shape.body.position)
			if c.rect.colliderect(self.rect):
				image = pygame.transform.rotate(c.image,c.body.angle*180/math.pi)
				surf.blit(image, RelRect(c, self))
				
	def draw_player(self, surf, players):
		for p in players:
			p.rect.center = to_pygame(p.shape.body.position)
			if p.rect.colliderect(self.rect):
				surf.blit(p.image, RelRect(p, self))
				
	def draw_badguys(self, surf, badguys):
		for b in badguys:
			b.rect.center = to_pygame(b.body.position)
			if b.rect.colliderect(self.rect):
				if b.alert == False:
					b.alert = True
					b.frame = 0
				surf.blit(b.image, RelRect(b,self))
			elif b.alert == True:
				b.alert = False
	def draw_bullets(self, surf, bullets):
		for b in bullets:
			if b.rect.colliderect(self.rect):
				image = pygame.transform.rotate(b.image,90+b.angle)
				surf.blit(image, RelRect(b,self))
		
class Game(object):
	
	def __init__(self, screen, continuing=False):
		global globalPlayer, globalBaddies, globalCrates
		#set screen
		self.screen = screen
		#init pymunk
		pymunk.init_pymunk()
		self.space = pymunk.Space()
		self.space.gravity = (0.0, -900.0)
		self.space.set_default_collisionpair_func(collision_handler)
		self.sprites = pygame.sprite.OrderedUpdates()
		self.players = pygame.sprite.OrderedUpdates()
		self.platforms = pygame.sprite.OrderedUpdates()
		self.nomoveplatforms = pygame.sprite.OrderedUpdates()
		self.crates = pygame.sprite.OrderedUpdates()
		self.badguys = pygame.sprite.OrderedUpdates()
		self.bullets = pygame.sprite.OrderedUpdates()
		
		#init spritesheets
		self.playersheet = Spritesheet("CaptainCommando.gif")
		self.baddiesheet = Spritesheet("ultimate badguy.gif")
		#set images
		
		Player.right_images = [self.playersheet.imgat((14,6,64,86),-1),self.playersheet.imgat((8,103,64,86),-1),self.playersheet.imgat((71,103,93,76),-1),self.playersheet.imgat((166,103,64,75),-1),self.playersheet.imgat((233,103,56,77),-1),self.playersheet.imgat((289,103,79,77),-1),self.playersheet.imgat((372,103,63,77),-1) ]
		
		Badguy.right_images = [self.baddiesheet.imgat((373,1750,100,101),-1),load_image("badguy1.png"),load_image("badguy2.png"),load_image("badguy3.png"),load_image("badguy4.png") ]
		Badguy.right_draw_images = [self.baddiesheet.imgat((14,15,75,102),-1),self.baddiesheet.imgat((7,1750,92,101),-1),self.baddiesheet.imgat((98,1750,92,101),-1),self.baddiesheet.imgat((192,1750,92,101),-1),self.baddiesheet.imgat((281,1750,92,101),-1)]
		
		Platform.images = {"platform-top.png": load_image("platform-top.png"), "platform-middle.png": load_image("platform-middle.png")}
		Bullet.images = [load_image("bullet.png"),load_image("bullet2.png")]
		#set groups
		Player.groups = self.sprites, self.players
		Platform.groups = self.sprites, self.platforms, self.nomoveplatforms
		Crate.groups = self.sprites, self.crates
		Badguy.groups = self.sprites, self.badguys
		Bullet.groups = self.sprites, self.bullets

		self.lvl = 2
		if continuing:
			self.lvl = get_saved_level()
		self.player = Player((20, 200))
		self.clock = pygame.time.Clock()
		self.bg = load_image("bg4.png")
		self.level = Level(self.lvl)
		print "ADDING STUFF"
		self.space.add(self.player.body, self.player.shape)
		globalPlayer = self.player			
		for platform in self.platforms:
			self.space.add_static(platform.shape)
		globalCrates = {}
		for crate in self.crates:
			self.space.add(crate.body,crate.shape)
			globalCrates[crate.shape] = crate
		globalBaddies = {}
		for badguy in self.badguys:
			self.space.add(badguy.body,badguy.shape) 
			globalBaddies[badguy.shape] = badguy

		
		self.camera = Camera(self.player, self.level.get_size()[0])
		self.font = pygame.font.Font(filepath("font.ttf"), 16)
		self.heroimg = load_image("hero1.png")
		self.running = 1
		#self.music = "gameloop.ogg"
		
		
		#self.intro_level()
		self.main_loop()
		
	def end(self):
		self.running = 0
		
	
	
				
	def redo_level(self):
		self.running = False

		
	def show_death(self):
		ren = self.font.render("YOU DIED!", 1, (255, 255, 255))
		self.screen.blit(ren, (320-ren.get_width()/2, 235))
		pygame.display.flip()
		pygame.time.wait(2500)
		
	def show_win(self):
		ren = self.font.render("YOU KILLIFIED THEM ALL!", 1, (255, 255, 255))
		self.screen.blit(ren, (320-ren.get_width()/2, 235))
		pygame.display.flip()
		pygame.time.wait(2500)
			
	def clear_sprites(self):
		for s in self.sprites:
			pygame.sprite.Sprite.kill(s)

	def main_loop(self):

		while self.running:
			Bullet.player =self.player
			Badguy.player = self.player
			if not self.running:
				return
			

			self.clock.tick(60)
			self.camera.update()
			for s in self.sprites:
				s.update()
				
			#set collision groups
			#self.player.collide(self.platforms)
			
			for e in pygame.event.get():
				if e.type == QUIT:
					sys.exit()
				if e.type == KEYDOWN:
					if e.key == K_ESCAPE:
						self.end()
					if e.key == K_UP or e.key == K_w:
						self.player.jump()
					#add mouse buttons and physics powers here
					if e.key == K_x:
						#self.ball = Ball(self.space)
						pass
				if e.type == MOUSEBUTTONDOWN:
					pos = (e.pos[0] + self.camera.rect.x, 480 - e.pos[1])
					#print "mouse pressed", e.button
					if e.button == 1:
						self.player.push(self.space, pos)
					elif e.button == 3:
						self.player.pull(self.space, pos)
				if e.type == KEYUP:
					self.player.gravityWellEnd(self.space)
			
			if pygame.key.get_pressed()[K_LSHIFT]:
				p = pygame.mouse.get_pos()
				pos = pymunk.Vec2d(p[0] + self.camera.rect.x, 480 - p[1])
				self.player.gravityWell(self.crates, pos)
			
			self.space.step(1/100.0)
			alive = False
			for badguy in self.badguys:
				if badguy.body.position[1] < 0:
					badguy.dead = True
					
				if badguy.dead:
					self.space.remove(badguy.shape)
					for group in badguy.groups:
						group.remove(badguy)
				else:
					alive = True
					
			for b in self.bullets:
				if not b.rect.colliderect(self.camera.rect):
					b.kill()
				if b.rect.colliderect(self.player.rect):
					self.player.hit()
					b.kill()
				for c in self.crates:
					if b.rect.colliderect(c.rect):
						b.kill()
			
			
			if not self.running:
				return
			self.screen.blit(self.bg, ((-self.camera.rect.x/2)%640, 0))
			self.screen.blit(self.bg, ((-self.camera.rect.x/2)%640 + 640, 0))
			self.screen.blit(self.bg, ((-self.camera.rect.x/2)%640 - 640, 0))
			self.camera.draw_platforms(self.screen, self.platforms)
			self.camera.draw_crates(self.screen, self.crates)
			self.camera.draw_badguys(self.screen,self.badguys)
			self.camera.draw_player(self.screen, self.players)
			self.camera.draw_bullets(self.screen, self.bullets)


			if not self.player.alive():
				self.show_death()
				self.redo_level()
			if not alive:
				self.show_win()
				self.redo_level()
			pygame.display.flip()
			if not self.running:
				return

	
