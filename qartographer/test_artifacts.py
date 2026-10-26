"""Packaging must preserve development symbols and bind validation to actual bytes."""
import contextlib,io,json,struct,subprocess,tempfile,unittest
from pathlib import Path
from artifacts import compare_bsp,elf_profile,load_artifact,prepare,sha

class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.work=Path(self.temp.name);src=self.work/'test.cc'
        src.write_text('#include <cstdio>\nint main(){std::puts("Qartographer qqbsp, upstream=test, downstream=test, patches=P1");}\n')
        self.binary=self.work/'development/qqbsp';self.binary.parent.mkdir()
        subprocess.run(['c++','-O2','-g',str(src),'-o',str(self.binary)],check=True)
        self.original=sha(self.binary)
        identity=subprocess.check_output([str(self.binary),'-help'],text=True)
        self.manifest=self.work/'patched-manifest.json'
        self.manifest.write_text(json.dumps({'binary':str(self.binary),'binary_sha256':self.original,'identity':identity,'runtime_sha256':{}}))
        with contextlib.redirect_stdout(io.StringIO()):self.package=prepare(self.work)

    def test_preserves_debug_build_and_loaded_sections(self):
        deployed=Path(self.package['binary'])
        self.assertEqual(sha(self.binary),self.original)
        self.assertGreater(elf_profile(self.binary)['debug_bytes'],0)
        self.assertEqual(elf_profile(deployed)['debug_bytes'],0)
        self.assertEqual(elf_profile(self.binary)['alloc'],elf_profile(deployed)['alloc'])
        self.assertNotEqual(sha(deployed),self.original)
        self.assertLess(deployed.stat().st_size,self.binary.stat().st_size)
        self.assertEqual(load_artifact(self.work,'deployment')['binary_sha256'],sha(deployed))

    def test_rejects_tampered_deployment_artifact(self):
        with Path(self.package['binary']).open('ab') as f:f.write(b'changed')
        with self.assertRaises(AssertionError):load_artifact(self.work,'deployment')

    def test_rejects_stale_development_manifest(self):
        m=json.loads(self.manifest.read_text());m['changed']='new build record'
        self.manifest.write_text(json.dumps(m))
        with self.assertRaises(AssertionError):load_artifact(self.work,'deployment')

class BspComparisonTests(unittest.TestCase):
    def fixture(self,marks,offsets=(-1,-1),light=b''):
        # Minimal storage-level fixture; this tests comparison, not geometry.
        lumps=[b'']*15
        faces=[bytearray(20),bytearray(20)]
        for f,o in zip(faces,offsets):struct.pack_into('<i',f,16,o)
        lumps[7]=b''.join(faces);lumps[8]=light
        leaf=bytearray(28);struct.pack_into('<HH',leaf,20,0,len(marks))
        lumps[10]=bytes(leaf);lumps[11]=struct.pack('<'+'H'*len(marks),*marks)
        b=bytearray(124);struct.pack_into('<i',b,0,29)
        for i,data in enumerate(lumps):
            struct.pack_into('<ii',b,4+i*8,len(b),len(data));b.extend(data)
        return bytes(b)

    def compare(self,a,b,pass_expected):
        with tempfile.TemporaryDirectory() as d:
            left,right=Path(d)/'a.bsp',Path(d)/'b.bsp';left.write_bytes(a);right.write_bytes(b)
            if pass_expected:self.assertFalse(compare_bsp(left,right)['byte_identical'])
            else:
                with self.assertRaises(AssertionError):compare_bsp(left,right)

    def test_leaf_order_preserves_membership_and_duplicates(self):
        self.compare(self.fixture([0,1]),self.fixture([1,0]),True)
        self.compare(self.fixture([0,1]),self.fixture([1,1]),False)

    def test_light_allocation_preserves_pixels_and_other_face_fields(self):
        a=self.fixture([0,1],(0,3),b'aaabbb');b=self.fixture([0,1],(3,0),b'bbbaaa')
        self.compare(a,b,True)
        self.compare(a,self.fixture([0,1],(3,0),b'bbbaac'),False)
        damaged=bytearray(b);face_offset=struct.unpack_from('<i',damaged,4+7*8)[0];damaged[face_offset]^=1
        self.compare(a,bytes(damaged),False)

if __name__=='__main__':unittest.main()
