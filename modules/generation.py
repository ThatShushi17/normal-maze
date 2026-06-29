import numpy as np
from helpers.data import get_nybble, pack_nybbles
from helpers.voxels import from_face_idx
from enum import IntEnum

class FaceType(IntEnum):
	EMPTY = 0

	WALL_GREY = 1
	WALL_RED = 2
	WALL_GREEN = 3
	WALL_BLUE = 4

def generate_wall(room, data, main_axis, face_i, size_u, size_v, start_u, start_v):
	vox_dist, is_high = from_face_idx(face_i)
	end_u, end_v = start_u + size_u, start_u + size_v
	output = data << 4 if is_high else data  # TEMPORARY
	if main_axis == 0:
		room[start_v:end_u, start_u:end_u, vox_dist, main_axis] = output
	elif main_axis == 1:
		room[start_v:end_u, vox_dist, start_u:end_u, main_axis] = output
	elif main_axis == 2:
		room[vox_dist, start_v:end_u, start_u:end_u, main_axis] = output

def generate_blank_room(room_id, size_x=32, size_y=32, size_z=32):
	grid = np.zeros((size_z, size_y, size_x, 4), dtype=np.uint8)

	# flush alphas to be room_id, TEMPORARY
	grid[..., 3] = room_id

	low_byte = pack_nybbles(FaceType.EMPTY, FaceType.WALL_GREY)
	high_byte = pack_nybbles(FaceType.WALL_GREY, FaceType.EMPTY)


	# yz walls
	generate_wall(grid, FaceType.WALL_RED, 0, 0, 32, 32, 0, 0)            # low
	grid[:, :, -1, 0] = pack_nybbles(FaceType.WALL_RED, FaceType.EMPTY)   # high

	# xz walls
	grid[:, 0, :, 1] = pack_nybbles(FaceType.EMPTY, FaceType.WALL_GREEN)  # low
	grid[:, -1, :, 1] = pack_nybbles(FaceType.WALL_BLUE, FaceType.EMPTY)  # high

	# xy walls
	grid[0, :, :, 2] = pack_nybbles(FaceType.EMPTY, FaceType.WALL_GREY)   # low
	grid[-1, :, :, 2] = pack_nybbles(FaceType.WALL_GREY, FaceType.EMPTY)  # high

	return grid