#version 430

layout (local_size_x = 8, local_size_y = 8) in;

layout (rgba8, binding = 0) writeonly uniform image2D img_output;

uniform vec3 u_cam_pos;
uniform vec3 u_cam_forward;
uniform vec3 u_cam_up;
uniform vec3 u_cam_right;
uniform usampler3D u_voxel_grid;



bool is_face_opaque(uint face_val) {
	return 1 == ((face_val >> 7u) & 1u);
}

uint get_channel_byte(uint channel_data, bool high) {
	return high ? ((channel_data >> 8) & 0xFF) : (channel_data & 0xFF);
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

	vec3 side_dist;
	if (ray_dir.x < 0.0) {
		side_dist.x = (ray_pos.x - float(grid_pos.x)) * travel_delta.x;
	} else {
		side_dist.x = (float(grid_pos.x) + 1.0 - ray_pos.x) * travel_delta.x;
	}

	if (ray_dir.y < 0.0) {
		side_dist.y = (ray_pos.y - float(grid_pos.y)) * travel_delta.y;
	} else {
		side_dist.y = (float(grid_pos.y) + 1.0 - ray_pos.y) * travel_delta.y;
	}

	if (ray_dir.z < 0.0) {
		side_dist.z = (ray_pos.z - float(grid_pos.z)) * travel_delta.z;
	} else {
		side_dist.z = (float(grid_pos.z) + 1.0 - ray_pos.z) * travel_delta.z;
	}

	bool hit = false;
	int max_steps = 45;
	uint face_val = 0;
	int side = 0;
	int last_side = -1;
	uvec4 vox;

	for (int i = 0; i < max_steps; i++) {
		if (grid_pos.x < 0 || grid_pos.x > 31 ||
			grid_pos.y < 0 || grid_pos.y > 31 ||
			grid_pos.z < 0 || grid_pos.z > 31) {
			break;
		}

		vox = texelFetch(u_voxel_grid, grid_pos, 0);

		if (last_side == 0) {
			face_val = get_channel_byte(vox.r, step_dir.x < 0);
			if (is_face_opaque(face_val)) { hit = true; break; }

		} else if (last_side == 1) {
			face_val = get_channel_byte(vox.g, step_dir.y < 0);
			if (is_face_opaque(face_val)) { hit = true; break; }

		} else if (last_side == 2) {
			face_val = get_channel_byte(vox.b, step_dir.z < 0);
			if (is_face_opaque(face_val)) { hit = true; break; }
		}

		if (side_dist.x < side_dist.y && side_dist.x < side_dist.z) {
			side = 0;

			face_val = get_channel_byte(vox.r, step_dir.x > 0);
			if (is_face_opaque(face_val)) { hit = true; break; }

			side_dist.x += travel_delta.x;
			grid_pos.x += step_dir.x;
			last_side = 0;

		} else if (side_dist.y < side_dist.z) {
			side = 1;

			face_val = get_channel_byte(vox.g, step_dir.y > 0);
			if (is_face_opaque(face_val)) { hit = true; break; }

			side_dist.y += travel_delta.y;
			grid_pos.y += step_dir.y;
			last_side = 1;
			
		} else {
			side = 2;

			face_val = get_channel_byte(vox.b, step_dir.z > 0);
			if (is_face_opaque(face_val)) { hit = true; break; }

			side_dist.z += travel_delta.z;
			grid_pos.z += step_dir.z;
			last_side = 2;
		}
	}

	vec4 pixel_color = vec4(0.10, 0.05, 0.05, 1.0);  // default/error

	if (hit) {
		vec3 color = vec3(0.5);  // grey wall
		uint face_data = face_val & 0xF;

		if (face_data == 4) color = vec3(0.7, 0.2, 0.2);  // red wall
		if (face_data == 8) color = vec3(0.2, 0.7, 0.2);  // green wall
		if (face_data == 12) color = vec3(0.2, 0.2, 0.7);  // blue wall

		if (side == 1) color *= 0.8;  // xz plane dimming
		if (side == 2) color *= 0.6;  // xy plane dimming
		pixel_color = vec4(color, 1.0);
	}

	imageStore(img_output, pixel_coords, pixel_color);
}
