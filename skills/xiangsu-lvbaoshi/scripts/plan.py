"""Create a reviewable full-duration draft; never invent selected effects or approval."""
import argparse,json
from pathlib import Path
from prepare import read,dump
import orchestration,effect_planning
import navigation
import roll_transitions
def skeleton(p):
    lock=read(p/'input-lock.json');tokens=read(p/'words.json')['tokens']
    plan=dict(id='glass-lime-film',profile=lock['profile'],duration=lock['duration'],beats=[],effects=[],captions=[],hostFinish={'enabled':False,'preset':'soft-edge-v1'},orchestration=dict(version=orchestration.VERSION,segments=[dict(id='draft-full',start=0,end=lock['duration'],scenario='host',producer='editorial',narration=''.join(t['text'] for t in tokens) or '待提供可信校订稿与时间',purpose='待按全文划连续观看任务',beatIds=[],effectIds=[],inputs=[dict(need='全文分段、全量候选评估、素材分工和衔接决定',status='missing')],entry='待填写实际进入',exit='待填写实际退出')],candidateReview=[],objectReview=[]))
    plan=roll_transitions.resolve(navigation.effective_plan(plan,lock),lock)
    if plan['navigation']['progress']:
        plan['orchestration']['segments'][0]['inputs'].append(dict(need='按全文填写 chapters.json 的真实章界、编号和标题；默认联动章节角标、A进度条与扫线转场',status='missing'))
    return plan
def main():
    a=argparse.ArgumentParser();a.add_argument('--project',required=True);a.add_argument('--out',default='edit-plan.json');a.add_argument('--catalog',action='store_true');x=a.parse_args()
    if x.catalog:print(json.dumps(effect_planning.catalog(),ensure_ascii=True,indent=2));return
    p=Path(x.project).resolve();target=p/x.out
    if not target.resolve().is_relative_to(p) or target.exists():raise ValueError('Draft destination must be a new project-local file')
    dump(target,skeleton(p))
if __name__=='__main__':main()
