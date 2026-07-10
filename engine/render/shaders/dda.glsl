#version 430

layout (local_size_x = 8, local_size_y = 8) in;

struct PortalData {
	ivec3 delta;
	int flip_main;
};

layout (rgba8, binding = 0) writeonly uniform image2D img_output;
layout (std430, binding = 2) buffer PortalDataBuffer {
	PortalData portals[];
};

uniform vec3 u_cam_pos;
uniform vec3 u_cam_forward;
uniform vec3 u_cam_up;
uniform vec3 u_cam_right;
uniform usampler3D u_voxel_grid;
uniform vec3 u_palette[16];

bool is_face_opaque(uint face_val) {
	return 1 == ((face_val >> 7u) & 1u);
}

bool is_face_portal(uint face_val) {
	return 1 == ((face_val >> 6u) & 1u);
}

uint get_channel_byte(uint channel_data, bool high) {
	return high ? ((channel_data >> 8) & 0xFF) : (channel_data & 0xFF);
}

vec3 calculate_side_dist(vec3 ray_pos, vec3 ray_dir, ivec3 grid_pos, vec3 travel_delta) {
	vec3 side_dist;
	
	if (ray_dir.x < 0.0) side_dist.x = (ray_pos.x - float(grid_pos.x)) * travel_delta.x;
	else                 side_dist.x = (float(grid_pos.x) + 1.0 - ray_pos.x) * travel_delta.x;
	
	if (ray_dir.y < 0.0) side_dist.y = (ray_pos.y - float(grid_pos.y)) * travel_delta.y;
	else                 side_dist.y = (float(grid_pos.y) + 1.0 - ray_pos.y) * travel_delta.y;
	
	if (ray_dir.z < 0.0) side_dist.z = (ray_pos.z - float(grid_pos.z)) * travel_delta.z;
	else                 side_dist.z = (float(grid_pos.z) + 1.0 - ray_pos.z) * travel_delta.z;

	return side_dist;
}

void traverse_portal(uint face_val, int side, float t_hit,
		inout vec3 ray_pos, inout vec3 ray_dir, inout ivec3 step_dir,
		inout ivec3 grid_pos, inout vec3 side_dist, vec3 travel_delta) {

	uint portal_id = face_val & 0x3Fu;

	vec3 delta = vec3(portals[portal_id].delta);
	bool flip = portals[portal_id].flip_main != 0;

	vec3 hit_pos = ray_pos + t_hit * ray_dir;

	if (flip) {
		if (side == 0)      ray_dir.x = -ray_dir.x;
		else if (side == 1) ray_dir.y = -ray_dir.y;
		else if (side == 2) ray_dir.z = -ray_dir.z;

		step_dir = ivec3(sign(ray_dir));
	}

	ray_pos = hit_pos + delta + (ray_dir * 1e-4);
	grid_pos = ivec3(floor(ray_pos));
	side_dist = calculate_side_dist(ray_pos, ray_dir, grid_pos, travel_delta);
}

