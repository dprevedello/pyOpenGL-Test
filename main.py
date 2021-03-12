import sys
import traceback

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


def triangolo():
	glPushMatrix()

	glBegin(GL_TRIANGLES)
	glColor3f( 1, 0, 0 )
	glVertex3f( -1, -1, 0 )
	glColor3f( 0, 0, 1 )
	glVertex3f( 1, -1, 0 )
	glColor3f( 0, 1, 0 )
	glVertex3f( 0, 1, 0 )
	glEnd()

	glPopMatrix()


animation_angle = 0
def disegna(zoom, rotx, roty, animate):
	glClearColor(0,0,0,1);
	glClear(GL_COLOR_BUFFER_BIT)

	glLoadIdentity()
	glPushMatrix()

	glTranslatef(0, 0, zoom)
	glTranslatef(0, 0, -5)
	glRotatef(-rotx, 1, 0, 0)
	glRotatef(-roty, 0, 1, 0)

	global animation_angle
	glRotatef(animation_angle, 0, 1, 0)
	if animate:
		animation_angle += 1

	triangolo()
	glPopMatrix()

	pygame.display.flip()


def main():
	pygame.init()
	display = (500, 500)
	screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

	glMatrixMode(GL_PROJECTION)
	gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

	glEnable(GL_CULL_FACE)
	glCullFace(GL_BACK)

	glMatrixMode(GL_MODELVIEW)
	zoom = 0
	old_x, old_y, rotx, roty = 0,0,0,0;
	dragging = False
	animate = False
	clock = pygame.time.Clock()
	while True:
		for event in pygame.event.get():
			# Uscita dal programma
			if event.type == pygame.QUIT:
				return
			if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
				return
			if event.type == pygame.KEYUP and event.unicode == 'q':
				return

			# Zoom in
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
				zoom += 1
			if event.type == pygame.KEYDOWN and event.key == pygame.K_PLUS:
				zoom += 0.5

			# Zoom out
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
				zoom -= 1
			if event.type == pygame.KEYDOWN and event.key == pygame.K_MINUS:
				zoom -= 0.5

			# Rotazioni del modello
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				dragging = True
				old_x, old_y = event.pos
			if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				dragging = False
			if event.type == pygame.MOUSEMOTION:
				if dragging:
					rotx = rotx - (event.pos[1] - old_y)
					roty = roty - (event.pos[0] - old_x)
					old_x = event.pos[0]
					old_y = event.pos[1]

			# Animazione
			if event.type == pygame.KEYUP and event.unicode == 'a':
				animate = not animate

			# Attivazione full screen
			if event.type == pygame.KEYUP and event.unicode == 'f':
				pygame.display.toggle_fullscreen()

			# Azione all'evento di resize della schermata
			if event.type == pygame.VIDEORESIZE:
				glMatrixMode(GL_PROJECTION)
				glLoadIdentity()
				gluPerspective(45, float(event.w)/event.h, 0.1, 50.0)
				glMatrixMode(GL_MODELVIEW)

		disegna(zoom, rotx, roty, animate)
		clock.tick(30)


if __name__ == "__main__":
	try:
		main()
	except:
		traceback.print_exc()
	finally:
		pygame.quit()
		sys.exit()
