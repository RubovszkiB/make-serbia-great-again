"""Mirror only the fully validated LIVE increment, then verify all installed hashes."""
import hashlib,json,shutil
from pathlib import Path
from deploy_local import ROOT,SOURCE,TARGET,inventory,main as verify

def main():
 record=json.loads((ROOT/'docs/balkan_mini_sources.json').read_text())
 reports=['balkan_mini_validation.json','balkan_mini_phase1_regression.json','balkan_mini_kosovo_regression.json','balkan_mini_bosnia_regression.json','balkan_mini_rearmament_regression.json']
 for name in reports:
  report=json.loads((ROOT/'docs'/name).read_text());assert 'passed' in [report.get(k) for k in ['static_and_model_validation','static_validation']]
  assert Path(report['validated_mod_root']).resolve()==TARGET.resolve(strict=True)
 for relative,digest in record['deployed_sha256'].items():
  live=TARGET/relative;assert hashlib.sha256(live.read_bytes()).hexdigest()==digest
  dest=SOURCE/relative;assert dest.resolve().is_relative_to(SOURCE.resolve());dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(live,dest)
 verify();deployment=json.loads((ROOT/'docs/local_deployment.json').read_text());assert not deployment['copied_absolute_paths'] and not deployment['runtime_only_files']
 hashes=inventory(TARGET);assert hashes==inventory(SOURCE) and len(hashes)==667
 (ROOT/'docs/balkan_mini_sync.json').write_text(json.dumps({'version':'0.17.0','runtime':str(TARGET),'all_source_runtime_files_identical':True,'file_count':len(hashes),'deployed_absolute_paths':record['deployed_absolute_paths'],'source_runtime_sha256':hashes,'validation_reports':reports,'Workshop_id':'3813570241','engine_test':'NOT RUN; user game and saves untouched'},indent=2)+'\n')
 print('LIVE/source verified: 667 identical files; launcher preserved. No additional deployment writes.')

if __name__=='__main__':main()
