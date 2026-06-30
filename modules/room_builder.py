from helpers.voxels import from_face_idx

class RoomBuilder:
	def __init__(self) -> None:
		pass

	def wall(self, room, data, axis, face_i, size_u, size_v, start_u, start_v):
		vox_dist, is_high = from_face_idx(face_i)
		end_u, end_v = start_u + size_u, start_u + size_v
		output = data << 4 if is_high else data  # TEMPORARY
		if axis == 0:
			room[start_v:end_u, start_u:end_u, vox_dist, axis] = output
		elif axis == 1:
			room[start_v:end_u, vox_dist, start_u:end_u, axis] = output
		elif axis == 2:
			room[vox_dist, start_v:end_u, start_u:end_u, axis] = output