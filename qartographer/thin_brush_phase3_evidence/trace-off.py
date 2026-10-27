import pathlib,subprocess,shutil
r=pathlib.Path('/tmp/qqbsp-phase3')
for name in ['p1','uniform']:
 d=r/('trace-off-'+name);d.mkdir(exist_ok=True);m=d/'full-off.map';shutil.copyfile('/home/warrenmarshall/dev/ericw-tools/qartographer/fixtures/full-off.map',m)
 with (d/'stdout.log').open('w') as f:subprocess.run([str(r/(name+'-final-trace-qqbsp')),'-bsp2','-notex','-nopercent','-chopfragment','-threads','1','-loghulls',str(m)],stdout=f,stderr=subprocess.STDOUT,check=True)
 print(name,'off traced',flush=True)
