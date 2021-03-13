import sys
import traceback
import numpy as np

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


def toFloat(array):
	return np.array(array, dtype='float32')


def triangolo():
	vertici = [-1, -1, 0,
				1, -1, 0,
				0,	1, 0]
	colori = [1, 0, 0,
			  0, 0, 1,
			  0, 1, 0]

	vertex_bufferId = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, vertex_bufferId)
	glBufferData(GL_ARRAY_BUFFER, 4*len(vertici), toFloat(vertici), GL_STATIC_DRAW)
	glFinish()
	glVertexPointer(3, GL_FLOAT, 0, None )

	color_bufferId = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, color_bufferId)
	glBufferData(GL_ARRAY_BUFFER, 4*len(colori), toFloat(colori), GL_STATIC_DRAW)
	glFinish()
	glColorPointer(3, GL_FLOAT, 0, None )

	glBindBuffer(GL_ARRAY_BUFFER, 0)

	glEnableClientState(GL_VERTEX_ARRAY);
	glEnableClientState(GL_COLOR_ARRAY);


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

	glPushMatrix()
	glTranslatef(-1, 0, 0)
	glDrawArrays(GL_TRIANGLES, 0, 3);
	glPopMatrix()

	glPushMatrix()
	glTranslatef(1, 0, 0)
	glDrawArrays(GL_TRIANGLES, 0, 3);
	glPopMatrix()

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

	triangolo()

	glMatrixMode(GL_MODELVIEW)
	zoom = 0
	old_x, old_y, rotx, roty = 0,0,0,0;
	dragging = False
	animate = False
	clock = pygame.time.Clock()
	wireframe = False
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

			# Attivazione wireframe
			if event.type == pygame.KEYUP and event.unicode == 'w':
				if wireframe:
					glPolygonMode( GL_FRONT_AND_BACK, GL_FILL );
				else:
					glPolygonMode( GL_FRONT_AND_BACK, GL_LINE );
				wireframe = not wireframe

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
