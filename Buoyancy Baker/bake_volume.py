import trimesh as tm
from PIL import Image
import numpy as np

import os
import math
import multiprocessing as mp
from itertools import repeat

def calc_volume_at_depth(depth: float, mesh: tm.Trimesh, mesh_volume: float) -> int:
	plane_origin_y = depth
	trimmed_mesh = mesh.slice_plane(plane_origin=(0, plane_origin_y, 0), plane_normal=(0, -1, 0), cap=True)
	return int((trimmed_mesh.volume / mesh_volume) * 255)

if __name__ == '__main__':
	start_y: int = -2
	end_y: int = 2
	steps: int = 64

	step_size: float = (end_y - start_y) / (steps - 1)
	step_angle: float = (math.pi / 2) / steps

	steps_sqrt = int(math.sqrt(steps))
	image_width = int(steps * math.sqrt(steps))
	array = np.zeros((image_width, image_width), "i1")

	pool = mp.Pool(mp.cpu_count())


	print(f"\n\n------------------------------\nSlicing mesh from {start_y:.3f} to {end_y:.3f} in {steps} steps.")
	# Output
	# Depth: X
	# Pitch: Y
	# Roll: Z
	mesh: tm.Trimesh = tm.load(os.path.join("meshes", "rowboat", "air.glb"), force = "mesh")
	mesh_volume = mesh.volume

	index_list: list = list(range(0, steps))
	depth_list: list = list(start_y + (step_size * depth_i)  for depth_i in range(0, steps))

	for roll_i in index_list:
		rolled_mesh = mesh.copy()

		roll_angle = step_angle * roll_i
		transform = tm.transformations.euler_matrix(0, 0, roll_angle)

		rolled_mesh.apply_transform(transform)
		x_offset = (roll_i % steps_sqrt) * steps
		y_offset = math.floor(roll_i / steps_sqrt) * steps

		for pitch_i in index_list:
			pitched_mesh = rolled_mesh.copy()

			pitch_angle = step_angle * pitch_i
			transform = tm.transformations.euler_matrix(pitch_angle, 0, 0)

			pitched_mesh.apply_transform(transform)

			results: list = pool.starmap(calc_volume_at_depth, zip(depth_list, repeat(pitched_mesh), repeat(mesh_volume)))
			temp_array = np.array(results)
			temp_array = temp_array.reshape((steps, 1))
			
			array[x_offset:x_offset + steps, y_offset + pitch_i:y_offset + pitch_i + 1] = temp_array
		
		print(f"Roll {roll_i} complete")

	pool.close()

	image: Image = Image.fromarray(array, "L")
	image = image.rotate(-90)
	image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
	image.save("air.png")
