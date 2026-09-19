"""Local evidence/Git closeout for independent remote night watchdog; no science edits."""
import hashlib,json,os,subprocess,time,traceback
import awm_7b_guardian as g

def upload(path):
    r=g.call([*g.SCP,str(path),'6004:'+g.RE+'/'+path.name],60)
    assert r.returncode==0,r.stderr

def main():
    seen=set(json.loads((g.E/'local_stage_commits.json').read_text()).get('completed',[]))
    waiting_seen=False
    g.put('local_guardian.json',dict(pid=os.getpid(),status='NIGHT_MONITORING',auto_shutdown=True))
    while True:
        try:
            g.sync()
            for stage in ['reference','direct','paraphrase','logit']:
                if stage not in seen and (g.E/(stage+'_complete.json')).exists():
                    h=g.update(stage);seen.add(stage)
                    g.put('local_stage_commits.json',dict(completed=sorted(seen),last_commit=h));g.push()
            waiting=g.E/'night_waiting_for_user.json'
            if waiting.exists() and not waiting_seen:
                x=json.loads(waiting.read_text())
                (g.E/'night_user_question.md').write_text('# WAITING_FOR_USER\n\n'+x['question']+'\n\n'+x['reason'],encoding='utf-8')
                g.update('WAITING_FOR_USER',True);g.push();waiting_seen=True
            request=g.E/'night_closure_request.json'
            if not request.exists():time.sleep(60);continue
            terminal=json.loads(request.read_text())
            # Watchdog produced the closure request only after workers exited and, on
            # success, a fresh verification of all three final model manifests.
            r=g.call([*g.SSH,'/root/miniconda3/bin/python /root/autodl-tmp/WMKD_Benchmark/scripts/awm_7b_night_watchdog.py --inventory'],240)
            assert r.returncode==0,r.stderr
            inv=json.loads(r.stdout)
            for name,digest in inv.items():
                f=g.E/name
                assert f.resolve().is_relative_to(g.E.resolve()) and f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==digest,name
            g.put('evidence_sync_verified.json',dict(verified=True,files=inv,time=time.time()))
            g.put('final_closeout.json',dict(status=terminal['status'],terminal=terminal,auto_shutdown=True,
                instance_release=False,llmprint_remains_paused=True,time=time.time()))
            if terminal['status']!='COMPLETED':
                failure='# AWM7B night failure / blocking report\n\n'+json.dumps(terminal,indent=2,ensure_ascii=False)+'\n'
                (g.E/'night_failure_report.md').write_text(failure,encoding='utf-8')
            h=g.update(terminal['status'],True);g.push()
            g.put('night_local_closure_ack.json',dict(request_time=terminal['time'],evidence_verified=True,commit=h,
                time=time.time(),auto_shutdown=True,instance_release=False))
            g.commit('Record AWM7B verified night closeout and shutdown authorization')
            upload(g.E/'night_local_closure_ack.json')
            # Remote watchdog leaves a minute to collect the accepted acknowledgement.
            g.put('local_guardian.json',dict(pid=os.getpid(),status='SHUTDOWN_ARMED_AFTER_VERIFIED_CLOSEOUT',auto_shutdown=True))
            for _ in range(8):
                time.sleep(30)
                r=g.call([*g.SSH,'cat '+g.RE+'/night_shutdown_intent.json'],30)
                if r.returncode==0:
                    g.put('night_shutdown_intent.json',json.loads(r.stdout))
                    g.commit('Record AWM7B remote shutdown intent after safe closeout')
                probe=g.call([*g.SSH,'true'],30)
                if probe.returncode:
                    g.put('night_shutdown_observation.json',dict(time=time.time(),ssh_unreachable=True,
                        caveat='SSH unreachable after authorized shutdown; not independent power-state verification'))
                    g.commit('Record AWM7B shutdown connection observation');return
            return
        except Exception:
            g.put('local_transport_retry.json',dict(error=traceback.format_exc(),time=time.time()))
            time.sleep(30)

if __name__=='__main__':
    # Outer wrapper recovers unexpected local guardian exceptions without touching GPU work.
    while True:
        try:main();break
        except Exception:
            g.put('night_local_outer_error.json',dict(time=time.time(),error=traceback.format_exc()));time.sleep(30)
