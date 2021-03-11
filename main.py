import sys
import traceback

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


def disegna():
	glClearColor(1,0,0,1); # R=1 G=0 B=0 A=1
	glClear(GL_COLOR_BUFFER_BIT)
	pygame.display.flip()


def main():
	pygame.init()
	display = (500, 500)
	screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
			if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
				return
			if event.type == pygame.KEYUP and event.unicode == 'q':
				return

		disegna()


if __name__ == "__main__":
	try:
		main()
	except:
		traceback.print_exc()
	finally:
		pygame.quit()
		sys.exit()