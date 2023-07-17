import json
import sys
import yaml

from pathlib import Path

input_path = Path(sys.argv[1])
material_mapper_file = input_path / "material_mapper.yaml"

if material_mapper_file.exists():
	with open(material_mapper_file, 'r') as file:
		shader_map = yaml.safe_load(file)
else:
	shader_map = {}

material_maps = {}
for p in input_path.glob('**/*.png'):
	if ".bak" in p.stem:
		continue

	if "_normal" in p.stem:
		key = p.stem.replace("_normal", "")
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["NORMAL_TEX"] = p
	elif "_norm" in p.stem:
		key = p.stem.replace("_norm", "")
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["NORMAL_TEX"] = p
	elif "_height" in p.stem:
		key = p.stem.replace("_height", "")
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["HEIGHT_TEX"] = p
	elif "_metallic" in p.stem:
		key = p.stem.replace("_metallic", "")
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["METALLIC_TEX"] = p
	elif "_metal" in p.stem:
		key = p.stem.replace("_metal", "")
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["METALLIC_TEX"] = p
	elif "_roughness" in p.stem:
		key = p.stem.replace("_roughness", "")
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["ROUGHNESS_TEX"] = p
	elif "_smoothness" in p.stem:
		key = p.stem.replace("_smoothness", "")
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["ROUGHNESS_TEX"] = p
	elif "_rough" in p.stem:
		key = p.stem.replace("_rough", "")
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["ROUGHNESS_TEX"] = p
	elif "_emissive" in p.stem:
		key = p.stem.replace("_emissive", "")
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["EMISSIVE_TEX"] = p
	elif "_occ" in p.stem:
		key = p.stem.replace("_occ", "")
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["AMBIENT_OCCLUSION_TEX"] = p
	elif "_ao" in p.stem:
		key = p.stem.replace("_ao", "")
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["AMBIENT_OCCLUSION_TEX"] = p
	elif "_diffuse" in p.stem:
		continue
	elif "_base" in p.stem:
		continue
	elif p.suffix == ".mtz":
		continue
	else:
		key = p.stem
		if key not in material_maps:
			material_maps[key] = {}
		material_maps[key]["NORMAL_TEX"] = p


material_folder = input_path / "materials"
material_folder.mkdir(parents=True, exist_ok=True)
for name, material_data in material_maps.items():
	data = {}
	data["values"] = []

	paths = []
	for material_type, material_path in material_data.items():
		material_value = {}
		material_value["type"] = "texture_asset"
		material_value["code_name"] = material_type
		material_value["value"] = "texture_" + material_path.stem
		data["values"].append(material_value)
		paths.append(material_path.resolve().parent)

	paths_set = set(paths)
	if (len(paths_set) == 1):
		paths = list(paths_set)
		root = material_folder / Path(*paths[0].relative_to(input_path).parts[1:])
		root.mkdir(parents=True, exist_ok=True)
		file = root / f'{name}.material.json'
		shader_name = "shader_color"
		for name, path in shader_map.items():
			if path in str(paths[0].relative_to(input_path)):
				shader_name = name
		data["shader_asset"] = shader_name
	else:
		file = material_folder / f'{name}.material.json'
	file.write_text(json.dumps(data, indent='\t', sort_keys=True))

