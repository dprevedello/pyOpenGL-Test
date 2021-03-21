import sys
import traceback
import numpy as np
import glm
import cv2

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from pywavefront import Wavefront


vertex_shader = """
#version 330 core

// Dati in input, variabili per ciascun vertice
layout(location = 0) in vec3 vertexPosition_modelspace;
layout(location = 1) in vec2 vertexUVcoords;

// Dati in output, interpolati per ciascun frammento
out vec2 UV;

// Valori passati allo shader che rimangono costanti
uniform mat4 MVP;

void main(){
	// Calcolo della posizione del vertice in clip space: MVP * position
	gl_Position =  MVP * vec4(vertexPosition_modelspace, 1);

	// Coordinate UV del vertice.
	UV = vertexUVcoords;
}
"""

fragment_shader = """
#version 330 core

// Valori interpolati forniti dal vertex shader
in vec2 UV;

// Dati in output
out vec3 color;

// Valori costanti per tutta l'esecuzione
uniform sampler2D textureSampler;

void main(){
	color = texture2D( textureSampler, UV ).rgb;
}
"""


def compile_shaders():
	# create program
	program = glCreateProgram()

	# vertex shader
	vs = glCreateShader(GL_VERTEX_SHADER)
	glShaderSource(vs, vertex_shader)
	glCompileShader(vs)
	if GL_TRUE != glGetShaderiv(vs, GL_COMPILE_STATUS):
		raise Exception(glGetShaderInfoLog(vs))
	glAttachShader(program, vs)

	# fragment shader
	fs = glCreateShader(GL_FRAGMENT_SHADER)
	glShaderSource(fs, fragment_shader)
	glCompileShader(fs)
	if GL_TRUE != glGetShaderiv(vs, GL_COMPILE_STATUS) :
		raise Exception(glGetShaderInfoLog(vs))
	glAttachShader(program, fs)

	glLinkProgram(program)
	if GL_TRUE != glGetProgramiv(program, GL_LINK_STATUS):
		raise Exception(glGetProgramInfoLog(program))

	MVP_ID = glGetUniformLocation(program, "MVP")
	TS_ID = glGetUniformLocation(program, "textureSampler")

	return {'shader':program, 'MVP':MVP_ID, 'sampler':TS_ID}


def carica_mesh(path, texture_path):
	shader = compile_shaders()

	mesh = Wavefront(path)
	print(mesh.mesh_list[0].materials[0].vertex_format)

	data = np.array([])
	for m_item in mesh.mesh_list:
		for mat in m_item.materials:
			data = np.append(data, mat.vertices)
	dim = len(data)//8
	data = data.reshape(dim, 8).astype(np.float32)
	vertici = data[:,5:8].reshape(-1)
	texel = data[:,0:2].reshape(-1)

	vertex_bufferId = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, vertex_bufferId)
	glBufferData(GL_ARRAY_BUFFER, 4*len(vertici), vertici, GL_STATIC_DRAW)

	texel_bufferId = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, texel_bufferId)
	glBufferData(GL_ARRAY_BUFFER, 4*len(texel), texel, GL_STATIC_DRAW)

	texture = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D, texture)
	img = cv2.flip(cv2.imread(texture_path), 0)
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.shape[1], img.shape[0], 0, GL_BGR, GL_UNSIGNED_BYTE, img.data)
	glGenerateMipmap(GL_TEXTURE_2D)

	glBindBuffer(GL_ARRAY_BUFFER, 0)
	glBindTexture(GL_TEXTURE_2D, 0)

	identity = glm.mat4(1.0)

	return shader | {'v':vertex_bufferId, 't':texel_bufferId, 'texture':texture,
					 'type':GL_TRIANGLES, 'n_triangoli':dim, 'model_m':identity}


def libera_risorse_mesh(mesh):
	glDeleteBuffers(1, mesh['v'])
	glDeleteBuffers(1, mesh['t'])
	glDeleteTexture(1, mesh['texture'])


animation_angle = 0
def disegna(zoom, rotx, roty, animate, view_m, proj_m, mesh):
	glClearColor(0,0,0,1)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	MVP = proj_m * view_m
	MVP = glm.translate(MVP, glm.vec3(0, 0, -5+zoom))
	MVP = glm.rotate(MVP, glm.radians(-rotx), glm.vec3(1, 0, 0))
	MVP = glm.rotate(MVP, glm.radians(-roty), glm.vec3(0, 1, 0))

	global animation_angle
	MVP = glm.rotate(MVP, glm.radians(animation_angle), glm.vec3(0, 1, 0))
	if animate:
		animation_angle += 1
	MVP = MVP * mesh['model_m']

	glUseProgram(mesh['shader'])
	glUniformMatrix4fv(mesh['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))

	glEnableVertexAttribArray(0)
	glBindBuffer(GL_ARRAY_BUFFER, mesh['v'])
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

	glEnableVertexAttribArray(1)
	glBindBuffer(GL_ARRAY_BUFFER, mesh['t'])
	glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

	glUniform1i(mesh['sampler'], 0)
	glBindTexture(GL_TEXTURE_2D, mesh['texture'])
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

	glDrawArrays(mesh['type'], 0, mesh['n_triangoli']*3)

	glDisableVertexAttribArray(0)
	glDisableVertexAttribArray(1)

	glUseProgram(0)
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	glBindTexture(GL_TEXTURE_2D, 0)

	pygame.display.flip()


def main():
	pygame.init()
	display = (500, 500)
	screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

	proj_m = glm.perspective(glm.radians(45), display[0]/display[1], 0.1, 50.0)
	view_m = glm.lookAt(glm.vec3(0,0,0), # Camera is at (0,0,0), in World Space
						glm.vec3(0,0,-1), #and looks at the (0.0.0))
						glm.vec3(0,1,0) ) #Head is up (set to 0,-1,0 to look upside-down)

	glEnable(GL_CULL_FACE)
	glCullFace(GL_BACK)
	glEnable(GL_DEPTH_TEST)

	mesh = carica_mesh('./mesh/earth.obj', './mesh/earthmap.2k.jpg')

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
				proj_m = glm.perspective(glm.radians(45), float(event.w)/event.h, 0.1, 50.0)

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

		disegna(zoom, rotx, roty, animate, view_m, proj_m, mesh)
		clock.tick(30)
	libera_risorse_mesh(mesh)


if __name__ == "__main__":
	try:
		main()
	except:
		traceback.print_exc()
	finally:
		pygame.quit()
		sys.exit()
