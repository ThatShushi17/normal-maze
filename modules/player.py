import pygame
import glm
import math
from helpers.data import pygame_Vec2_to_int_tuple
from helpers.math import clamp

MOUSE_SENSITIVITY = 0.2
WORLD_UP = glm.vec3(0.0, 0.0, 1.0)

class Player:
	def __init__(self, x, y, z, yaw, pitch, lin_speed=3, rot_speed=3) -> None:
		self.lin_speed = lin_speed
		self.rot_speed = rot_speed

		self.yaw = yaw
		self.pitch = pitch

		self.pos = glm.vec3()
		self.pos.x = x
		self.pos.y = y
		self.pos.z = z

		self.velocity = glm.vec3()
		self.forward = glm.vec3()
		self.right = glm.vec3()
		self.up = glm.vec3()

	def update(self, keys, m_dx, m_dy):
		self._handle_direction(keys, m_dx, m_dy)
		self._handle_movement(keys)


	# def draw(self, surf):
	# 	center = pygame_Vec2_to_int_tuple(self.pos)
	# 	dir_end = pygame_Vec2_to_int_tuple(self.pos + self.find_dir_vec() * 25)

	# 	pygame.draw.line(surf, (255, 255, 0), center, dir_end, 4)
	# 	pygame.draw.circle(surf, (255, 73, 106), center, 8)


	# def find_dir_vec(self, offset_rad=0.0):
	# 	return pygame.Vector2(math.cos(self.theta + offset_rad), math.sin(self.theta + offset_rad))


	def _set_self_dir_vecs(self):
		yaw = math.radians(self.yaw)
		pitch = math.radians(self.pitch)

		self.forward.x = math.cos(yaw) * math.cos(pitch)
		self.forward.y = math.sin(yaw) * math.cos(pitch)
		self.forward.z = math.sin(pitch)

		self.forward = glm.normalize(self.forward)
		self.right = glm.normalize(glm.cross(self.forward, WORLD_UP))
		self.up = glm.normalize(glm.cross(self.right, self.forward))

	def _handle_direction(self, keys, m_dx, m_dy):
		self.yaw += m_dx * MOUSE_SENSITIVITY
		self.pitch = clamp(self.pitch - m_dy * MOUSE_SENSITIVITY, -89.0, 89.0)

		if keys[pygame.K_LEFT]: self.yaw -= self.rot_speed
		if keys[pygame.K_RIGHT]: self.yaw += self.rot_speed

		self._set_self_dir_vecs()


	def _handle_movement(self, keys):
		self.velocity.x = 0
		self.velocity.y = 0
		self.velocity.z = 0

		if keys[pygame.K_UP] or keys[pygame.K_w]:
			self.velocity += self.forward

		if keys[pygame.K_DOWN] or keys[pygame.K_s]:
			self.velocity -= self.forward

		if keys[pygame.K_a]:
			self.velocity -= self.right

		if keys[pygame.K_d]:
			self.velocity += self.right

		# if isMoving:
		if glm.length2(self.velocity):  # type: ignore
			self.velocity = glm.normalize(self.velocity) * self.lin_speed
			self.pos += self.velocity
