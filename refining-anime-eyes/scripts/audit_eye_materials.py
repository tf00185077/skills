"""Read-only Blender material wiring audit. Never saves the current .blend."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import sys

import bpy

LIMITATIONS = (
    'Static saved/in-memory node wiring and socket defaults only; linked defaults are not evaluated. '
    'Mix Shader weights describe local shader mixing, not final pixel brightness or eye quality. '
    'No render, lighting, compositing, animation, driver, modifier, geometry-node, or per-pixel evaluation. '
    'Polygon usage is the original mesh, not the evaluated render mesh. Group bindings are structural. '
    'The on-disk input SHA-256 does not prove an unsaved in-memory scene matches that file. '
    'All existing output paths are refused, including earlier JSON reports. No blend file is saved.'
)

def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def plain(value):
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, bpy.types.ID):
        return {'datablock_name': value.name, 'type': type(value).__name__}
    try:
        return [plain(x) for x in value]
    except TypeError:
        return str(value)

def socket_index(socket, sockets):
    return next((i for i, candidate in enumerate(sockets) if candidate == socket), None)

def link_info(link):
    return {
        'from_node': link.from_node.name,
        'from_socket': link.from_socket.name,
        'from_socket_index': socket_index(link.from_socket, link.from_node.outputs),
        'from_socket_identifier': link.from_socket.identifier,
        'to_node': link.to_node.name,
        'to_socket': link.to_socket.name,
        'to_socket_index': socket_index(link.to_socket, link.to_node.inputs),
        'to_socket_identifier': link.to_socket.identifier,
        'is_valid': link.is_valid,
        'is_muted': getattr(link, 'is_muted', False),
    }

def socket_info(index, socket):
    return {'index': index, 'name': socket.name, 'identifier': socket.identifier,
            'type': socket.bl_idname, 'enabled': socket.enabled,
            'value': plain(getattr(socket, 'default_value', None)),
            'is_linked': socket.is_linked, 'links': [link_info(link) for link in socket.links],
            'value_role': 'ignored_default_when_linked' if socket.is_linked else 'socket_default'}

def properties(owner, names):
    return {name: plain(getattr(owner, name)) for name in names if hasattr(owner, name)}

def tree_info(tree, ancestors=()):
    if tree is None:
        return None
    identity = tree.as_pointer()
    if identity in ancestors:
        return {'name': tree.name, 'cycle_reference': True}
    ancestry = (*ancestors, identity)
    result = {'name': tree.name, 'nodes': [], 'links': [link_info(link) for link in tree.links],
              'active_material_outputs': [], 'animation_present': tree.animation_data is not None}
    for node in tree.nodes:
        record = {'name': node.name, 'type': node.bl_idname, 'label': node.label,
                  'mute': node.mute, 'inputs': [socket_info(i, s) for i, s in enumerate(node.inputs)],
                  'outputs': [socket_info(i, s) for i, s in enumerate(node.outputs)],
                  'settings': properties(node, ['operation', 'blend_type', 'data_type', 'attribute_name', 'uv_map', 'interpolation', 'extension', 'projection']),
                  'internal_links': [link_info(link) for link in node.internal_links]}
        if hasattr(node, 'is_active_output'):
            record['is_active_output'] = node.is_active_output
            record['target'] = getattr(node, 'target', None)
            if node.bl_idname == 'ShaderNodeOutputMaterial' and node.is_active_output:
                result['active_material_outputs'].append({'name': node.name, 'target': record['target'], 'inputs': record['inputs']})
        if node.bl_idname == 'ShaderNodeMixShader':
            factor = node.inputs[0]
            constant = None if factor.is_linked else max(0.0, min(1.0, float(factor.default_value)))
            record['mix_shader'] = {
                'factor': record['inputs'][0],
                'shader_weights': [
                    {'input_index': 1, 'expression': '1 - clamp(Factor, 0, 1)', 'weight': None if constant is None else 1 - constant, 'links': record['inputs'][1]['links']},
                    {'input_index': 2, 'expression': 'clamp(Factor, 0, 1)', 'weight': constant, 'links': record['inputs'][2]['links']}],
                'meaning': 'Local shader mix only; no final pixel brightness contribution is inferred.'}
        if node.bl_idname in ('ShaderNodeBsdfPrincipled', 'ShaderNodeEmission'):
            record['shading_inputs'] = record['inputs']
        if hasattr(node, 'color_ramp'):
            record['color_ramp'] = {'interpolation': node.color_ramp.interpolation, 'elements': [{'position': e.position, 'color': list(e.color)} for e in node.color_ramp.elements]}
        if node.bl_idname == 'ShaderNodeTexImage':
            img = node.image
            record['image'] = None if img is None else {
                'name': img.name, 'color_space': img.colorspace_settings.name,
                'packed': bool(img.packed_file or len(img.packed_files)),
                'size': list(img.size), 'path': img.filepath,
                'resolved_path': bpy.path.abspath(img.filepath, library=img.library),
                'source': img.source, 'alpha_mode': img.alpha_mode}
        if node.bl_idname == 'ShaderNodeGroup' and node.node_tree:
            group = node.node_tree
            record['group_input_bindings'] = []
            for index, external in enumerate(node.inputs):
                matching = []
                for inside in group.nodes:
                    if inside.bl_idname == 'NodeGroupInput':
                        for inner_index, inner in enumerate(inside.outputs):
                            if inner.identifier == external.identifier:
                                matching.append({'node': inside.name, 'output_index': inner_index, 'identifier': inner.identifier, 'links': [link_info(link) for link in inner.links]})
                record['group_input_bindings'].append({'external_input': record['inputs'][index], 'internal_group_input_outputs': matching})
            record['node_tree'] = tree_info(group, ancestry)
        result['nodes'].append(record)
    return result

def object_info(obj, explicitly_selected):
    counts = Counter(poly.material_index for poly in getattr(obj.data, 'polygons', ()))
    return {'name': obj.name, 'type': obj.type, 'explicitly_selected': explicitly_selected,
            'polygon_usage_basis': 'original mesh polygons; modifiers are not evaluated',
            'polygon_count': sum(counts.values()),
            'unassigned_polygon_material_indices': {str(i): count for i, count in counts.items() if i >= len(obj.material_slots)},
            'material_slots': [{'index': i, 'link': slot.link, 'material': slot.material.name if slot.material else None,
                                'polygon_count': counts[i]} for i, slot in enumerate(obj.material_slots)]}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, epilog=LIMITATIONS)
    parser.add_argument('--material', action='append', default=[], metavar='NAME', help='Exact material name; repeatable. Includes all objects using it in a slot.')
    parser.add_argument('--object', action='append', default=[], metavar='NAME', help='Exact object name; repeatable. Audits all materials in its slots.')
    parser.add_argument('--output', required=True, type=Path, metavar='JSON', help='New .json report path; existing files are never overwritten.')
    args = parser.parse_args(argv)
    if not args.material and not args.object:
        parser.error('At least one --material or --object selector is required.')
    missing = [f'material {name!r}' for name in args.material if name not in bpy.data.materials]
    missing += [f'object {name!r}' for name in args.object if name not in bpy.data.objects]
    if missing:
        parser.error('Selector not found: ' + ', '.join(missing))
    target = args.output.expanduser().absolute()
    # lexists covers dangling symlinks; exclusive creation closes overwrite races.
    if os.path.lexists(target):
        parser.error(f'Refusing existing output path: {target}')
    if target.suffix.lower() != '.json':
        parser.error('Output must have a .json extension.')
    source = Path(bpy.data.filepath).resolve() if bpy.data.filepath else None
    before = sha256(source) if source and source.is_file() else None
    material_names = set(args.material)
    for name in args.object:
        material_names.update(slot.material.name for slot in bpy.data.objects[name].material_slots if slot.material)
    objects = [obj for obj in bpy.data.objects if obj.name in args.object or any(slot.material and slot.material.name in material_names for slot in obj.material_slots)]
    report = {
        'schema_version': 1, 'blender_version': bpy.app.version_string,
        'input': {'path': str(source) if source else None, 'sha256_before': before, 'is_dirty': bpy.data.is_dirty},
        'selectors': {'materials': args.material, 'objects': args.object},
        'limitations': LIMITATIONS, 'objects': [object_info(obj, obj.name in args.object) for obj in objects],
        'materials': []}
    for name in sorted(material_names):
        mat = bpy.data.materials[name]
        report['materials'].append({'name': name, 'use_nodes': mat.use_nodes,
            'transparency': properties(mat, ['surface_render_method', 'blend_method', 'shadow_method', 'alpha_threshold', 'use_transparent_shadow', 'use_transparency_overlap', 'use_backface_culling', 'use_backface_culling_shadow', 'use_backface_culling_lightprobe', 'show_transparent_back', 'use_screen_refraction', 'use_raytrace_refraction', 'thickness_mode']),
            'diffuse_color': list(mat.diffuse_color), 'node_tree': tree_info(mat.node_tree)})
    after = sha256(source) if source and source.is_file() else None
    report['input'].update(sha256_after=after, unchanged=(before == after) if before else None)
    if before is not None and before != after:
        raise RuntimeError('Input file changed during audit; no success report written.')
    payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8') as output:
        output.write(payload + '\n')
    print(f'EYE_MATERIAL_AUDIT {target}', flush=True)
    return report

if __name__ == '__main__':
    try:
        main(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    except SystemExit as exc:
        if exc.code:
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(int(exc.code))
    except Exception as exc:
        print(f'EYE_MATERIAL_AUDIT ERROR: {exc}', file=sys.stderr, flush=True)
        sys.stdout.flush()
        os._exit(1)
