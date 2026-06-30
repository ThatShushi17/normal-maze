def find_uv_axes(main_axis):
	if main_axis == 0:
		return 1, 2
	elif main_axis == 1:
		return 0, 2
	else:
		return 0, 1
