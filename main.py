import sys
import traceback
import numpy as np

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


def genera_cubo():
	vertici = np.array([[ 1, -1, -1], [ 1,	1, -1], [-1,  1, -1], [-1, -1, -1],
						[ 1, -1,  1], [ 1,	1,	1], [-1, -1,  1], [-1,	1,	1]], dtype='float32')

	colori = np.array([[0,1,0], [0,0,1], [1,0,0], [1,1,1]], dtype='float32')

	superfici = np.array([[3,2,1,0], [6,7,2,3], [4,5,7,6],
						  [0,1,5,4], [2,7,5,1], [6,3,0,4]]).reshape(-1)

	vbo1 = vertici[superfici].reshape(-1)
	vbo2 = np.tile(colori, (6, 1)).reshape(-1)

	vertex_bufferId = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, vertex_bufferId)
	glBufferData(GL_ARRAY_BUFFER, 4*len(vbo1), vbo1, GL_STATIC_DRAW)

	color_bufferId = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, color_bufferId)
	glBufferData(GL_ARRAY_BUFFER, 4*len(vbo2), vbo2, GL_STATIC_DRAW)

	glBindBuffer(GL_ARRAY_BUFFER, 0)

	return {'v':vertex_bufferId, 'c':color_bufferId, 'type':GL_QUADS, 'len':len(superfici)}


def disegna_mesh(mesh, colore=None):
	glEnableClientState(GL_VERTEX_ARRAY)
	if colore is None:
		glEnableClientState(GL_COLOR_ARRAY)

	glBindBuffer(GL_ARRAY_BUFFER, mesh['v'])
	glVertexPointer(3, GL_FLOAT, 0, None )
	if colore is None:
		glBindBuffer(GL_ARRAY_BUFFER, mesh['c'])
		glColorPointer(3, GL_FLOAT, 0, None )
	glBindBuffer(GL_ARRAY_BUFFER, 0)

	if colore is not None:
		glColor3fv(colore)
	glDrawArrays(mesh['type'], 0, mesh['len'])

	glDisableClientState(GL_VERTEX_ARRAY)
	if colore is None:
		glDisableClientState(GL_COLOR_ARRAY)


animation_angle = 0
def disegna(zoom, rotx, roty, animate, wireframe, mesh):
	glClearColor(0,0,0,1)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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

	disegna_mesh(mesh)
	glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
	disegna_mesh(mesh, [1,1,1])
	if not wireframe:
		glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

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
	glEnable(GL_DEPTH_TEST)

	mesh = genera_cubo()

	glMatrixMode(GL_MODELVIEW)
	zoom = 0
	old_x, old_y, rotx, roty = 0,0,0,0
	dragging = False
	animate = False
	clock = pygame.time.Clock()
	wireframe = False
	culling = True
	dept_test = True
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
					glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )
				else:
					glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
				wireframe = not wireframe

			# Attivazione culling
			if event.type == pygame.KEYUP and event.unicode == 'c':
				if culling:
					glDisable(GL_CULL_FACE)
				else:
					glEnable(GL_CULL_FACE)
				culling = not culling

			# Attivazione dept test
			if event.type == pygame.KEYUP and event.unicode == 'd':
				if dept_test:
					glDisable(GL_DEPTH_TEST)
				else:
					glEnable(GL_DEPTH_TEST)
				dept_test = not dept_test

		disegna(zoom, rotx, roty, animate, wireframe, mesh)
		clock.tick(30)


if __name__ == "__main__":
	try:
		main()
	except:
		traceback.print_exc()
	finally:
		pygame.quit()
		sys.exit()
