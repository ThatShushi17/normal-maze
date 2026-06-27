import pygame
import glm
import math
import numpy as np
from helpers.data import get_nybble
from helpers.math import clamp

MOUSE_SENSITIVITY = 0.2
WORLD_UP = glm.vec3(0.0, 0.0, 1.0)

class Player:
	def __init__(self, x, y, z, yaw, pitch, lin_speed=3.0, rot_speed=3.0) -> None:
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

	def update(self, keys, m_dx, m_dy, room):
		self._handle_direction(keys, m_dx, m_dy)
		self._set_velocity(keys)
		self._handle_collisions(room)
		self.pos += self.velocity

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


	def _set_velocity(self, keys):
		self.velocity.x = 0.0
		self.velocity.y = 0.0
		self.velocity.z = 0.0

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

	def _handle_collisions(self, room):
		grid_pos = glm.ivec3(glm.floor(self.pos))
		new_grid_pos = glm.ivec3(glm.floor(self.pos + self.velocity))
		# grid_pos_delta = new_grid_pos - grid_pos

		curr_voxel = room[grid_pos.z, grid_pos.y, grid_pos.x, :]

		if 0 <= new_grid_pos.x <= 31:
			new_voxel = room[grid_pos.z, grid_pos.y, new_grid_pos.x, :]

			curr_face = get_nybble(curr_voxel[0], self.velocity.x > 0)
			new_face = get_nybble(new_voxel[0], self.velocity.x < 0)

			if curr_face != 0 or new_face != 0:
				self.velocity.x = 0
		else:
			self.velocity.x = 0

		if 0 <= new_grid_pos.y <= 31:
			new_voxel = room[grid_pos.z, new_grid_pos.y, grid_pos.x, :]

			curr_face = get_nybble(curr_voxel[1], self.velocity.y > 0)
			new_face = get_nybble(new_voxel[1], self.velocity.y < 0)

			if curr_face != 0 or new_face != 0:
				self.velocity.y = 0
		else:
			self.velocity.y = 0

		if 0 <= new_grid_pos.z <= 31:
			new_voxel = room[new_grid_pos.z, grid_pos.y, grid_pos.x, :]

			curr_face = get_nybble(curr_voxel[2], self.velocity.z > 0)
			new_face = get_nybble(new_voxel[2], self.velocity.z < 0)

			if curr_face != 0 or new_face != 0:
				self.velocity.z = 0
		else:
			self.velocity.z = 0
