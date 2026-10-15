import importlib.util
import itertools
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v2_plate_search", HERE / "plate.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
groups, _ = P.production_groups()
carriers = [part for parts in groups.values() for part in parts if part[0].startswith("frame__carrier_")]
base = {name: [part for part in parts if not part[0].startswith("frame__carrier_")]
        for name, parts in groups.items()}
for assignment in itertools.product(groups, repeat=len(carriers)):
    candidate = {name: list(parts) for name, parts in base.items()}
    for part, group in zip(carriers, assignment):
        candidate[group].append(part)
    try:
        layouts = {name: P.arrange(parts)[1] for name, parts in candidate.items()}
    except ValueError:
        continue
    print({part[0]: group for part, group in zip(carriers, assignment)})
    print({name: len(parts) for name, parts in layouts.items()})
    break
else:
    raise RuntimeError("No four-plate carrier assignment fits")
