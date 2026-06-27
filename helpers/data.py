def pack_nybbles(high, low):
	return ((high << 4) & 0xF0) | (low & 0x0F)

def get_nybble(val, isHigh: bool):
	return (val >> 4) & 0x0F if isHigh else val & 0x0F