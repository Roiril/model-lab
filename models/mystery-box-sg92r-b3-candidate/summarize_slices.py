from pathlib import Path
import zipfile,json,re,collections,hashlib,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent;rows=[];Q=R/'print_qa';Q.mkdir(exist_ok=True)
for path in sorted((R/'slice_checks').glob('*/*.3mf')):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        cfg=json.loads(z.read('Metadata/project_settings.config'));g=z.read('Metadata/plate_1.gcode').decode('utf8')
        feature=collections.Counter(re.findall(r'; FEATURE: ([^\n]+)',g));paints={}
        for n in z.namelist():
            if n.endswith('.model'):
                root=ET.fromstring(z.read(n));paints[n]=dict(collections.Counter(x.get('paint_supports') for x in root.iter() if x.get('paint_supports')))
        stats={}
        for label in ['total layer number','max_z_height','total filament weight [g]','model printing time']:
            match=re.search(r'^; '+re.escape(label)+r':?\s*([^\n]+)',g,re.M);stats[label]=match.group(1).strip().lstrip(': ') if match else None
        for n in ['Metadata/plate_1.png','Metadata/top_1.png']:
            if n in z.namelist():(Q/(path.stem+'_'+Path(n).name)).write_bytes(z.read(n))
        expected=path.stem in ['plate_02_cassette','plate_04_support_tests']
        assert cfg.get('enable_support')==('1' if expected else '0'),cfg.get('enable_support')
        actual=any('Support' in f for f in feature)
        assert actual==expected,(path.stem,dict(feature))
        if expected:
            assert cfg.get('support_type')=='normal(manual)'
            assert cfg.get('independent_support_layer_height')=='0'
            assert any(v.get('4',0)>0 for v in paints.values()),paints
        meshstats=ET.fromstring(z.read('Metadata/model_settings.config')).findall('.//mesh_stat')
        rows.append(dict(plate=path.stem,printer_profile='Bambu Lab X1 Carbon 0.4 nozzle (locally selected saved profile)',material='Bambu PLA Basic',slicer='Bambu Studio02.03.01.51',layer_height=cfg.get('layer_height'),wall_loops=cfg.get('wall_loops'),supports_enabled=expected,actual_support_paths=actual,support_type=cfg.get('support_type'),statistics=stats,feature_blocks=dict(feature),paint_counts=paints,mesh_statistics=[dict(x.attrib) for x in meshstats],input_plate_sha256=hashlib.sha256((R/'plates'/path.name).read_bytes()).hexdigest(),crc_ok=True))
report={'physical_tested':False,'note':'Actual offline slices, no printer connection or print. G-code and sliced machine-specific3MF excluded. Support removal, fits and bridging remain untested. Manual painted support paths on plate02 and support trial plate04; independent support layer height disabled.','plates':rows}
(R/'slicer_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(rows,ensure_ascii=False,indent=2))
