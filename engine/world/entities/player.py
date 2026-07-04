import pygame
import glm
import math
from engine.math.functions import clamp
from engine.math.geometry import check_face_solid, find_uv_axes

MOUSE_SENSITIVITY = 0.2
WORLD_UP = glm.vec3(0.0, 0.0, 1.0)

class Player:
	def __init__(self, x, y, z, yaw, pitch, lin_speed=3.0, rot_speed=3.0):
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
		self._handle_velocity(room)


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

		if keys[pygame.K_LEFT]: self.yaw += self.rot_speed
		if keys[pygame.K_RIGHT]: self.yaw -= self.rot_speed

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

		# if is_moving:
		if glm.length2(self.velocity):  # type: ignore
			self.velocity = glm.normalize(self.velocity) * self.lin_speed
			self.pos += self.velocity

	def _handle_velocity(self, room):
		vel_length = glm.length(self.velocity)  # type: ignore
		if vel_length < 1e-6: return

		# use 3d dda to traverse the grid
		ray_dir = self.velocity / vel_length
		ray_pos = glm.vec3(self.pos)
		grid_pos = glm.ivec3(glm.floor(ray_pos))

		travel_delta = glm.abs(1.0 / (ray_dir + 1e-8))
		step_dir = glm.ivec3(glm.sign(ray_dir))

		side_dist = glm.vec3(0.0)

		for i in range(3):
			if ray_dir[i] < 0.0:
				side_dist[i] = (ray_pos[i] - float(grid_pos[i])) * travel_delta[i]
			else:
				side_dist[i] = (float(grid_pos[i]) + 1.0 - ray_pos[i]) * travel_delta[i]

		last_side = -1
		curr_dist = 0.0

		SAFETY_MARGIN = 5e-3
		RADIUS = 0.3
		SPHERE_OFFSETS = [WORLD_UP * -0.6, glm.vec3(0.0), WORLD_UP * -0.6]

		# DEPRACATED
		# def check_colliding(eval_pos, eval_side):
		# 	# uv are face coords
		#   ax_u, ax_v = find_uv_axes(eval_side)
		# 	if eval_side == 0:   ax_u, ax_v = 1, 2  # y, z
		# 	elif eval_side == 1: ax_u, ax_v = 0, 2  # x, z
		# 	else:                ax_u, ax_v = 0, 1  # x, y

		# 	for offset in SPHERE_OFFSETS:
		# 		sphere_pos = eval_pos + offset

		# 		u_val, v_val = sphere_pos[ax_u], sphere_pos[ax_v]
		# 		u_floor, v_floor = int(math.floor(u_val)), int(math.floor(v_val))

		# 		u_min = -1 if (u_val - u_floor - RADIUS) <  0.0 else 0
		# 		u_max =  1 if (u_val - u_floor + RADIUS) >= 1.0 else 0
		# 		u_min = -1 if (u_val - u_floor - RADIUS) <  0.0 else 0
		# 		u_min =  1 if (u_val - u_floor + RADIUS) >= 1.0 else 0

		# 		coords = [0, 0, 0]
		# 		coords[eval_side] = grid_pos[eval_side]

		# 		eval_coords = coords[eval_side]
		# 		eval_step_dir = step_dir[eval_side]
		# 		is_moving_forward = eval_step_dir > 0
		# 		hasNext = eval_coords > 0 and not is_moving_forward or eval_coords < 31 and is_moving_forward

		# 		for du in range(u_min, u_max + 1):
		# 			for dv in range(v_min, v_max + 1):
		# 				coords[ax_u] = u_floor + du
		# 				coords[ax_v] = v_floor + dv

		# 				nx, ny, nz = coords[0], coords[1], coords[2]
		# 				u, v = coords[ax_u], coords[ax_v]
		# 				if not (0 <= nx <= 31 and 0 <= ny <= 31 and 0 <= nz <= 31):
		# 					continue

		# 				curr_faces = room[nz, ny, nx, eval_side]
		# 				curr_face = get_nybble(curr_faces, eval_step_dir > 0)

		# 				if hasNext:
		# 					next_coords = coords.copy()
		# 					next_coords[eval_side] += eval_step_dir
		# 					next_faces = room[next_coords[2], next_coords[1], next_coords[0], eval_side]
		# 					next_face = get_nybble(next_faces, eval_step_dir < 0)
		# 				else: next_face = None

		# 				if hasNext: is_solid = check_face_solid(curr_face, next_face)
		# 				else: is_solid = check_face_solid(curr_face, next_face, False)

		# 				if is_solid:
		# 					u_closest = clamp(u_val, float(u), float(u + 1))

		# while side_dist.x < float('inf') or side_dist.y < float('inf') or side_dist.z < float('inf'):
		# 	curr_pos = ray_pos + ray_dir * curr_dist

		# 	# check the entry face
		# 	hit_entry = False
		# 	if last_side != -1:
		# 		side = last_side

		# 		for z_off in SPHERE_OFFSETS:
		# 			sphere_pos = glm.vec3(curr_pos.x, curr_pos.y, curr_pos.z + z_off)
		# 			s_grid_pos = glm.ivec3(glm.floor(sphere_pos))



		# 			# uv are face offset coords
		# 			if side == 0:
		# 				u_min, u_max = get_adjacencies(sphere_pos.y, s_grid_pos.y)
		# 				v_min, v_max = get_adjacencies(sphere_pos.z, s_grid_pos.z)
		# 			elif side == 1:
		# 				u_min, u_max = get_adjacencies(sphere_pos.x, s_grid_pos.x)
		# 				v_min, v_max = get_adjacencies(sphere_pos.z, s_grid_pos.z)
		# 			else:
		# 				u_min, u_max = get_adjacencies(sphere_pos.x, s_grid_pos.x)
		# 				v_min, v_max = get_adjacencies(sphere_pos.y, s_grid_pos.y)