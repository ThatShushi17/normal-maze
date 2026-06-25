def pygame_Vec2_to_int_tuple(vec) -> tuple:
	return (int(vec.x), int(vec.y))

def pack_nybbles(high, low):
	return ((high << 4) & 0xF0) | (low & 0x0F)