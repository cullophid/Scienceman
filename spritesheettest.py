import sys, os
import pygame
from pygame.locals import *
from pygame.color import *
from gamelib import data
class Spritesheet:
	def __init__(self, filename):
		self.sheet = pygame.image.load(os.path.join('data',filename)).convert()
	def imgat(self,rect,colorkey=None):
		rect = Rect(rect)
		image = pygame.Surface(rect.size).convert()
		image.blit(self.sheet, (0,0),rect)
		if colorkey is not None:
			if colorkey is -1:
				colorkey = image.get_at((0,0))
				image.set_colorkey(colorkey, RLEACCEL)
		return image
	def imgsat(self,rects,colorkey=None):
		imgs = []
		for rect in rects:
			imgs.append(self.imgat(rect, colorkey))
		return imgs


os.environ["SDL_VIDEO_CENTERED"] = "1"
#pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()
pygame.mouse.set_visible(1)

pygame.display.set_caption("In the name of Science")
screen = pygame.display.set_mode((1000, 480))
font = pygame.font.Font((os.path.join('data','font.ttf')), 16)
ren = font.render("YOU DIED!", 1, (255, 255, 255))
screen.blit(ren, (320-ren.get_width()/2, 235))
sheet = Spritesheet("CaptainCommando.gif")
image = sheet.imgat((14,6,64,86),-1)
while True:
	for e in pygame.event.get():
		if e.type == QUIT:
			sys.exit()
		if e.type == KEYDOWN:
			if e.key == K_ESCAPE:
				self.end()
		
		ren = font.render("YOU DIED!", 1, (255, 255, 255))
		screen.blit(ren, (320-ren.get_width()/2, 235))
		screen.blit(image,(100,100))
		pygame.display.flip()
		
		
