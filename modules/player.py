import pygame
import math
from helpers.datatypes import pygame_Vec2_to_int_tuple

class Player:
	def __init__(self, x, y, theta, lin_speed=3, rot_speed=3) -> None:
		self.pos = pygame.Vector2(x, y)
		self.theta = math.radians(theta)
		self.lin_speed = lin_speed
		self.rot_speed = math.radians(rot_speed)

	def update(self, keys):
		self._handle_input(keys)

	def draw(self, surf):
		center = pygame_Vec2_to_int_tuple(self.pos)
		dir_end = pygame_Vec2_to_int_tuple(self.pos + self.find_dir_vec() * 25)

		pygame.draw.line(surf, (255, 255, 0), center, dir_end, 4)
		pygame.draw.circle(surf, (255, 73, 106), center, 8)

	def find_dir_vec(self, offset_rad=0.0):
		return pygame.Vector2(math.cos(self.theta + offset_rad), math.sin(self.theta + offset_rad))

	def find_screen_pos(self) -> tuple:
		return (int(self.pos.x), int(self.pos.y))

	def _handle_input(self, keys):
		if keys[pygame.K_LEFT]:
			self.theta -= self.rot_speed
		if keys[pygame.K_RIGHT]:
			self.theta += self.rot_speed

		forward_vec = self.find_dir_vec()
		tangent_vec = self.find_dir_vec(offset_rad=math.radians(90))

		if keys[pygame.K_UP] or keys[pygame.K_w]:
			self.pos += forward_vec * self.lin_speed
		if keys[pygame.K_DOWN] or keys[pygame.K_s]:
			self.pos -= forward_vec * self.lin_speed
		if keys[pygame.K_a]:
			self.pos -= tangent_vec * self.lin_speed
		if keys[pygame.K_d]:
			self.pos += tangent_vec * self.lin_speed