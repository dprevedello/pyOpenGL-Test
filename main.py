import sys
import traceback

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


def triangolo():
	glPushMatrix()

	glRotatef(10, 0, 0, 1)
	glScalef(0.7, 0.5, 1)
	glTranslatef(0, 0, -1.0)
	glTranslatef(0, 0.5, 0)

	glBegin(GL_TRIANGLES)
	glColor3f( 1, 0, 0 )
	glVertex3f( -1, -1, 0 )
	glColor3f( 0, 1, 0 )
	glVertex3f( 0, 1, 0 )
	glColor3f( 0, 0, 1 )
	glVertex3f( 1, -1, 0 )
	glEnd()

	glPopMatrix()


def disegna(zoom):
	glClearColor(0,0,0,1);
	glClear(GL_COLOR_BUFFER_BIT)
	
	glLoadIdentity()

	glPushMatrix()
	glTranslatef(0, 0, zoom)

	triangolo()
	glPopMatrix()

	pygame.display.flip()


def main():
	pygame.init()
	display = (500, 500)
	screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

	glMatrixMode(GL_PROJECTION)
	gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
	
	glMatrixMode(GL_MODELVIEW)
	zoom = 0;
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
			if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
				return
			if event.type == pygame.KEYUP and event.unicode == 'q':
				return

			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
				zoom+=1
			if event.type == pygame.KEYDOWN and event.key == pygame.K_PLUS:
				zoom+=0.5
				
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
				zoom-=1
			if event.type == pygame.KEYDOWN and event.key == pygame.K_MINUS:
				zoom-=0.5

		disegna(zoom)


if __name__ == "__main__":
	try:
		main()
	except:
		traceback.print_exc()
	finally:
		pygame.quit()
		sys.exit()
