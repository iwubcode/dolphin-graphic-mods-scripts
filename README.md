# dolphin-graphic-mods-scripts
Scripts to help create graphics mods

**color_table_to_material.py** - takes a yaml file as input with a path to an color mask (or alternatively known as an [id matte](https://en.wikipedia.org/wiki/Cryptomatte)) + a folder containing one or more folders with materials in them (an example would be extracting a PBR series of textures that you find on ).  Can also specify the starting map to blend with.

Example:

```
material_library_path: "C:/texture_library"
output:
    directory: "C:/output_location"
    starting:
        normal: "C:/my_normal_map.png"
        occlusion: "C:/my_ao_map.png"
masks:
    "C:/my_color_mask.png":
        colors:
            "#beac64":
                material: Fabric_Silk_001_SD
                scale: 0.5
                blend:
                    normal: 0.25
                    occlusion: 0.5
            "#efebda":
                material: Fabric019_2K-JPG
                scale: 0.15
                blend:
                    normal: 0.25
                    occlusion: 0.5
            "#beac64":
                material: Fabric019_2K-JPG
                scale: 0.25
                blend:
                    normal: 0.3
                    occlusion: 0.5
            "#705e33":
                material: outdoor-polyester-fabric1-bl
                blend:
                    normal: 0.25
                    occlusion: 0.5
```

**assets-to-metadata-graphics-mod.py** - generates a metadata file from assets (textures, shaders, and materials), ready to be used as a custom pipeline (see Dolphin [PR #11300](https://github.com/dolphin-emu/dolphin/pull/11300))
**textures-to-material.py** - generates material json for textures (files that end in `_norm` or `_ao`, etc), ready to be incorporated into a custom pipeline (see Dolphin [PR #11300](https://github.com/dolphin-emu/dolphin/pull/11300))