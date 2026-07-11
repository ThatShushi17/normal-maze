import os
from glm import axis
import pygame
import sys
import moderngl
import numpy as np
import math

from PIL import Image
import imageio

from engine.world import Player, RoomBuilder
from engine.math import Palette, pack_byte, generate_wall_data, FaceSet, FacePos

WIDTH, HEIGHT = 800, 608

palette = Palette()

palette[0] = (0.5, 0.5, 0.5)
palette[1] = (0.7, 0.2, 0.2)
palette[2] = (0.2, 0.7, 0.2)
palette[3] = (0.2, 0.2, 0.7)
palette[4] = (0.2, 0.7, 0.7)
palette[5] = (0.7, 0.2, 0.7)
palette[6] = (0.7, 0.7, 0.2)

palette.set_name(0, "grey")
palette.set_name(1, "red")
palette.set_name(2, "green")
palette.set_name(3, "blue")
palette.set_name(4, "cyan")
palette.set_name(5, "magenta")
palette.set_name(6, "yellow")
palette.set_name(7, "anim")


def screenshot(ctx, dirname="screenshots"):
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	current_filecount = len(os.listdir(dirname))
	filename = f"screenshot_{current_filecount + 1}.png"
	path = os.path.join(dirname, filename)

	img_data = ctx.screen.read(components=3)
	image = Image.frombytes("RGB", (WIDTH, HEIGHT), img_data)
	image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

	image.save(path)
	print(f"saved screenshot to: {path}")


def main():
	# --- initialising pygame stuff --- #

	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
	clock = pygame.time.Clock()

	pygame.mouse.set_visible(False)
	pygame.event.set_grab(True)

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

	# --- initialising media stuff --- #

	screenshot_taken = False
	recording = False
	video_writer = None
	record_pressed = False

	# --- initialising game stuff --- #


	# player = Player(2.0, 2.0, 2, 0, 0, 0.2, 3)
	player = Player(1.0, 1.0, 8.4, 0.0, 0.0, 0.1, 3.0)

	builder = RoomBuilder()
	room = builder.create_room()
	builder.bind_room(room)

	builder.box(
		pos=(0, 0, 0),
		size=(10, 10, 10),
		faces=FaceSet.matching(
			face_x=generate_wall_data(1, palette.get_id("red")),
			face_y=generate_wall_data(1, palette.get_id("green")),
			face_z=generate_wall_data(0, palette.get_id("grey")),
		)
	)
	builder.box(
		pos=(10, 0, 3),
		size=(10, 10, 7),
		faces=FaceSet.matching(
			face_x=generate_wall_data(1, palette.get_id("magenta")),
			face_y=generate_wall_data(1, palette.get_id("blue")),
			face_z=generate_wall_data(0, palette.get_id("yellow")),
		)
	)
	builder.box(
		pos=(4, 4, 7),
		size=(3, 3, 3),
		faces=FaceSet.matching(
			face_x=generate_wall_data(1, palette.get_id("grey")),
			face_y=generate_wall_data(1, palette.get_id("grey")),
			face_z=generate_wall_data(0, palette.get_id("grey")),
		)
	)
	builder.linked_portals(
		in_face_pos=FacePos(
			axis=0,
			face_i=7,
			start_u=5,
			start_v=8
		),
		out_face_pos=FacePos(
			axis=0,
			face_i=27,
			start_u=5,
			start_v=8
		),
		size_u=1,
		size_v=2,
	)

	builder.build()

	portal_buffer = ctx.buffer(builder.serialize_portal_data())
	portal_buffer.bind_to_storage_buffer(2)

	tex_room = ctx.texture3d((32, 32, 32), 4, room.tobytes(), dtype='u2')
	tex_room.filter = (moderngl.NEAREST, moderngl.NEAREST)

	# --- main loop --- #

	running = True
	while running:
		dt = clock.tick(60) / 1000.0
		t = pygame.time.get_ticks() / 1000.0

		palette[4] = (math.sin(t) * 2 + 1, 0.0, 0.0)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False

				if event.key == pygame.K_F12 and not screenshot_taken:
					screenshot(ctx)
					screenshot_taken = True

				if event.key == pygame.K_F11 and not record_pressed:
					record_pressed = True
					recording = not recording

					if recording:
						print("start recording")
						video_writer = imageio.get_writer("capture.mp4", fps=60, codec="libx264")

					else:
						print("stop recording")
						if video_writer is not None:
							video_writer.close()
							video_writer = None


			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_F12:
					screenshot_taken = False
				if event.key == pygame.K_F11:
					record_pressed = False

		keys = pygame.key.get_pressed()
		m_dx, m_dy = pygame.mouse.get_rel()

		player.update(keys, m_dx, m_dy, room)

		# --- compute shader stuff --- #

		tex.bind_to_image(0, read=False, write=True)
		tex_room.use(1)
		compute_shader['u_voxel_grid'] = 1

		compute_shader['u_cam_pos'] = tuple(player.pos)
		compute_shader['u_cam_forward'] = tuple(player.cam_forward)
		compute_shader['u_cam_up'] = tuple(player.up)
		compute_shader['u_cam_right'] = tuple(player.right)

		compute_shader['u_palette'].write(palette.tobytes())

		compute_shader.run(int(np.ceil(WIDTH / 8)), int(np.ceil(HEIGHT / 8)))

		ctx.clear()
		tex.use(0)
		program['u_tex'] = 0
		vao.render(moderngl.TRIANGLE_STRIP)

		if recording and video_writer is not None:
			img_data = ctx.screen.read(components=3)
			frame = np.frombuffer(img_data, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
			frame = np.flipud(frame)
			video_writer.append_data(frame)

		pygame.display.flip()

	print("exiting")

	tex.release()
	tex_room.release()
	vbo.release()
	vao.release()
	program.release()
	compute_shader.release()
	portal_buffer.release()

	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()
