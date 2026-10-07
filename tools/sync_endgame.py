"""Synchronize only the already validated endgame deployment, then verify all files."""
from pathlib import Path
import hashlib,json,shutil
from deploy_local import SOURCE,TARGET,ROOT,inventory,main as verify_deployment

def main():
    record=json.loads((ROOT/'docs/endgame_sources.json').read_text())
    report=json.loads((ROOT/'docs/endgame_validation.json').read_text())
    assert report['static_and_model_validation']=='passed' and not report['prepared_overlay_only']
    assert Path(report['validated_mod_root']).resolve()==TARGET.resolve(strict=True)
    for suite in ['new_order','pact_war','post_bosnia','phase1','economic']:
        r=json.loads((ROOT/f'docs/endgame_regression_{suite}.json').read_text())
        assert 'passed' in [r.get(k) for k in ['validation','static_validation','static_and_model_validation']]
        assert Path(r['validated_mod_root']).resolve()==TARGET.resolve()
    for relative,digest in record['deployed_sha256'].items():
        source=TARGET/relative;target=SOURCE/relative
        assert hashlib.sha256(source.read_bytes()).hexdigest()==digest,relative
        assert target.resolve().is_relative_to(SOURCE.resolve())
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    verify_deployment() # Existing primary-runtime workflow: no extra copy should be needed.
    deployed=json.loads((ROOT/'docs/local_deployment.json').read_text())
    assert not deployed['copied_absolute_paths'] and not deployed['runtime_only_files']
    runtime=inventory(TARGET);assert runtime==inventory(SOURCE)
    sync={'version':record['version'],'runtime':str(TARGET),'launcher_descriptor':str(TARGET.parent/'make_serbia_great_again.mod'),'all_source_runtime_files_identical':True,'file_count':len(runtime),'changed_relative_paths':record['changed_relative_paths'],'deployed_absolute_paths':record['deployed_absolute_paths'],'source_runtime_sha256':runtime,'Workshop_id':'3813570241','validation_order':'LIVE first, then source sync and existing deploy_local hash verification','actual_engine_test':'Reserved by user; game and saves untouched'}
    (ROOT/'docs/endgame_sync.json').write_text(json.dumps(sync,indent=2)+'\n')
    print(f'Confirmed {len(runtime)} identical files. LIVE first; source synchronized after validation.')

if __name__=='__main__':main()
