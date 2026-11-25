import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import refresh

class RefreshTests(unittest.TestCase):
 def test_schema_host_and_row_limit(self):
  header=['timestamp','original','digest']
  rows=[header,['20000102030405','http://example.ca/','A'],['20000102030405','http://evil.ca/','B']]
  self.assertEqual(len(refresh.parse_captures(rows,'www.example.ca/',20)),1)
  with self.assertRaises(ValueError):refresh.parse_captures(rows,'example.ca/',1)
  with self.assertRaises(ValueError):refresh.parse_captures([header,['20000230030405','http://example.ca/','A']],'example.ca/',10)
 def test_extra_profile_and_source_failure_preserve_existing_snapshot(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);out=root/'web/data';out.mkdir(parents=True)
   old={'existing':{'2000':{'count':1,'versions':1,'first':['20000102030405','http://example.ca/'],'last':['20000102030405','http://example.ca/']}}}
   config={'networks':[{'id':'existing','homepages':['example.ca/']},{'id':'extra','homepages':['extra.ca/']}],'sample_years':[2000],'max_capture_rows':10}
   (root/'web/config.json').write_text(json.dumps(config));(out/'captures.json').write_text(json.dumps(old));(out/'status.json').write_text(json.dumps({'retrieved':'2020-01-01'}))
   before={p.name:p.read_bytes() for p in out.iterdir()}
   with patch.object(refresh,'ROOT',root),patch.object(refresh,'configuration',return_value=config),patch.object(refresh,'captures',side_effect=OSError('upstream')):
    with self.assertRaises(ValueError):refresh.main()
   self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})
   with patch.object(refresh,'ROOT',root),patch.object(refresh,'configuration',return_value=config),patch.object(refresh,'captures',return_value=[('20010102030405','http://extra.ca/','B')]),patch.object(refresh,'read_capture',return_value=None):refresh.main(only_new=True)
   saved=json.loads((out/'captures.json').read_text());status=json.loads((out/'status.json').read_text())
   self.assertEqual(saved['existing'],old['existing']);self.assertIn('extra',saved);self.assertEqual(status['retrieved'],'2020-01-01');self.assertEqual(status['count'],2)
 def test_atomic_write_restores_all_files_on_late_failure(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td);(out/'a.json').write_text('old-a');(out/'b.json').write_text('old-b')
   real=refresh.os.replace;calls=0
   def fail_second(a,b):
    nonlocal calls
    calls+=1
    if calls==2:raise OSError('disk failure')
    return real(a,b)
   with patch.object(refresh.os,'replace',side_effect=fail_second):
    with self.assertRaises(OSError):refresh.atomic_documents(out,{'a.json':{'new':1},'b.json':{'new':2}})
   self.assertEqual((out/'a.json').read_text(),'old-a');self.assertEqual((out/'b.json').read_text(),'old-b')

if __name__=='__main__':unittest.main()
