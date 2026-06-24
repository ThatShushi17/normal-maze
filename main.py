import pygame
import sys
import math
from modules.player import Player

WIDTH, HEIGHT = 800, 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BG_COLOR = (20, 20, 20)
WALL_COLOR = (200, 200, 200)

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
		pygame.draw.polygon(surf, WALL_COLOR, points, 3)
		pygame.draw.circle(surf, (0, 255, 255), (int(self.c1.x), int(self.c1.y)), 4)

player = Player(WIDTH // 2, HEIGHT // 2, 0, 3, 3)

walls = [
	Rect(250, 150, 0, 100, 100)
]

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	keys = pygame.key.get_pressed()

	player.update(keys)

	screen.fill(BG_COLOR)

	for wall in walls:
		wall.draw(screen)

	player.draw(screen)

	# pygame.draw.circle(screen, PLAYER_COLOR, (int(player.pos.x), int(player.pos.y)), 8)

	# dir_end = player.pos + player.find_dir_vec() * 20
	# pygame.draw.line(screen, DIR_LINE_COLOR, (int(player.pos.x), int(player.pos.y)), (int(dir_end.x), int(dir_end.y)), 4)

	# dir_end = player.pos + tangent_vec * 20
	# pygame.draw.line(screen, DIR_LINE_COLOR, (int(player.pos.x), int(player.pos.y)), (int(dir_end.x), int(dir_end.y)), 4)

	pygame.display.flip()
	clock.tick(60)