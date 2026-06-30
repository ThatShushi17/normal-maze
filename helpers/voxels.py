def from_face_idx(i: int):
	return i // 2, i % 2  # voxel coord, is_high

# None => check both
def check_face_solid(face_1, face_2, is2=None):
	faces = [face_1, face_2]
	if is2 is not None:
		return faces[is2] != 0
	else:
		return face_1 != 0 or face_2 != 0