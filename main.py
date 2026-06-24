import pygame
import sys
import moderngl
import numpy as np
from modules.player import Player
from modules.geometry import Rect

WIDTH, HEIGHT = 800, 600

# --- initialising pygame stuff --- #

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
clock = pygame.time.Clock()

# --- initialising mgl stuff --- #

ctx = moderngl.create_context()
pygame_surf = pygame.Surface((WIDTH, HEIGHT))

quad_verts = np.array([
	-1.0,  1.0, 0.0, 1.0,
	-1.0, -1.0, 0.0, 0.0,
	 1.0,  1.0, 1.0, 1.0,
	 1.0, -1.0, 1.0, 0.0,
], dtype='f4')

with open('shaders/vert.glsl') as f:
	vert_src = f.read()
with open('shaders/frag.glsl') as f:
	frag_src = f.read()

program = ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)

vbo = ctx.buffer(quad_verts.tobytes())
vao = ctx.vertex_array(program, [
	(vbo, '2f 2f', 'in_vert', 'in_texcoord')
])

tex = ctx.texture((WIDTH, HEIGHT), 4)
tex.filter = (moderngl.NEAREST, moderngl.NEAREST)

# --- initialising game stuff --- #

player = Player(WIDTH // 2, HEIGHT // 2, 0, 3, 3)
walls = [
	Rect(250, 150, 0, 100, 100)
]

# --- main loop --- #

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	keys = pygame.key.get_pressed()

	player.update(keys)

	pygame_surf.fill((20, 20, 20))

	for wall in walls:
		wall.draw(pygame_surf)

	player.draw(pygame_surf)

	surf_data = pygame.image.tostring(pygame_surf, 'RGBA', False)
	tex.write(surf_data)

	ctx.clear(0.0, 0.0, 0.0, 1.0)

	tex.use(0)
	program['u_tex'] = 0
	vao.render(moderngl.TRIANGLE_STRIP)

	pygame.display.flip()
	clock.tick(60)