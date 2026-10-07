"""Synchronize the validated LIVE political increment, then check every byte."""
import hashlib, json, shutil
from pathlib import Path
from deploy_local import ROOT, SOURCE, TARGET, inventory, main as verify

def main():
 record=json.loads((ROOT/'docs/yugoslav_politics_sources.json').read_text())
 for name in ['yugoslav_politics_validation.json','yugoslav_politics_endgame_regression.json']:
  report=json.loads((ROOT/'docs'/name).read_text());assert report['static_and_model_validation']=='passed'
  assert Path(report['validated_mod_root']).resolve()==TARGET.resolve(strict=True)
 for relative,digest in record['deployed_sha256'].items():
  installed=TARGET/relative;assert hashlib.sha256(installed.read_bytes()).hexdigest()==digest
  source=SOURCE/relative;assert source.resolve().is_relative_to(SOURCE.resolve())
  source.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(installed,source)
 verify()
 deployed=json.loads((ROOT/'docs/local_deployment.json').read_text());assert not deployed['copied_absolute_paths'] and not deployed['runtime_only_files']
 hashes=inventory(TARGET);assert hashes==inventory(SOURCE)
 report={'version':record['version'],'runtime':str(TARGET),'all_source_runtime_files_identical':True,'file_count':len(hashes),'changed_relative_paths':record['changed_relative_paths'],'deployed_absolute_paths':record['deployed_absolute_paths'],'source_runtime_sha256':hashes,'launcher_descriptor':str(TARGET.parent/'make_serbia_great_again.mod'),'Workshop_id':'3813570241','validation_order':'LIVE install and both targeted validations before source sync','actual_engine_test':'Reserved by user; game and saves untouched'}
 (ROOT/'docs/yugoslav_politics_sync.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f'{len(hashes)} identical source/runtime files; 0 further deployment changes.')

if __name__=='__main__':main()
