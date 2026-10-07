from pathlib import Path
EXCLUDED={'machine_x1c_flat.json','filament_pla_flat.json','process_manual_support.json','process_no_support.json','slice_run.json','package_report.json','library_identity.json','manifest_sha256.json','protected_model_hashes.json'}
SUBDIRS={'stl','coupons','plates','print_qa','reference','slow_open_demo'}
def release_files(root):
    return sorted(p for p in Path(root).rglob('*') if p.is_file() and not any(x in ('__pycache__','slice_checks') for x in p.relative_to(root).parts) and (len(p.relative_to(root).parts)>1 and p.relative_to(root).parts[0] in SUBDIRS or p.parent==Path(root) and p.suffix.lower() in ('.py','.json','.png','.svg','.md','.txt','.html') and p.name not in EXCLUDED or p.name=='editable_cube_v6.blend') and p.suffix not in ('.blend1','.pyc'))
