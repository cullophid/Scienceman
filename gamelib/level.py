#! /usr/bin/env python

import pygame
from pygame.locals import *

from data import *
from sprites import *

class Level:

	def __init__(self,lvl=1):
		self.level = pygame.image.load(filepath(("lvl%d.png" % lvl))).convert()
		self.x = 0
		self.y = 0
		for y in range(self.level.get_height()):
			self.y = y
			for x in range(self.level.get_width()):
				self.x = x
				color = self.level.get_at((self.x, self.y))
				if color == (255,255,255,255):
					pass
				elif color == (0, 0, 0, 255):
					l=r=False
					tile = "middle"
					if self.get_at(0, -1) != (0, 0, 0, 255):
						tile = "top"
					if self.get_at(-1, 0) != (0, 0, 0, 255):
						l=True
					if self.get_at(1, 0) != (0, 0, 0, 255):
						r=True
					Platform((self.x*32, self.y*32), tile)
				elif color == (210, 210, 210, 255):
					Crate((self.x*32,self.y*32), "small")
				elif color == (255, 0, 0, 255):
					Badguy((self.x*32,self.y*32))	
				elif color == (153, 79, 0 ,255):
					Crate((self.x*32,self.y*32), "medium")
				else:
					print color
		
		print "level loaded"
				   
	def get_at(self, dx, dy):
		try:
			return self.level.get_at((self.x+dx, self.y+dy))
		except:
			pass
			
	def get_size(self):
		return [self.level.get_size()[0]*32, self.level.get_size()[1]*32]
