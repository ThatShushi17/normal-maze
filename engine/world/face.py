from dataclasses import dataclass

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
