#version 430

uniform sampler2D u_tex;
in vec2 v_texcoord;
out vec4 f_color;

void main() {
	f_color = texture(u_tex, vec2(v_texcoord.x, 1.0 - v_texcoord.y));
}