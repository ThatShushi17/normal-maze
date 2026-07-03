import pygame
import sys
import moderngl
import numpy as np
import math

from engine.world import Player, RoomBuilder, FaceSet

# from engine.world.entities.player import Player
# from engine.world.generation.room_builder import RoomBuilder
# from engine.world.face import FaceSet
from engine.math.bytes import pack_byte
from enum import IntEnum

WIDTH, HEIGHT = 800, 600

colors = np.zeros((16, 3), dtype=np.float32)
colors[0] = (0.5, 0.5, 0.5)
colors[1] = (0.7, 0.2, 0.2)
colors[2] = (0.2, 0.7, 0.2)
colors[3] = (0.2, 0.2, 0.7)

class FaceType(IntEnum):
	EMPTY = pack_byte(0, 0, 0, 0)

	WALL_GREY = pack_byte(1, 0, 0, 0)
	WALL_RED = pack_byte(1, 0, 0, 1)
	WALL_GREEN = pack_byte(1, 0, 0, 2)
	WALL_BLUE = pack_byte(1, 0, 0, 3)
	WALL_ANIM = pack_byte(1, 0, 0, 4)

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

	with open('engine/render/shaders/vert.glsl') as f: vert_src = f.read()
	with open('engine/render/shaders/frag.glsl') as f: frag_src = f.read()
	with open('engine/render/shaders/dda.glsl') as f: comp_src = f.read()

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

	builder = RoomBuilder()
	room = builder.create_room()
	builder.bind_room(room)
	builder.box(
		pos=(0, 0, 0),
		size=(32, 32, 32),
		faces=FaceSet.matching(
			face_x=FaceType.WALL_RED,
			face_y=FaceType.WALL_GREEN,
			face_z=FaceType.WALL_ANIM,
		)
	)
	builder.build()

	tex_room = ctx.texture3d((32, 32, 32), 4, room.tobytes(), dtype='u2')
	tex_room.filter = (moderngl.NEAREST, moderngl.NEAREST)

	# --- main loop --- #

	running = True
	while running:
		dt = clock.tick(60) / 1000.0
		t = pygame.time.get_ticks() / 1000.0

		colors[4] = (1.0, 0.0, 0.0) if int(t) % 2 == 0 else (0.0, 1.0, 0.0)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False

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

		compute_shader['u_palette'].write(colors.copy().tobytes())

		compute_shader.run(int(np.ceil(WIDTH / 8)), int(np.ceil(HEIGHT / 8)))

		ctx.clear()
		tex.use(0)
		program['u_tex'] = 0
		vao.render(moderngl.TRIANGLE_STRIP)

		pygame.display.flip()

	print("exiting")

	tex.release()
	tex_room.release()
	vbo.release()
	vao.release()
	program.release()
	compute_shader.release()

	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()