import numpy as np
from helpers.voxels import from_face_idx
from enum import IntEnum
from helpers.bytes import pack_byte, pack_bytes

class FaceType(IntEnum):
	EMPTY = pack_byte(0, 0, 0, 0)

	WALL_GREY = pack_byte(1, 0, 0, 0)
	WALL_RED = pack_byte(1, 0, 0, 4)
	WALL_GREEN = pack_byte(1, 0, 0, 8)
	WALL_BLUE = pack_byte(1, 0, 0, 12)

def generate_wall(room, data, main_axis, face_i, size_u, size_v, start_u, start_v):
	vox_dist, is_high = from_face_idx(face_i)
	end_u, end_v = start_u + size_u, start_u + size_v
	output = data << 4 if is_high else data  # TEMPORARY
	if main_axis == 0:
		room[start_v:end_v, start_u:end_u, vox_dist, main_axis] = output
	elif main_axis == 1:
		room[start_v:end_v, vox_dist, start_u:end_u, main_axis] = output
	elif main_axis == 2:
		room[vox_dist, start_v:end_v, start_u:end_u, main_axis] = output

def generate_blank_room(room_id, size_x=32, size_y=32, size_z=32):
	grid = np.zeros((size_z, size_y, size_x, 4), dtype=np.uint16)

	# flush alphas to be room_id, TEMPORARY
	grid[..., 3] = room_id

	# yz walls
	grid[:, :,  0, 0] = pack_bytes(FaceType.EMPTY, FaceType.WALL_RED)    # low
	grid[:, :, -1, 0] = pack_bytes(FaceType.WALL_RED, FaceType.EMPTY)    # high

	# xz walls
	grid[:,  0, :, 1] = pack_bytes(FaceType.EMPTY, FaceType.WALL_GREEN)  # low
	grid[:, -1, :, 1] = pack_bytes(FaceType.WALL_BLUE, FaceType.EMPTY)   # high

	# xy walls
	grid[ 0, :, :, 2] = pack_bytes(FaceType.EMPTY, FaceType.WALL_GREY)   # low
	grid[-1, :, :, 2] = pack_bytes(FaceType.WALL_GREY, FaceType.EMPTY)   # high

	return grid