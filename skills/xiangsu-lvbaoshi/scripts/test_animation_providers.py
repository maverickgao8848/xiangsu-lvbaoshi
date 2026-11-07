"""Synthetic source/video roundtrip for producer routing; no Lemo artistic claim."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SKILL/'scripts'))
from prepare import read, dump
import animation_contract as contract
import animation_routing
import animation_insert
import effect_planning
import orchestration
from stage_animation import stage

spec=importlib.util.spec_from_file_location('provider_compiler',SKILL/'scripts/compile.py')
compiler=importlib.util.module_from_spec(spec);spec.loader.exec_module(compiler)


class Providers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp=tempfile.TemporaryDirectory(prefix='animation-provider-')
        cls.addClassCleanup(temp.cleanup)
        cls.root=Path(temp.name);cls.project=cls.root/'film'
        cls.green=SKILL.name=='xiangsu-lvbaoshi'
        video=cls.root/'source.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=0x364150:s=1920x1080:r=30:d=8',
                        '-f','lavfi','-i','sine=frequency=330:duration=8','-c:v','libx264','-preset','ultrafast',
                        '-crf','28','-c:a','aac','-shortest',str(video)],check=True)
        args=[sys.executable,'-B',str(SKILL/'scripts/prepare.py'),'--source',str(video),
              '--project',str(cls.project),'--end','8','--preserve-full-input']
        tokens=[dict(id='t'+str(i),start=i*2,end=i*2+1.5,text='接口测试'+str(i)) for i in range(4)]
        if cls.green:
            timing=cls.root/'timing.json'
            dump(timing,dict(basis='Synthetic interface fixture, not human timing',precision='segment',
                            tokens=[{k:v for k,v in t.items() if k!='id'} for t in tokens]))
            args+=['--timing',str(timing)]
        else:
            alignment=cls.root/'alignment.json';mapping=cls.root/'source-map.json'
            dump(alignment,{'tokens':[]})
            dump(mapping,dict(schemaVersion='mav-talking-head-roughcut-source-map/v1',outputTokens=tokens))
            args+=['--alignment',str(alignment),'--source-map',str(mapping)]
        subprocess.run(args,check=True,capture_output=True)
        source=cls.root/'source';source.mkdir()
        (source/'index.html').write_text('<canvas></canvas><script>window.render=t=>t;</script>',encoding='utf-8')
        (source/'TREATMENT.md').write_text('# Synthetic handoff fixture\nNot a Lemo creative production.',encoding='utf-8')
        (source/'build.mjs').write_text('// Synthetic build entry, no external project reference\n',encoding='utf-8')
        style=cls.root/'STYLE.md';style.write_text('# Synthetic style fixture\nNot an artistic validation.',encoding='utf-8')
        cls.beat=stage(cls.project,'lemo-test',source,video,'blueprint',style,'build.mjs')
        cls.beat.update(start=2,end=6,title='接口验证')
        if cls.green:
            cls.beat.pop('title')  # Green frozen-picture interface has no additional title.
        cls.plan=dict(id='provider-film',profile=read(cls.project/'input-lock.json')['profile'],
                      title='技术样片',duration=8,beats=[cls.beat],effects=[],openingBehindText=False)
        if cls.green:
            cls.plan.pop('title');cls.plan.pop('openingBehindText')
        segments=[]
        for ident,start,end,scenario,producer,beats in (
            ('opening',0,2,'host','editorial',[]),
            ('metaphor',2,6,'illustration','lemo-opuscar',['lemo-test']),
            ('closing',6,8,'host','editorial',[])):
            segments.append(dict(id=ident,start=start,end=end,scenario=scenario,producer=producer,beatIds=beats,
                                 effectIds=[],narration='合成接口样段',purpose='检查实际制作方与源工程交接',
                                 inputs=[],entry='进入当前焦点',exit='交给下一段'))
        cls.plan['orchestration']=dict(version=orchestration.VERSION,segments=segments,objectReview=[])
        if cls.green:
            import navigation,roll_transitions
            cls.plan=roll_transitions.resolve(navigation.effective_plan(cls.plan,read(cls.project/'input-lock.json')),read(cls.project/'input-lock.json'))
        else:
            import mav_defaults
            cls.plan=mav_defaults.resolve(cls.plan,read(cls.project/'input-lock.json'))
        used=effect_planning.selected(cls.plan,effect_planning.catalog())
        cls.plan['orchestration']['candidateReview']=[
            dict(candidateIds=[c['id']],decision='inapplicable',segmentIds=[],reason='本技术输入仅验证Lemo片段交接')
            for c in effect_planning.catalog() if c['id'] not in used]
        entry=cls.root/'.agents/skills/lemo-opuscar/SKILL.md'
        entry.parent.mkdir(parents=True);entry.write_text('Synthetic discovery fixture',encoding='utf-8')
        cls.env=patch.dict(os.environ,{'EDITORIAL_REPO':str(cls.root)})
        cls.env.start();cls.addClassCleanup(cls.env.stop)

    def test_full_prepare_compile_with_lemo_only(self):
        original=animation_routing.discover
        def only_lemo(project=None,provider='xiangsu-mg'):
            self.assertEqual(provider,'lemo-opuscar','Lemo must not require the MG installation')
            return original(project,provider)
        with patch.object(animation_routing,'discover',side_effect=only_lemo):
            checked=compiler.validate(self.project,self.plan)
            if self.green:compiler.build(self.project,self.plan,checked)
            else:compiler.build(self.project,self.plan)
        page=(self.project/'compositions/lemo-test.html').read_text(encoding='utf-8')
        self.assertIn('muted playsinline',page)
        self.assertIn('lemo-opuscar',(self.project/'ANIMATION-ROUTING.md').read_text(encoding='utf-8'))
        self.assertEqual(read(self.project/'build-report.json')['animationInserts']['entries'][0]['provider'],'lemo-opuscar')
        master=(self.project/'index.html').read_text(encoding='utf-8')
        self.assertIn('data-has-audio="true"' if self.green else '<audio id="voice"',master)
        self.assertFalse((self.project/'animations/lemo-test/frame-provenance.json').exists())

    def test_candidates_distinguish_mg_and_lemo(self):
        selected=effect_planning.selected(self.plan,effect_planning.catalog())
        self.assertEqual(selected['animation:lemo-opuscar'],['beats:lemo-test'])
        self.assertNotIn('route:animation' if self.green else 'animation:mav-mg',selected)
        result=effect_planning.audit(self.plan,required=True,lock=read(self.project/'input-lock.json'))
        self.assertEqual(result['objectUsedWindows'],0)
        self.assertEqual(result['unreviewedObjectEntries'],[])

    def test_producer_and_beat_must_match(self):
        plan=copy.deepcopy(self.plan);plan['beats'][0].pop('provider')
        with self.assertRaisesRegex(ValueError,'provider differs'):
            orchestration.validate(plan,read(self.project/'input-lock.json'))

    def test_source_drift_rejected(self):
        file=self.project/'animations/lemo-test/index.html';original=file.read_bytes()
        try:
            file.write_bytes(original+b'changed')
            with self.assertRaisesRegex(ValueError,'source drift'):animation_insert.validate(self.project,self.plan)
        finally:file.write_bytes(original)

    def test_wrong_style_rejected(self):
        plan=copy.deepcopy(self.plan);plan['beats'][0]['styleId']='watercolor'
        with self.assertRaisesRegex(ValueError,'styleId/provider'):animation_insert.validate(self.project,plan)

    def test_wrong_credit_rejected(self):
        file=self.project/'asset-credits.json';original=file.read_bytes()
        try:
            rows=read(file);rows[-1]['sourcePage']='generated:mav-mg:lemo-test';dump(file,rows)
            with self.assertRaisesRegex(ValueError,'credit'):animation_insert.validate(self.project,self.plan)
        finally:file.write_bytes(original)

    def test_short_media_window_rejected(self):
        plan=copy.deepcopy(self.plan);plan['beats'][0]['mediaStart']=7
        with self.assertRaisesRegex(ValueError,'too short'):animation_insert.validate(self.project,plan)

    def test_unknown_provider_and_missing_selected_skill_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unknown animation'):contract.provider({'provider':'unknown'})
        with patch.object(animation_routing,'discover',return_value={'provider':'missing'}):
            with self.assertRaisesRegex(ValueError,'unavailable'):animation_insert.validate(self.project,self.plan)

    def test_repository_lemo_overrides_personal_entry(self):
        route=animation_routing.discover(self.project,'lemo-opuscar')
        self.assertTrue(Path(route['skillPath']).is_relative_to(self.root))
        repo=self.root/'xiangsu-mg-content'
        self.assertEqual(animation_routing.candidates(repo,'lemo-opuscar')[0],repo/'.agents/skills/lemo-opuscar/SKILL.md')

    def test_same_plan_keeps_both_provider_identities(self):
        plan=copy.deepcopy(self.plan)
        plan['beats'].append(dict(id='mg-test',kind='animation',provider='xiangsu-mg',start=0,end=1))
        with patch.object(animation_routing,'discover',side_effect=lambda p,ident:dict(provider=ident)):
            self.assertEqual(set(contract.selected_routes(self.project,plan)),{'xiangsu-mg','lemo-opuscar'})
        uses=effect_planning.selected(plan,effect_planning.catalog())
        self.assertEqual(uses['animation:lemo-opuscar'],['beats:lemo-test'])
        self.assertEqual(uses['route:animation' if self.green else 'animation:mav-mg'],['beats:mg-test'])

    def test_old_freeze_does_not_add_mandatory_animation_reviews(self):
        plan=copy.deepcopy(self.plan);plan['beats']=[];plan['orchestration']['candidateReview']=[]
        lock={}
        result=effect_planning.audit(plan,lock=lock)
        self.assertNotIn('animation:lemo-opuscar',result['unreviewed'])


if __name__=='__main__':unittest.main()
