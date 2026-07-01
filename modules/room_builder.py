import numpy as np
from helpers.data import find_uv_axes
from helpers.voxels import from_face_idx

class RoomBuilder:
	def __init__(self) -> None:
		self.room = None
		self._wall_queue = []

	def _wall(self, room, data, axis, vox_dist, is_high, size_u, size_v, start_u, start_v):
		end_u, end_v = start_u + size_u, start_v + size_v

		mask = 0xFF if is_high else 0xFF00
		insert = data << 8 if is_high else data

		mask, insert = np.uint16(mask), np.uint16(insert)

		if axis == 0:
			room[start_v:end_v, start_u:end_u, vox_dist, axis] &= mask
			room[start_v:end_v, start_u:end_u, vox_dist, axis] |= insert

		elif axis == 1:
			room[start_v:end_v, vox_dist, start_u:end_u, axis] &= mask
			room[start_v:end_v, vox_dist, start_u:end_u, axis] |= insert

		elif axis == 2:
			room[vox_dist, start_v:end_v, start_u:end_u, axis] &= mask
			room[vox_dist, start_v:end_v, start_u:end_u, axis] |= insert

	def create_room(self, size_x=32, size_y=32, size_z=32):
		return np.zeros((size_z, size_y, size_x, 4), dtype=np.uint16)

	def bind_room(self, room):
		self.room = room

	def wall(self, data, axis, face_i, size_u, size_v, start_u, start_v):
		vox_dist, is_high = from_face_idx(face_i)
		self._wall_queue.append(lambda: self._wall(self.room, data, axis, vox_dist, is_high, size_u, size_v, start_u, start_v))

	def box(self, face_pos, face_size, faces):
		for axis in range(3):
			axis_u, axis_v = find_uv_axes(axis)

			face_start_dist, face_end_dist = face_pos[axis], face_pos[axis] + face_size[axis]

			start_is_high = face_start_dist % 2
			end_is_high = face_end_dist % 2

			face_size_u, face_size_v = face_size[axis_u], face_size[axis_v]
			face_start_u, face_start_v = face_pos[axis_u], face_pos[axis_v]

			start_u, start_v = face_start_u // 2, face_start_v // 2
			size_u, size_v = face_size_u // 2, face_size_v // 2

			self.wall(faces[axis, start_is_high], axis, face_start_dist, size_u, size_v, start_u, start_v)
			self.wall(faces[axis, end_is_high], axis, face_end_dist, size_u, size_v, start_u, start_v)


	def build(self):
		for f in self._wall_queue:
			f()