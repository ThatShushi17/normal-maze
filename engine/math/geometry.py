def find_uv_axes(main_axis):
	if main_axis == 0:
		return 1, 2
	elif main_axis == 1:
		return 0, 2
	else:
		return 0, 1

def to_face_idx(vox_dist, is_high):
	return 2 * vox_dist + is_high

def from_face_idx(i: int):
	return i // 2, (i % 2) == 1  # vox_dist, is_high

# None => check both
def check_face_solid(face_1, face_2, is2=None):
	faces = [face_1, face_2]
	if is2 is not None:
		return faces[is2] != 0
	else:
		return face_1 != 0 or face_2 != 0
