import numpy as np
from helpers.data import pack_nybbles
from enum import IntEnum

class FaceType(IntEnum):
	EMPTY = 0

	WALL_GREY = 1
	WALL_RED = 2
	WALL_GREEN = 3
	WALL_BLUE = 4

def generate_blank_room(room_id, size_x=32, size_y=32, size_z=32):
	grid = np.zeros((size_z, size_y, size_x, 4), dtype=np.uint8)

	# flush alphas to be room_id, temporary
	grid[..., 3] = room_id

	low_byte = pack_nybbles(FaceType.EMPTY, FaceType.WALL_GREY)
	high_byte = pack_nybbles(FaceType.WALL_GREY, FaceType.EMPTY)

	# yz walls
	grid[:, :, 0, 0] = pack_nybbles(FaceType.EMPTY, FaceType.WALL_RED)    # low
	grid[:, :, -1, 0] = pack_nybbles(FaceType.WALL_RED, FaceType.EMPTY)   # high

	# xz walls
	grid[:, 0, :, 1] = pack_nybbles(FaceType.EMPTY, FaceType.WALL_GREEN)  # low
	grid[:, -1, :, 1] = pack_nybbles(FaceType.WALL_BLUE, FaceType.EMPTY)  # high

	# xy walls
	grid[0, :, :, 2] = pack_nybbles(FaceType.EMPTY, FaceType.WALL_GREY)   # low
	grid[-1, :, :, 2] = pack_nybbles(FaceType.WALL_GREY, FaceType.EMPTY)  # high

	return grid