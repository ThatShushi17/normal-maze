import numpy as np
from engine.math.geometry import find_uv_axes, from_face_idx, to_face_idx

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

	def box(self, pos, size, faces):
		for axis in range(3):
			axis_u, axis_v = find_uv_axes(axis)

			start_dist = pos[axis]
			end_dist = start_dist + size[axis] - 1
			start_u, start_v = pos[axis_u], pos[axis_v]
			size_u, size_v = size[axis_u], size[axis_v]

			face_start_dist = to_face_idx(start_dist, False)
			face_end_dist = to_face_idx(end_dist, True)

			self.wall(faces[axis, 0], axis, face_start_dist, size_u, size_v, start_u, start_v)
			self.wall(faces[axis, 1], axis, face_end_dist, size_u, size_v, start_u, start_v)

	def build(self):
		for f in self._wall_queue:
			f()