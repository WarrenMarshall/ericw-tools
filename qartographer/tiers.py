#!/usr/bin/env python3
"""QBSP-only tiers; failed evidence is retained and never promoted."""
import argparse,hashlib,json,os,re,shutil,struct,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
sys.dont_write_bytecode=True
from deploy import DEFAULT,sha
HERE=Path(__file__).resolve().parent
FAST='qbsp.duplicatePlanes:qbsp.emptyBrush:testmapsQ1.simpleSealed'
CORRECTNESS=FAST+':testmapsQ1.chopNoChange:testmapsQ1.cube:testmapsQ1.cubes:testmapsQ1.brushClippingOrder:testmapsQ1.angledBrush:testmapsQ1.sealingContents:testmapsQ1.detailTouchingWater:testmapsQ1.hull1ContentTypes:testmapsQ1.sealingHull1Onnode:testmapsQ1.csg'
def invoke(cmd,log):
    r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
    log.write_text(r.stdout+r.stderr)
    assert r.returncode==0,(cmd,r.returncode,'see '+str(log))
def lumps(p):
    b=p.read_bytes();return b[:4],{i:b[o:o+n] for i in range(15) for o,n in [struct.unpack_from('<ii',b,4+i*8)]}
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tier',type=int,choices=[1,2,3],required=True)
    ap.add_argument('--work',type=Path,required=True);ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--engine',type=Path,default=Path.home()/'.steam/steam/steamapps/common/Quake/qrustyquake')
    ap.add_argument('--id1',type=Path,default=Path.home()/'.local/share/Steam/steamapps/common/Quake/id1')
    ap.add_argument('--utilities',type=Path,default=DEFAULT.parent)
    ap.add_argument('--performance-note',default='')
    ap.add_argument('--resume-native',type=Path,help='Validate completed native saves after a shutdown failure; reuse earlier passing checks')
    a=ap.parse_args();a.results=a.results.resolve();a.work=a.work.resolve()
    if a.resume_native:
        report=json.loads((a.results/'tier-results.json').read_text())
        manifest=json.loads((a.work/'patched-manifest.json').read_text())
        fixed=Path(manifest['binary']);stock=a.work/'pristine-build/qbsp/qbsp'
        assert report['tier']==3 and report['binary_sha256']==sha(fixed)==manifest['binary_sha256']
        core=json.loads((a.results/'collision/results.json').read_text())
        assert core['acceptance']=='PASS' and core['full'] and core['patched']['sha256']==sha(fixed)
        assert report['upstream_tests']==13 and len(report['thin'])==4 and report['compatibility']
        native=a.resume_native.resolve()
        expected=(HERE/'fixtures/roller-direct.map').read_text()+'\n{\n"classname" "info_player_start"\n"origin" "-1400 -1664 180"\n"angle" "90"\n}\n'
        for label in ['stock','fixed']:assert (native/'id1/maps'/(label+'.map')).read_text()==expected
        banner=next(line for line in manifest['identity'].splitlines() if line.startswith('Qartographer qqbsp,'))
        assert banner in (native/'fixed-compile.log').read_text()
        assert sha(native/'id1/maps/ordinary.bsp')==sha(a.results/'compatibility/ordinary.bsp')
        from native import validate_saved
        report['native']=validate_saved(stock,fixed,a.engine.resolve(),a.id1.resolve(),native,shutdown='Resumed completed saves after engine shutdown timeout; test processes forcibly cleaned up')
        report['acceptance']='PASS'
        (a.results/'tier-results.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2));return
    assert not a.results.exists(),'Use a new results directory'
    a.results.mkdir(parents=True)
    m=json.loads((a.work/'patched-manifest.json').read_text());binary=Path(m['binary']);stock=a.work/'pristine-build/qbsp/qbsp'
    assert sha(binary)==m['binary_sha256']
    lock=json.loads((HERE/'baseline.json').read_text())
    for name,want in lock['fixtures'].items():assert sha(HERE/'fixtures'/name)==want,name
    report={'tier':a.tier,'binary_sha256':sha(binary),'source':m['downstream'],'acceptance':'INCOMPLETE'}
    receipt=a.results/'tier-results.json'
    receipt.write_text(json.dumps(report,indent=2)+'\n')
    identity=subprocess.run([str(binary),'-help'],capture_output=True,text=True)
    assert identity.returncode==0 and 'Qartographer qqbsp,' in identity.stdout and 'patches=P1' in identity.stdout
    (a.results/'identity.txt').write_text(identity.stdout+identity.stderr)
    tests=a.work/'patched-build/qartographer/qqbsp_tests'
    xml=a.results/'upstream.xml'
    invoke([tests,'--gtest_filter='+ (FAST if a.tier==1 else CORRECTNESS),'--gtest_output=xml:'+str(xml)],a.results/'upstream.log')
    x=ET.parse(xml).getroot()
    assert int(x.attrib['tests'])==(3 if a.tier==1 else 13),x.attrib
    assert int(x.attrib['failures'])==0 and int(x.attrib.get('disabled','0'))==0
    assert not x.findall('.//skipped'),'Unexpected skipped test'
    report['upstream_tests']=int(x.attrib['tests'])
    if a.tier==1:
        invoke([sys.executable,HERE/'wildspline_bsp_collision_compile.py',binary,a.results/'reduced'],a.results/'reduced.log')
    else:
        invoke([sys.executable,HERE/'regress.py',stock,binary,a.results/'collision','--full'],a.results/'collision.log')
        thin=a.results/'thin';shutil.copytree(HERE/'fixtures/thin',thin)
        invoke([sys.executable,HERE/'thin_oracle.py',binary,thin],a.results/'thin.log')
        report['thin']=json.loads((thin/'results.json').read_text())
        # Record timing observations, never interpret a noisy timing difference
        # as geometric failure. Large differences need an explicit review note.
        timing={}
        for label in ['pristine','patched']:
            log=(a.results/'collision'/label/'full/full-on-compile.log').read_text()
            timing[label]=float(re.findall(r'([0-9.]+)s seconds elapsed',log)[-1])
        timing['ratio']=timing['patched']/timing['pristine']
        report['full_compile_seconds']=timing
        report['performance_note']=a.performance_note
        receipt.write_text(json.dumps(report,indent=2)+'\n')
        if a.tier==3 and timing['ratio']>1.25 and not a.performance_note:
            raise RuntimeError('PERFORMANCE REVIEW REQUIRED (not a collision failure): inspect timings; rerun with --performance-note after investigating')
    if a.tier==3:
        # Stock VIS/LIGHT are consumers only. Work on a disposable generated copy.
        compat=a.results/'compatibility';compat.mkdir()
        p=compat/'ordinary.map'
        p.write_text((HERE.parent/'testmaps/qbsp_simple_sealed.map').read_text()+'\n{\n"classname" "light"\n"origin" "-16 -80 128"\n"light" "300"\n}\n')
        invoke([binary,'-notex','-nopercent',p],compat/'compile.log')
        bsp=p.with_suffix('.bsp');version,before=lumps(bsp);assert version==struct.pack('<i',29),'Not ordinary BSP29'
        consumers={}
        for tool,flags in [('vis',['-fast','-nopercent']),('light',['-nopercent'])]:
            exe=(a.utilities/tool).resolve()
            invoke([exe,*flags,bsp],compat/(tool+'.log'))
            consumers[tool]={'path':str(exe),'sha256':sha(exe)}
        version,after=lumps(bsp)
        assert after[4] and after[8],'Missing visibility/light data'
        for i in [1,5,9,14]:assert before[i]==after[i],('consumer changed collision/model lump',i)
        report['compatibility']={'format':'BSP29','consumers':consumers,'visibility_bytes':len(after[4]),'light_bytes':len(after[8])}
        receipt.write_text(json.dumps(report,indent=2)+'\n')
        from native import run_native
        report['native']=run_native(stock,binary,a.engine.resolve(),a.id1.resolve(),a.results/'native',bsp)
    report['acceptance']='PASS'
    receipt.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
