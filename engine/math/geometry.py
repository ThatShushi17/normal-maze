from dataclasses import dataclass
from engine.math import pack_byte

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

def generate_wall_data(datatype, data):
	return pack_byte(1, 0, datatype, data)

@dataclass(frozen=True)
class FacePos:
	axis: int
	face_i: int
	start_u: int
	start_v: int

@dataclass(frozen=True)
class FaceSet:
	x_low: int
	x_high: int
	y_low: int
	y_high: int
	z_low: int
	z_high: int

	def __getitem__(self, key):
		axis, is_high = key
		return (
			self.x_low,
			self.x_high,
			self.y_low,
			self.y_high,
			self.z_low,
			self.z_high,
		)[2 * axis + is_high]

	@classmethod
	def uniform(cls, face):
		return cls(face, face, face, face, face, face)

	@classmethod
	def matching(cls, face_x, face_y, face_z):
		return cls(
			face_x, face_x,
			face_y, face_y,
			face_z, face_z,
		)

	@classmethod
	def uniform_room(cls, wall, floor, ceiling):
		return cls(
			wall, wall,
			wall, wall,
			floor, ceiling,
		)

	@classmethod
	def matching_room(cls, wall_x, wall_y, floor, ceiling):
		return cls(
			wall_x, wall_x,
			wall_y, wall_y,
			floor, ceiling,
		)
