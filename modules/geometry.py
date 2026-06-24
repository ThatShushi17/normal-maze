import pygame
import math

class Rect:
	def __init__(self, x, y, theta, l, w) -> None:
		self.x = x
		self.y = y
		self.theta = math.radians(theta)
		self.l = l
		self.w = w

		self._reset_points()

	def _reset_points(self) -> None:
		f_x = math.cos(self.theta)
		f_y = math.sin(self.theta)

		r_x = -math.sin(self.theta)
		r_y = math.cos(self.theta)

		x = self.x
		y = self.y
		l = self.l
		w = self.w

		# going clockwise
		self.c1 = pygame.Vector2(x, y)
		self.c2 = pygame.Vector2(x + f_x * l, y + f_y * l)
		self.c3 = pygame.Vector2(x + f_x * l + r_x * w, y + f_y * l + r_y * w)
		self.c4 = pygame.Vector2(x + r_x * w, y + r_y * w)

		self.sides = [
			(self.c1, self.c2),
			(self.c2, self.c3),
			(self.c3, self.c4),
			(self.c4, self.c1)
		]

	def draw(self, surf) -> None:
		points = [self.c1, self.c2, self.c3, self.c4]
		pygame.draw.polygon(surf, (200, 200, 200), points, 3)
		pygame.draw.circle(surf, (0, 255, 255), (int(self.c1.x), int(self.c1.y)), 4)
