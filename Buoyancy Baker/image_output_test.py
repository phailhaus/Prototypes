from PIL import Image
import numpy as np

import math

if __name__ == '__main__':
	start_y: int = -2
	end_y: int = 2
	steps: int = 64

	step_size: float = (end_y - start_y) / (steps - 1)
	step_angle: float = (math.pi / 2) / steps

	steps_sqrt = int(math.sqrt(steps))
	image_width = int(steps * math.sqrt(steps))
	arrayr = np.zeros((image_width, image_width), "i1")
	arrayg = np.zeros((image_width, image_width), "i1")
	arrayb = np.zeros((image_width, image_width), "i1")

	index_list: list = list(range(0, steps))

	for altitude_i in index_list:
		x_offset = (altitude_i % steps_sqrt) * steps
		y_offset = math.floor(altitude_i / steps_sqrt) * steps

		for azimuth_i in index_list:
			results = list(range(0, steps))
			temp_array = np.array(results)
			temp_array = temp_array.reshape((steps, 1))
			
			arrayr[x_offset:x_offset + steps, y_offset + azimuth_i:y_offset + azimuth_i + 1] = temp_array

			temp_array = np.full((steps, 1), azimuth_i)
			arrayg[x_offset:x_offset + steps, y_offset + azimuth_i:y_offset + azimuth_i + 1] = temp_array

			temp_array = np.full((steps, 1), altitude_i)
			arrayb[x_offset:x_offset + steps, y_offset + azimuth_i:y_offset + azimuth_i + 1] = temp_array
	
	r: Image = Image.fromarray(arrayr, "L")
	g: Image = Image.fromarray(arrayg, "L")
	b: Image = Image.fromarray(arrayb, "L")
	image = Image.merge("RGB", (r, g, b))
	image = image.rotate(-90)
	image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
	image.save("test.png")
