# 16bit voxel data is as follows:
# 76543210|76543210
# 7   : is_opaque (for shader)
# 6   : is_portal
# 54  : datatype of,
# 3210: data
# the higher byte represents the greater plane, and the lower the lesser plane.
# the rgb channels hold the data for the xyz planes respectively.

def pack_byte(is_opaque, is_portal, datatype, data):
	return (
		((is_opaque & 1) << 7) |
		((is_portal & 1) << 6) |
		((datatype & 0b11) << 4) |
		(data & 0b1111)
	)

# default: pack_bytes(high_byte, low_byte)
# switch False => 0, True => 1
def pack_bytes(byte_0, byte_1, high_switch=None):
	byte_0 &= 0xFF
	byte_1 &= 0xFF

	if high_switch is None or high_switch == False:
		byte_0 <<= 8
	else:
		byte_1 <<= 8

	return byte_1 | byte_0
