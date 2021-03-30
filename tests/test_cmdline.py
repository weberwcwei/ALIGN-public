import pytest
import align
import os
import pathlib
import shutil

examples = [('inverter_v1',1,False),
            ('buffer',1,False),
            ('five_transistor_ota',1,False),
            ('five_transistor_ota',2,False),
            ('cascode_current_mirror_ota',1,False),
            #Hierarchical block fail with num_placements > 1
            #('cascode_current_mirror_ota',2,False),
            ('telescopic_ota',1,True),
            ('high_speed_comparator',1,True),
            ('adder',1,False)]

ALIGN_HOME = pathlib.Path(__file__).resolve().parent.parent

if 'ALIGN_HOME' in os.environ:
    assert pathlib.Path(os.environ['ALIGN_HOME']).resolve() == ALIGN_HOME
else:
    os.environ['ALIGN_HOME'] = str(ALIGN_HOME)

if 'LD_LIBRARY_PATH' not in os.environ:
    os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib/lpsolve/lp_solve_5.5.2.5_dev_ux64'

@pytest.mark.parametrize( "design,num_placements,PDN_mode", examples)
def test_cmdline(design,num_placements,PDN_mode):
    run_dir = ALIGN_HOME / 'tests' / 'tmp'

    if run_dir.exists():
        assert run_dir.is_dir()
        shutil.rmtree(run_dir)

    run_dir.mkdir(parents=True, exist_ok=False)
    os.chdir(run_dir)

    design_dir = ALIGN_HOME / 'examples' / design
    pdk_dir = ALIGN_HOME / 'pdks' / 'FinFET14nm_Mock_PDK'
    args = [str(design_dir), '-f', str(design_dir / f"{design}.sp"), '-s', design, '-p', str(pdk_dir), '-flat',  str(0), '--check', '-v', 'INFO', '-l', 'INFO', '-n', str(num_placements)]
    if PDN_mode:
        args.append( '--PDN_mode')

    results = align.CmdlineParser().parse_args(args)

    for result in results:
        _, variants = result
        for (k,v) in variants.items():
            print(k,v)
            assert 'errors' in v
            assert v['errors'] == 0