void main() {
	ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);
	ivec2 screen_size = imageSize(img_output);

	if (pixel_coords.x >= screen_size.x || pixel_coords.y >= screen_size.y) {
		return;
	}

	vec2 uv = (vec2(pixel_coords) / vec2(screen_size)) * 2.0 - 1.0;
	float aspect_ratio = float(screen_size.x) / float(screen_size.y);
	uv.x *= aspect_ratio;

	// todo: add fov
	vec3 ray_dir = normalize(u_cam_forward + uv.x * u_cam_right + uv.y * u_cam_up);
	vec3 ray_pos = u_cam_pos;

	ivec3 grid_pos = ivec3(floor(ray_pos));
	vec3 travel_delta = abs(1.0 / (ray_dir + 1e-8));
	ivec3 step_dir = ivec3(sign(ray_dir));
	vec3 side_dist = calculate_side_dist(ray_pos, ray_dir, grid_pos, travel_delta);

	bool hit = false;
	int max_steps = 30;
	uint face_val = 0;
	int side = 0;
	int last_side = -1;
	uvec4 vox;
	float t_hit = 0.0;

	for (int i = 0; i < max_steps; i++) {
		if (grid_pos.x < 0 || grid_pos.x > 31 ||
			grid_pos.y < 0 || grid_pos.y > 31 ||
			grid_pos.z < 0 || grid_pos.z > 31) {
			break;
		}

		vox = texelFetch(u_voxel_grid, grid_pos, 0);

		if (last_side == 0) {
			face_val = get_channel_byte(vox.r, step_dir.x < 0);
			
			if (is_face_opaque(face_val)) {
				hit = true;
				t_hit = side_dist.x - travel_delta.x;
				break;
			}

		} else if (last_side == 1) {
			face_val = get_channel_byte(vox.g, step_dir.y < 0);
			
			if (is_face_opaque(face_val)) {
				hit = true;
				t_hit = side_dist.y - travel_delta.y;
				break;
			}

		} else if (last_side == 2) {
			face_val = get_channel_byte(vox.b, step_dir.z < 0);
			
			if (is_face_opaque(face_val)) {
				hit = true;
				t_hit = side_dist.z - travel_delta.z;
				break;
			}
		}

		if (side_dist.x < side_dist.y && side_dist.x < side_dist.z) {
			side = 0;

			face_val = get_channel_byte(vox.r, step_dir.x > 0);
			
			if (is_face_opaque(face_val)) {
				hit = true;
				t_hit = side_dist.x;
				break;
			}
			if (is_face_portal(face_val)) {
				traverse_portal(face_val, side, side_dist.x, ray_pos, ray_dir, step_dir, grid_pos, side_dist, travel_delta);
				last_side = -1;
				continue;
			}

			side_dist.x += travel_delta.x;
			grid_pos.x += step_dir.x;
			last_side = 0;

		} else if (side_dist.y < side_dist.z) {
			side = 1;

			face_val = get_channel_byte(vox.g, step_dir.y > 0);
			
			if (is_face_opaque(face_val)) {
				hit = true;
				t_hit = side_dist.y;
				break;
			}
			if (is_face_portal(face_val)) {
				traverse_portal(face_val, side, side_dist.y, ray_pos, ray_dir, step_dir, grid_pos, side_dist, travel_delta);
				last_side = -1;
				continue;
			}

			side_dist.y += travel_delta.y;
			grid_pos.y += step_dir.y;
			last_side = 1;
			
		} else {
			side = 2;

			face_val = get_channel_byte(vox.b, step_dir.z > 0);
			
			if (is_face_opaque(face_val)) {
				hit = true;
				t_hit = side_dist.z;
				break;
			}

			if (is_face_portal(face_val)) {
				traverse_portal(face_val, side, side_dist.z, ray_pos, ray_dir, step_dir, grid_pos, side_dist, travel_delta);
				last_side = -1;
				continue;
			}

			side_dist.z += travel_delta.z;
			grid_pos.z += step_dir.z;
			last_side = 2;
		}
	}

	vec4 pixel_color = vec4(0.10, 0.05, 0.05, 1.0);  // default/error

	if (hit) {
		uint face_data = face_val & 0xFu;
		uint face_datatype = (face_val >> 4u) & 3u;
		vec3 color = u_palette[face_data];

		if (face_datatype == 1u) {
			vec3 hit_pos = ray_pos + t_hit * ray_dir;
			vec2 face_uv;

			if (side == 0)      face_uv = fract(hit_pos.yz);
			else if (side == 1) face_uv = fract(hit_pos.xz);
			else                face_uv = fract(hit_pos.xy);

			float thickness = 0.02;
			if (face_uv.x < thickness || face_uv.x > 1.0 - thickness ||
				face_uv.y < thickness || face_uv.y > 1.0 - thickness) {
				color = mix(vec3(0.25), color, 0.85);
			} else {
				int n = 4;  // number of gridlines per tile
				float sub_thickness = thickness * float(n + 1) * 0.33;

				vec2 sub_uv = fract(face_uv * float(n + 1));

				if (sub_uv.x < sub_thickness || sub_uv.x > 1.0 - sub_thickness ||
					sub_uv.y < sub_thickness || sub_uv.y > 1.0 - sub_thickness) {
					color = mix(vec3(0.25), color, 0.85);
				}
			}
		}

		if (side == 1) color *= 0.8;  // xz plane dimming
		if (side == 2) color *= 0.6;  // xy plane dimming
		pixel_color = vec4(color, 1.0);
	}

	imageStore(img_output, pixel_coords, pixel_color);
}
