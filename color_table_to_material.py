import numpy
import sys
import yaml

from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageColor, ImageOps
from typing import List, Dict

@dataclass
class MaterialReference:
	color : Path = None
	normal : Path = None
	height : Path = None
	metal : Path = None
	roughness : Path = None
	roughness_inverted : int = 0
	emissive : Path = None
	occlusion : Path = None

@dataclass
class Material:
	color : Image = None
	normal : Image = None
	height : Image = None
	metal : Image = None
	roughness : Image = None
	emissive : Image = None
	occlusion : Image = None

@dataclass
class MaterialApplier:
	material : Material = None
	scale : float = 1.0
	blend_color : float = 1.0
	blend_normal : float = 1.0
	blend_height : float = 1.0
	blend_metal : float = 1.0
	blend_roughness : float = 1.0
	blend_emissive : float = 1.0
	blend_occlusion : float = 1.0

@dataclass
class RGBA:
	r : int = 0
	g : int = 0
	b : int = 0
	a : int = 255

def parse_material_folder(root : Path, material : MaterialReference):
	for p in root.glob('*'):
		if ".bak" in p.stem:
			continue

		stem_lower = p.stem.lower()
		if "_normal" in stem_lower:
			material.normal = p
		elif "_nor" in stem_lower:
			material.normal = p
		elif "_NORM" in stem_lower:
			material.normal = p
		elif "_height" in stem_lower:
			material.height = p
		elif "_disp" in stem_lower:
			material.height = p
		elif "_metallic" in stem_lower:
			material.metal = p
		elif "_metal" in stem_lower:
			material.metal = p
		elif "_roughness" in stem_lower:
			material.roughness = p
		elif "_smoothness" in stem_lower:
			material.roughness = p
			material.roughness_inverted = 1
		elif "_rough" in stem_lower:
			material.roughness = p
		elif "_emissive" in stem_lower:
			material.emissive = p
		elif "_occ" in stem_lower:
			material.occlusion = p
		elif "_ao" in stem_lower:
			material.occlusion = p
		elif "_ambientocclusion" in stem_lower:
			material.occlusion = p
		elif "_diffuse" in stem_lower:
			material.color = p
		elif "_base" in stem_lower:
			material.color = p
		elif "_color" in stem_lower:
			material.color = p
		elif "_albedo" in stem_lower:
			material.color = p

def parse_material_library_path(root : Path, material_library : Dict[str, MaterialReference]):
	for p in root.glob('*'):
		material_library[p.name] = MaterialReference()
		parse_material_folder(p, material_library[p.name])

def load_material(reference : MaterialReference):
	material = Material()
	if reference.color != None:
		material.color = Image.open(reference.color)
	if reference.normal != None:
		material.normal = Image.open(reference.normal)
	if reference.height != None:
		material.height = Image.open(reference.height)
	if reference.metal != None:
		material.metal = Image.open(reference.metal)
	if reference.roughness != None:
		material.roughness = Image.open(reference.roughness)
		if reference.roughness_inverted == 1:
		  material.roughness = ImageOps.invert(material.roughness)
	if reference.emissive != None:
		material.emissive = Image.open(reference.emissive)
	if reference.occlusion != None:
		material.occlusion = Image.open(reference.occlusion)
	return material

def save_material(material : Material, out_path : Path):
	if material.color != None:
		material.color.save(Path(out_path.parent, out_path.stem + "_albedo" + out_path.suffix))
	if material.normal != None:
		material.normal.save(Path(out_path.parent, out_path.stem + "_norm" + out_path.suffix))
	if material.height != None:
		material.height.save(Path(out_path.parent, out_path.stem + "_height" + out_path.suffix))
	if material.metal != None:
		material.metal.save(Path(out_path.parent, out_path.stem + "_metal" + out_path.suffix))
	if material.roughness != None:
		material.roughness.save(Path(out_path.parent, out_path.stem + "_roughness" + out_path.suffix))
	if material.emissive != None:
		material.emissive.save(Path(out_path.parent, out_path.stem + "_emissive" + out_path.suffix))
	if material.occlusion != None:
		material.occlusion.save(Path(out_path.parent, out_path.stem + "_ao" + out_path.suffix))

def apply_texture_to_output(output : Image, size, input : Image, scale : float, blend : float, mask : Image):
	if output is None:
		output = Image.new(mode = "RGB", size = size)
		blend = 1.0
	
	new_width = int(input.size[0] * scale)
	new_height = int(input.size[1] * scale)

	max_width = size[0]
	max_height = size[1]
	width_copies = int(max_width / new_width)
	height_copies = int(max_height / new_height)
	
	new_input = input.resize((new_width, new_height), Image.Resampling.LANCZOS)
	input = Image.new(mode = "RGB", size = size)
	for i in range(0, width_copies+1):
		for j in range(0, height_copies+1):
			input.paste(new_input, (i * new_width, j * new_height))

	input = Image.blend(output, input, blend)
	output.paste(input, (0, 0), mask=mask)
	return output

