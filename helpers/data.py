def pack_nybbles(high, low):
	return ((high << 4) & 0xF0) | (low & 0x0F)

def get_nybble(val, is_high: bool):
	return (val >> 4) & 0x0F if is_high else val & 0x0F

def find_uv_axes(main_axis):
	if main_axis == 0:
		return 1, 2
	elif main_axis == 1:
		return 0, 2
	else:
		return 0, 1
