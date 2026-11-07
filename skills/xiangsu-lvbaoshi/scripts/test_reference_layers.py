"""Freeze and compile the seven retained recipes with supplied review fixtures."""
import argparse,copy,json,shutil,subprocess,sys,unittest
from pathlib import Path
from prepare import SKILL,read,dump,sha
import compile as compiler
import effect_planning

def review(p):
    used=effect_planning.selected(p,effect_planning.catalog())
    p['orchestration']['candidateReview']=[dict(candidateIds=[c['id']],decision='inapplicable',segmentIds=[],reason='此技术样板仅验证本轮保留两项与R01–R05，未涉及原L模板其它语义') for c in effect_planning.catalog() if c['id'] not in used]

class ReferenceLayers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if 'PLAN' not in globals():
            raise unittest.SkipTest('Run this media-backed suite with --fixtures and --project; unit discovery has no supplied review media')
    def reject(self,change):
        p=copy.deepcopy(PLAN);change(p)
        with self.assertRaises(ValueError):compiler.validate(P,p)
    def test_01_full_pipeline(self):
        checked=compiler.validate(P,PLAN);compiler.build(P,PLAN,checked)
        index=(P/'index.html').read_text(encoding='utf-8')
        for ident in ('ref01','ref02','ref03','ref04','ref05','white-objects','glass-callout','ref02-video'):self.assertIn('compositions/'+ident+'.html',index)
        self.assertNotIn('glass-lime-progress',index)
    def test_02_progress_requires_chapters(self):self.reject(lambda p:p.update(navigation={'progress':True}))
    def test_03_old_behind_rejected(self):self.reject(lambda p:p.update(behindText=[]))
    def test_04_old_annotation_rejected(self):self.reject(lambda p:p['screenEffects'][0].update(mode='spotlight'))
    def test_05_circle_bounds(self):self.reject(lambda p:p['screenEffects'][0]['region'].update(x=99999))
    def test_06_original_glass_size(self):self.reject(lambda p:p['screenEffects'][0]['card'].update(width=400))
    def test_07_floating_source_credit(self):self.reject(lambda p:p['companions'][0]['left'].update(asset='assets/clean-reference-plate.png'))
    def test_08_wrong_stage_placement(self):self.reject(lambda p:p['editorialScenes'][0]['content']['lines'][0].update(x=1910))
    def test_09_orphan_reference(self):self.reject(lambda p:p['orchestration']['segments'][0].update(layerIds=[]))
    def test_10_media_time(self):self.reject(lambda p:p['editorialScenes'][-1]['content']['media'].update(mediaStart=999))
    def test_11_crop_pixel_bounds(self):self.reject(lambda p:p['beats'][0]['content']['media']['crop'].update(width=99999))
    def test_12_no_dead_fields(self):self.reject(lambda p:p['editorialScenes'][1]['content'].update(rotationY=17))
    def test_14_invalid_capture_position(self):self.reject(lambda p:p['beats'][1]['content'].update(hostSide='force-right'))
    def test_13_all_retained_candidates(self):
        selected=effect_planning.selected(PLAN,effect_planning.catalog())
        for id in ('screen:callout','host:companions',*[f'reference:R0{i}' for i in range(1,6)]):self.assertIn(id,selected)
        self.assertIn('navigation:progress',[x['id'] for x in effect_planning.catalog()])
        self.assertNotIn('navigation:progress',selected)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--fixtures',required=True);a.add_argument('--project',required=True);x=a.parse_args();F=Path(x.fixtures).resolve();P=Path(x.project).resolve()
    if P.exists() and any(P.iterdir()):raise ValueError('Use a new technical test directory')
    P.parent.mkdir(parents=True,exist_ok=True);av=P.parent/'reference-loop-av.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-stream_loop','7','-i',str(F/'assets/host.mp4'),'-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t','48','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac',str(av)],check=True)
    timing=P.parent/'reference-loop-timing.json';dump(timing,dict(basis='Reference fixture with silent test audio, not production narration alignment',precision='segment',tokens=[dict(start=i*6,end=i*6+5,text='技术样板'+str(i+1)) for i in range(8)]))
    subprocess.run([sys.executable,str(SKILL/'scripts/prepare.py'),'--source',str(av),'--project',str(P),'--end','48','--timing',str(timing)],check=True)
    for f in (F/'assets').rglob('*'):
        if f.is_file() and 'fonts' not in f.parts and f.suffix.lower() in {'.png','.mp4','.svg'}:
            dest=P/'assets'/f.relative_to(F/'assets');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
    dump(P/'asset-credits.json',read(F/'asset-credits.json'))
    scenes=read(F/'preview-scenes.json');PLAN=read(P/'edit-plan.json');PLAN['effects']=[];PLAN['beats']=[];PLAN['editorialScenes']=[];PLAN['companions']=[];PLAN['screenEffects']=[];PLAN['orchestration']['segments']=[]
    for i,s in enumerate(scenes):
        start,end=i*6,(i+1)*6;kind=s['kind'];id=s['id'];scenario='host';beats=[];layers=[];e=dict(id=id,start=start,end=end)
        if kind in {'R04','R05'}:
            c=copy.deepcopy(s['data']);c['media']={k:v for k,v in c['media'].items() if k not in ('sourceWidth','sourceHeight')}
            if kind=='R05':c.update(hostSource='assets/source.mp4',hostMediaStart=start)
            PLAN['beats'].append(dict(**e,kind='editorial',templateId=kind,content=c));beats=[id];scenario='evidence' if kind=='R04' else 'illustration'
        elif kind in {'R01','R02','R03'}:PLAN['editorialScenes'].append(dict(**e,templateId=kind,content=s['data']));layers=[id]
        elif kind=='companion':PLAN['companions'].append(dict(**e,**s['data']));layers=[id]
        else:
            PLAN['beats'].append(dict(id='photo-source',kind='screen',start=start,end=end,image='assets/ref-16.png',sourceLabel='Actual supplied UI screenshot; material explanation callout fixture'));beats=['photo-source'];scenario='operation'
            d={k:v for k,v in s['data'].items() if k!='sourceDimensions'};PLAN['screenEffects'].append(dict(**e,targetBeat='photo-source',**d));layers=[id]
        PLAN['orchestration']['segments'].append(dict(id='segment-'+str(i),start=start,end=end,scenario=scenario,producer='editorial',narration='功能验证，不冒充真实原片台词',purpose='对应已确认的参考效果与素材分工',beatIds=beats,effectIds=[],layerIds=layers,inputs=[dict(need='已冻结的本地参考和实际Pixel2all素材',status='ready')],entry='建立当前观看焦点',exit='交给下一段'))
    obj=PLAN['companions'][0];ref='companions:'+obj['id'];PLAN['orchestration']['objectReview']=[dict(entryIds=[ref],decision='used',searchTerms=['文件柜','brain'],bindings=[dict(entryId=ref,path=obj[s]['asset']) for s in ('left','right')],reason='实际显示从Pixel2all下载的原白色陶瓷物件，未染色')]
    review(PLAN);dump(P/'edit-plan.json',PLAN)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReferenceLayers));dump(P/'reference-test-report.json',dict(tests=result.testsRun,errors=[str(t) for t,_ in result.errors+result.failures],scope='Retained/reference recipe actual compiler roundtrip, sources and rejections; no artistic approval'))
    sys.exit(not result.wasSuccessful())