def apply_material_to_output(output : Material, size, material_applier : MaterialApplier, mask : Image):
	if material_applier.material.normal != None:
		output.normal = apply_texture_to_output(output.normal, size, material_applier.material.normal, material_applier.scale, material_applier.blend_normal, mask)
	if material_applier.material.height != None:
		output.height = apply_texture_to_output(output.height, size, material_applier.material.height, material_applier.scale, material_applier.blend_height, mask)
	if material_applier.material.metal != None:
		output.metal = apply_texture_to_output(output.metal, size, material_applier.material.metal, material_applier.scale, material_applier.blend_metal, mask)
	if material_applier.material.roughness != None:
		output.roughness = apply_texture_to_output(output.roughness, size, material_applier.material.roughness, material_applier.scale, material_applier.blend_roughness, mask)
	if material_applier.material.emissive != None:
		output.emissive = apply_texture_to_output(output.emissive, size, material_applier.material.emissive, material_applier.scale, material_applier.blend_emissive, mask)
	if material_applier.material.occlusion != None:
		output.occlusion = apply_texture_to_output(output.occlusion, size, material_applier.material.occlusion, material_applier.scale, material_applier.blend_occlusion, mask)


def apply_color_mask(mask : Image, output : Material, colorcode_to_materialapplier : Dict[tuple, MaterialApplier]):
	mask_arry = numpy.array(mask)
	for k,v in colorcode_to_materialapplier.items():
		if mask_arry.shape[2] == 4:
			matching_colors = numpy.all(mask_arry == (k[0], k[1], k[2], 255), axis=-1)
		else:
			matching_colors = numpy.all(mask_arry == k, axis=-1)
		color_mask = Image.fromarray((matching_colors*255).astype(numpy.uint8))
		apply_material_to_output(output, mask.size, v, color_mask)
	return output

yaml_file = Path(sys.argv[1])
with open(yaml_file, "r") as stream:
	try:
		data = yaml.safe_load(stream)

		if "material_library_path" not in data:
			raise Exception("Material library path not in yaml")

		mat_lib_path = Path(data["material_library_path"])
		if not mat_lib_path.is_dir():
			raise Exception("Invalid material path")

		material_library = {}
		parse_material_library_path(mat_lib_path, material_library)

		if "output" not in data:
			raise Exception("Output dictionary not in yaml")

		data_output = data["output"]
		if "directory" not in data_output:
			raise Exception("Output directory not in yaml")
		output_directory = Path(data_output["directory"])
		if not output_directory.is_dir():
			raise Exception("Output directory not valid path")
		
		output = Material()

		if "starting" in data_output:
			if "normal" in data_output["starting"]:
				output.normal = Image.open(Path(data_output["starting"]["normal"])).convert("RGB")
			if "occlusion" in data_output["starting"]:
				output.occlusion = Image.open(Path(data_output["starting"]["occlusion"])).convert("RGB")
				if "_smooth" in data_output["starting"]["occlusion"]:
				  output.occlusion = ImageOps.invert(output.occlusion)

		if "masks" not in data:
			raise Exception("Masks dictionary not in yaml")

		masks = data["masks"]
		if len(masks) == 0:
			raise Exception("Need at least one mask specified in yaml")

		for k,v in masks.items():
			mask_path = Path(k)
			if not mask_path.is_file():
				raise Exception(f"Mask {k} does not exist")
			mask = Image.open(mask_path)
			if "colors" not in v:
				raise Exception("Need at least one color in a mask")

			colors = v["colors"]
			colorcode_to_materialapplier = {}
			for color_key,color_options in colors.items():
				material_applier = MaterialApplier()
				if "scale" not in color_options:
					material_applier.scale = 1.0
				else:
					material_applier.scale = float(color_options["scale"])

				if "blend" in color_options:
					blend = color_options["blend"]
					if "normal" in blend:
						material_applier.blend_normal = float(blend["normal"])
					if "height" in blend:
						material_applier.blend_height = float(blend["height"])
					if "metal" in blend:
						material_applier.blend_metal = float(blend["metal"])
					if "roughness" in blend:
						material_applier.blend_roughness = float(blend["roughness"])
					if "emissive" in blend:
						material_applier.blend_emissive = float(blend["emissive"])
					if "occlusion" in blend:
						material_applier.blend_occlusion = float(blend["occlusion"])

				if "material" not in color_options:
					raise Exception(f"Need to specify a material name for {color_key} in mask {k}")
				material_name = color_options["material"]

				if material_name not in material_library:
					raise Exception(f"Material name {material_name} not found in material library for {color_key} in mask {k}")
				material_applier.material = load_material(material_library[material_name])
				color = ImageColor.getcolor(color_key, "RGB")
				colorcode_to_materialapplier[color] = material_applier
			output = apply_color_mask(mask, output, colorcode_to_materialapplier)

		save_material(output, output_directory / Path(yaml_file.stem + ".png"))

	except yaml.YAMLError as exc:
		print(exc)
