import pygame
import sys
import moderngl
import numpy as np
from modules.player import Player
from modules.voxels import generate_blank_room

WIDTH, HEIGHT = 800, 600

def main():
	# --- initialising pygame stuff --- #

	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
	clock = pygame.time.Clock()

	# pygame.mouse.set_visible(False)
	# pygame.event.set_grab(True)

	# --- initialising mgl stuff --- #

	ctx = moderngl.create_context()

	quad_verts = np.array([
		-1.0,  1.0, 0.0, 1.0,
		-1.0, -1.0, 0.0, 0.0,
		 1.0,  1.0, 1.0, 1.0,
		 1.0, -1.0, 1.0, 0.0,
	], dtype='f4')

	with open('shaders/vert.glsl') as f: vert_src = f.read()
	with open('shaders/frag.glsl') as f: frag_src = f.read()
	with open('shaders/dda.glsl') as f: comp_src = f.read()

	program = ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)
	compute_shader = ctx.compute_shader(comp_src)

	vbo = ctx.buffer(quad_verts.tobytes())
	vao = ctx.vertex_array(program, [
		(vbo, '2f 2f', 'in_vert', 'in_texcoord')
	])

	tex = ctx.texture((WIDTH, HEIGHT), 4)
	tex.filter = (moderngl.NEAREST, moderngl.NEAREST)

	# --- initialising game stuff --- #

	player = Player(2.0, 2.0, 2, 0, 0, 0.2, 3)
	room = generate_blank_room(0)
	tex_room = ctx.texture3d((32, 32, 32), 4, room.tobytes(), dtype='f1')
	tex_room.filter = (moderngl.NEAREST, moderngl.NEAREST)

	# --- main loop --- #

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

		keys = pygame.key.get_pressed()
		m_dx, m_dy = pygame.mouse.get_rel()

		player.update(keys, m_dx, m_dy, room)

		# --- compute shader stuff --- #

		tex.bind_to_image(0, read=False, write=True)
		tex_room.use(1)
		compute_shader['u_voxel_grid'] = 1

		compute_shader['u_cam_pos'] = tuple(player.pos)
		compute_shader['u_cam_forward'] = tuple(player.forward)
		compute_shader['u_cam_up'] = tuple(player.up)
		compute_shader['u_cam_right'] = tuple(player.right)

		compute_shader.run(int(np.ceil(WIDTH / 8)), int(np.ceil(HEIGHT / 8)))

		ctx.clear()
		tex.use(0)
		program['u_tex'] = 0
		vao.render(moderngl.TRIANGLE_STRIP)

		pygame.display.flip()
		clock.tick(60)


if __name__ == "__main__":
	main()