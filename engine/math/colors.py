import math
import numpy as np
from dataclasses import dataclass


# --- linear <-> srgb --- #


def linear_to_srgb(x: float) -> float:
	return 12.92 * x if x <= 0.0031308 else 1.055 * pow(x, 0.4166666666666667) - 0.055


def srgb_to_linear(x: float) -> float:
	return ((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92


# --- linear <-> lab --- #


def linear_to_oklab(r: float, g: float, b: float) -> tuple[float, float, float]:
	l = +0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
	m = +0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
	s = +0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

	l_ = math.cbrt(l)
	m_ = math.cbrt(m)
	s_ = math.cbrt(s)

	L = +0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
	A = +1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
	B = +0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_

	return L, A, B


def oklab_to_linear(L: float, A: float, B: float) -> tuple[float, float, float]:
	l_ = L + 0.3963377774 * A + 0.2158037573 * B
	m_ = L - 0.1055613458 * A - 0.0638541728 * B
	s_ = L - 0.0894841775 * A - 1.2914855480 * B

	l, m, s = l_ ** 3, m_ ** 3, s_ ** 3

	r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
	g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
	b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

	return r, g, b


# --- hsv <-> lab helpers --- #


def _toe(x: float) -> float:
	k_1 = 0.206
	k_2 = 0.03
	k_3 = (1 + k_1) / (1 + k_2)

	return 0.5 * (k_3 * x - k_1 + math.sqrt((k_3 * x - k_1) ** 2 + 4 * k_2 * k_3 * x))


def _toe_inv(x: float) -> float:
	k_1 = 0.206
	k_2 = 0.03
	k_3 = (1 + k_1) / (1 + k_2)

	return (x**2 + x * k_1) / (k_3 * (x + k_2))


def _find_max_saturation(A: float, B: float) -> float:
	if -1.88170328 * A - 0.80936493 * B > 1:
		k0 = +1.19086277
		k1 = +1.76576728
		k2 = +0.59662641
		k3 = +0.75515197
		k4 = +0.56771245

		wl = +4.0767416621
		wm = -3.3077115913
		ws = +0.2309699292

	elif 1.81444104 * A - 1.19445276 * B > 1:
		k0 = +0.73956515
		k1 = -0.45954404
		k2 = +0.08285427
		k3 = +0.12541070
		k4 = +0.14503204

		wl = -1.2684380046
		wm = +2.6097574011
		ws = -0.3413193965

	else:
		k0 = +1.35733652
		k1 = -0.00915799
		k2 = -1.15130210
		k3 = -0.50559606
		k4 = +0.00692167

		wl = -0.0041960863
		wm = -0.7034186147
		ws = +1.7076147010

	S = k0 + k1 * A + k2 * B + k3 * A * A + k4 * A * B

	k_l = +0.3963377774 * A + 0.2158037573 * B
	k_m = -0.1055613458 * A - 0.0638541728 * B
	k_s = -0.0894841775 * A - 1.2914855480 * B

	l = 1 + S * k_l
	m = 1 + S * k_m
	s = 1 + S * k_s

	f1 = wl * (3 * k_l * l * l) + wm * (3 * k_m * m * m) + ws * (3 * k_s * s * s)
	f2 = wl * (6 * k_l * k_l * l) + wm * (6 * k_m * k_m * m) + ws * (6 * k_s * k_s * s)

	f = wl * (l ** 3) + wm * (m ** 3) + ws * (s ** 3)

	return S - f * f1 / (f1 * f1 - 0.5 * f * f2)


def _find_cusp(A: float, B: float) -> tuple[float, float]:
	S_cusp = _find_max_saturation(A, B)

	r, g, b = oklab_to_linear(1.0, A * S_cusp, B * S_cusp)

	L_cusp = math.cbrt(1.0 / max(r, g, b))
	C_cusp = L_cusp * S_cusp

	return L_cusp, C_cusp


# --- hsv <-> lab --- #


def okhsv_to_oklab(h: float, s: float, v: float) -> tuple[float, float, float]:
	if v < 1e-8:
		return 0.0, 0.0, 0.0

	A = math.cos(math.tau * h)
	B = math.sin(math.tau * h)

	L_cusp, C_cusp = _find_cusp(A, B)

	S_max = C_cusp / L_cusp
	T_max = C_cusp / (1.0 - L_cusp)

	S_0 = 0.5
	k = 1.0 - S_0 / S_max

	t = S_0 / (S_0 + T_max - T_max * k * s)
	L_v = 1.0 - s * t
	C_v = s * T_max * t

	if L_v < 1e-8:
		return 0.0, 0.0, 0.0

	L_ = v * L_v
	C_ = v * C_v

	if L_ < 1e-8:
		return 0.0, 0.0, 0.0

	L_vt = _toe_inv(L_v)
	C_vt = C_v * L_vt / L_v

	L_new = _toe_inv(L_)
	C = C_ * L_new / L_
	L = L_new

	r, g, b = oklab_to_linear(L_vt, A * C_vt, B * C_vt)
	scale_L = math.cbrt(1.0 / max(r, g, b, 1e-8))

	return L * scale_L, A * C * scale_L, B * C * scale_L


def oklab_to_okhsv(L: float, A_in: float, B_in: float) -> tuple[float, float, float]:
	C = math.hypot(A_in, B_in)

	if C < 1e-8:
		return 0.0, 0.0, _toe(L)

	A_ = A_in / C
	B_ = B_in / C

	h = 0.5 + 0.5 * math.atan2(-B_in, -A_in) / math.pi

	L_cusp, C_cusp = _find_cusp(A_, B_)
	S_max = C_cusp / L_cusp
	T_max = C_cusp / (1.0 - L_cusp)
	S_0 = 0.5
	k = 1.0 - S_0 / S_max

	t = T_max / (C + L * T_max)
	L_v = t * L
	C_v = t * C

	if L_v < 1e-8:
		return 0.0, 0.0, 0.0

	L_vt = _toe_inv(L_v)
	C_vt = C_v * L_vt / L_v

	r, g, b = oklab_to_linear(L_vt, A_ * C_vt, B_ * C_vt)
	scale_L = math.cbrt(1.0 / max(r, g, b, 1e-8))

	L = L / scale_L
	C = C / scale_L

	if L < 1e-8:
		return 0.0, 0.0, 0.0

	C = C * _toe(L) / L
	L = _toe(L)

	v = L / L_v
	s = (S_0 + T_max) * C_v / ((T_max * S_0) + T_max * k * C_v)

	return h, s, v


@dataclass
class PaletteEntry:
	name: str
	color: tuple[float, float, float]


class Palette:
	def __init__(self) -> None:
		self.entries = [PaletteEntry(f"Color {i}", (0, 0, 0)) for i in range(16)]

	def __getitem__(self, i: int):
		return self.entries[i].color

	def __setitem__(self, i: int, color) -> None:
		self.entries[i].color = color

	def get_name(self, i: int) -> str:
		return self.entries[i].name

	def set_name(self, i: int, name: str):
		self.entries[i].name = name

	def get_id(self, name: str) -> int:
		for i, entry in enumerate(self. entries):
			if entry.name == name:
				return i


		raise KeyError(f"Unknown palette entry: {name}")

	def tobytes(self):
		return np.array(
			[e.color for e in self.entries],
			dtype=np.float32
		).tobytes()

# class PaletteArray:
# 	def __init__(self):
# 		self._palettes = []

# 	def add(self, palette):
# 		self._palettes.append(palette)

# 	def stack_array(self):
# 		return np.stack(
# 			[p.colors for p in self._palettes],
# 			axis=0
# 		)  # shape (N, 16, 4)

