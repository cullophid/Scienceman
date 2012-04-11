'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''
#stolen direcly from mr. fuze
import os, pygame
from pygame.locals import *

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))

def filepath(filename):
	'''Determine the path to a file in the data directory.
	'''
	return os.path.join(data_dir, filename)

def load(filename, mode='rb'):
	'''Open a file in the data directory.

	"mode" is passed as the second arg to open().
	'''
	return open(os.path.join(data_dir, filename), mode)

def load_image(filename):
	filename = filepath(filename)
	try:
		image = pygame.image.load(filename)
		image = pygame.transform.scale(image, (image.get_width()*2, image.get_height()*2))
		image.set_colorkey((255, 115,220,255))
	except pygame.error:
		raise SystemExit, "Unable to load: " + filename
	return image.convert_alpha()

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


