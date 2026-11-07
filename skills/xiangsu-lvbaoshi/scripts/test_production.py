"""Real freeze/compile roundtrip and rejection tests; synthetic footage, no art approval."""
import copy,json,subprocess,sys,tempfile,unittest,re,html
from pathlib import Path
from prepare import SKILL,read,dump,sha
import compile as compiler
import orchestration,effect_planning,content_slots

WORKSPACE=tempfile.TemporaryDirectory(prefix='glass-lime-production-')
LAB=Path(WORKSPACE.name);P=LAB/'work/production-contract-check'
class Production(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.addClassCleanup(WORKSPACE.cleanup)
        # Preserve an existing test workspace; reruns must be explicit new destinations.
        if P.exists():
            if not (P/'animations/demo-mg/BRIEF.md').is_file() or 'technical fixture only' not in (P/'animations/demo-mg/BRIEF.md').read_text(encoding='utf-8'):raise ValueError('Existing path is not this synthetic test workspace')
            cls.plan=read(P/'edit-plan.json');return
        source=LAB/'work/production-test-source.mp4';source.parent.mkdir(exist_ok=True)
        if not source.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','lavfi','-i','color=c=0x536b64:s=1920x1080:r=30:d=24','-f','lavfi','-i','sine=frequency=330:sample_rate=48000:duration=24','-c:v','libx264','-preset','ultrafast','-crf','24','-c:a','aac','-shortest',str(source)],check=True)
        timing=LAB/'work/production-test-timing.json';dump(timing,dict(basis='Synthetic technical fixture, no human narration',precision='segment',tokens=[dict(start=i,end=i+3,text=t) for i,t in [(0,'先看真人观点'),(8,'进入完整机制解释'),(16,'展示对话情境'),(20,'返回真人收束')]]))
        subprocess.run([sys.executable,str(SKILL/'scripts/prepare.py'),'--source',str(source),'--project',str(P),'--end','24','--timing',str(timing),'--preserve-full-input'],check=True)
        mg=P/'animations/demo-mg';mg.mkdir(parents=True)
        for file,text in {'index.html':'<p>Technical video handoff fixture only</p>','STORYBOARD.md':'# Synthetic full-frame fixture','frame.md':'# Fixture\nNo art approval; no production style claimed.','BRIEF.md':'style: cobalt-grid\ntechnical fixture only'}.items():(mg/file).write_text(text,encoding='utf-8')
        from animation_routing import inherit_frame
        inherit_frame(P,mg,replace=True)
        (mg/'BRIEF.md').write_text('style: glass-lime-extracted\ntechnical fixture only',encoding='utf-8')
        dump(P/'asset-credits.json',[dict(path='assets/source.mp4',sha256=sha(P/'assets/source.mp4'),sourcePage='generated:mav-mg:demo-mg',sourceLabel='Synthetic AV fixture; not an actual 像素 MG creative build')])
        plan=read(P/'edit-plan.json');plan['hostFinish']['enabled']=True
        plan['effects']=[dict(id='question-one',start=1,end=7,templateId='L07',motion='C',content={'title':'为何先看证据？','text':['为何先看证据？'],'images':[]}),dict(id='definition-one',start=20,end=24,templateId='L02',motion='D',content={'title':'验证边界','definition':'先验证接口，再审看成片。','note':'技术测试不代替艺术判断。','text':[],'images':[]})]
        second=content_slots.slots(content_slots.render([plan['effects'][1]])[0]['body']);plan['effects'][1]['content']['text']=['本期表达'+str(i+1) for i in range(len(second['text']))]
        plan['beats']=[dict(id='demo-mg',kind='animation',start=8,end=16,video='assets/source.mp4',mediaStart=8,editableSource='animations/demo-mg',sourceLabel='MG handoff technical fixture'),dict(id='operation-one',kind='interface',start=16,end=20,sceneId='S01',config={'content':{'selfId':'me','title':'接口测试','showTyping':True,'participants':[{'id':'me','name':'测试者'},{'id':'client','name':'对方'}],'messages':[{'id':'m1','senderId':'client','text':'请确认这期的验收范围。'}]}},sourceLabel='情景模拟 · 技术测试')]
        plan['mg']={'styleId':'glass-lime-extracted'}
        segments=[]
        for id,start,end,scenario,producer,beats,effects in [('host-open',0,8,'host','editorial',[],['question-one']),('mechanism',8,16,'mechanism','xiangsu-mg',['demo-mg'],[]),('operation',16,20,'dialogue','scene-kit',['operation-one'],[]),('host-close',20,24,'host','editorial',[],['definition-one'])]:
            segments.append(dict(id=id,start=start,end=end,scenario=scenario,producer=producer,narration='技术样段：'+id,purpose='验证完整覆盖和制作方交接',beatIds=beats,effectIds=effects,inputs=[dict(need='已冻结技术测试输入',status='ready')],entry='进入本段主画面',exit='交给下一连续观看任务'))
        plan['orchestration']['segments']=segments
        dump(P/'chapters.json',[dict(number='01',title='开场',start=0),dict(number='02',title='机制',start=12)])
        plan['navigation']={'progress':True}
        uses=effect_planning.selected(plan,effect_planning.catalog())
        plan['orchestration']['candidateReview']=[dict(candidateIds=[c['id']],decision='inapplicable',segmentIds=[],reason='本技术样段仅验证问句、定义、MG和录屏路线，其余语义不在测试输入中') for c in effect_planning.catalog() if c['id'] not in uses]
        plan['orchestration']['objectReview']=[dict(entryIds=[r],decision='exception',searchTerms=[],bindings=[],reason='合成接口测试没有真实选题，不借演示物件宣称素材复用') for r in ['effects:question-one','effects:definition-one','beats:demo-mg']]
        plan['orchestration']['objectMajorityException']='本片是接口技术fixture；真实制作仍须按语义检索并绑定实际物件。'
        dump(P/'edit-plan.json',plan);cls.plan=plan
    def test_01_real_pipeline(self):
        checked=compiler.validate(P,self.plan);compiler.build(P,self.plan,checked)
        self.assertEqual(read(P/'build-report.json')['duration'],24)
        self.assertTrue((P/'ORCHESTRATION.md').is_file());self.assertTrue((P/'ANIMATION-ROUTING.md').is_file())
        page=(P/'index.html').read_text(encoding='utf-8');self.assertIn('data-has-audio="true"',page);self.assertIn('assets/source.mp4',page);self.assertIn('slot-navigation-progress',page);self.assertTrue((P/'compositions/navigation-progress.html').is_file())
        self.assertEqual((P/'animations/demo-mg/frame.md').read_bytes(),(P/'frame.md').read_bytes())
        self.assertEqual(len(read(P/'captions.json')),4)
        self.assertEqual([r['cut'] for r in read(P/'build-report.json')['rollTransitions']['entries']],[8,20])
        self.assertTrue((P/'effective-plan.json').is_file())
    def reject(self,change):
        plan=copy.deepcopy(self.plan);change(plan)
        with self.assertRaises(ValueError):compiler.validate(P,plan)
    def test_02_missing_input(self):self.reject(lambda p:p['orchestration']['segments'][1]['inputs'][0].update(status='missing'))
    def test_03_coverage_gap(self):self.reject(lambda p:p['orchestration']['segments'][2].update(start=16.2))
    def test_04_wrong_reference(self):self.reject(lambda p:p['orchestration']['segments'][0]['effectIds'].append('absent'))
    def test_05_unreviewed_candidate(self):self.reject(lambda p:p['orchestration']['candidateReview'].pop())
    def test_06_media_overrun(self):self.reject(lambda p:p['beats'][0].update(mediaStart=22))
    def test_07_demo_text_not_bound(self):self.reject(lambda p:p['effects'][0]['content'].update(text=[]))
    def test_08_wrong_style(self):self.reject(lambda p:p['mg'].update(styleId='unknown'))
    def test_09_mg_decoration(self):self.reject(lambda p:p['effects'][0].update(end=9))
    def test_10_pending_object(self):self.reject(lambda p:p['orchestration']['objectReview'][0].update(decision='pending'))
    def test_11_fake_binding(self):self.reject(lambda p:p['orchestration']['objectReview'][0].update(decision='used',bindings=[dict(entryId='effects:question-one',path='assets/unbound.png')]))
    def test_12_timing_drift(self):
        file=P/'words.json';original=file.read_bytes()
        try:
            file.write_bytes(original+b' ')
            with self.assertRaises(ValueError):compiler.validate(P,self.plan)
        finally:file.write_bytes(original)
    def test_13_draft_does_not_approve(self):
        from plan import skeleton
        draft=skeleton(P);summary=orchestration.validate(draft,read(P/'input-lock.json'),draft=True)
        self.assertTrue(summary['missingInputs']);self.assertTrue(summary['effectPlanning']['unreviewed'])
        with self.assertRaises(ValueError):compiler.validate(P,draft)
    def test_14_bundle_slots_all_templates(self):
        entries=[dict(id=e['id'],templateId=e['id']) for e in read(SKILL/'references/effect-catalog.json')]
        self.assertEqual(len(content_slots.render(entries)),28)
        self.assertTrue(all(content_slots.slots(x['body'])['text'] for x in content_slots.render(entries)))
    def test_15_screen_route(self):
        plan=copy.deepcopy(self.plan)
        plan['beats'][1]=dict(id='operation-one',kind='screen',start=16,end=20,video='assets/source.mp4',mediaStart=16,sourceLabel='Synthetic screen route fixture')
        plan['orchestration']['segments'][2].update(scenario='operation',producer='editorial')
        plan['orchestration']['candidateReview']=[r for r in plan['orchestration']['candidateReview'] if 'route:screen' not in r['candidateIds']]
        if not any('route:interface' in r['candidateIds'] for r in plan['orchestration']['candidateReview']):plan['orchestration']['candidateReview'].append(dict(candidateIds=['route:interface'],decision='inapplicable',segmentIds=[],reason='此测试专门使用录屏视频'))
        compiler.validate(P,plan)
    def test_16_caption_groups_preserve_timing_and_text(self):
        cues=[dict(start=round(.13+i*1.27,4),end=round(.91+i*1.27,4),text=f'第{i}句与<&>') for i in range(35)]
        layers=compiler.caption_layers(P,cues,{'beats':[]},'', '.mav-subtitle{position:absolute;bottom:78px}')
        self.assertEqual(len(layers),3)
        found=[]
        for layer in layers:
            base=float(re.search(r'data-start="([^"]+)"',layer)[1])
            file=re.search(r'data-composition-src="([^"]+)"',layer)[1]
            page=(P/file).read_text(encoding='utf-8')
            rows=re.findall(r'id="caption-(\d+)"[^>]*data-start="([^"]+)" data-duration="([^"]+)"[^>]*><span class="mav-subtitle"[^>]*>(.*?)</span>',page)
            self.assertLessEqual(len(rows),16)
            for i,start,duration,text in rows:found.append((int(i),round(base+float(start),4),round(base+float(start)+float(duration),4),html.unescape(text)))
        self.assertEqual(found,[(i,c['start'],c['end'],c['text']) for i,c in enumerate(cues)])

    def test_17_cinema_animation_roundtrip(self):
        plan=copy.deepcopy(self.plan)
        plan['beats'][0]['display']={'style':'cinema'}
        plan['orchestration']['candidateReview']=[r for r in plan['orchestration']['candidateReview'] if 'display:cinema' not in r['candidateIds']]
        checked=compiler.validate(P,plan);compiler.build(P,plan,checked)
        page=(P/'compositions/demo-mg.html').read_text(encoding='utf-8')
        self.assertIn('stage-shell cinema',page)
        self.assertIn('data-media-start="8"',page)
        self.assertIn('muted playsinline',page)
        self.assertEqual(read(P/'build-report.json')['materialDisplay']['entries'][0]['kind'],'animation')
        self.assertEqual(read(P/'build-report.json')['animationInserts']['entries'][0]['editableSource'],'animations/demo-mg')

    def test_18_cinema_media_roundtrip(self):
        plan=copy.deepcopy(self.plan)
        b=plan['beats'][1]
        plan['beats'][1]=dict(id=b['id'],kind='media',start=16,end=20,video='assets/source.mp4',mediaStart=16,sourceLabel='Synthetic supplied video',display={'style':'cinema'})
        plan['orchestration']['segments'][2].update(scenario='illustration',producer='editorial')
        uses=effect_planning.selected(plan,effect_planning.catalog())
        plan['orchestration']['candidateReview']=[dict(candidateIds=[c['id']],decision='inapplicable',segmentIds=[],reason='Synthetic selected-route fixture') for c in effect_planning.catalog() if c['id'] not in uses]
        checked=compiler.validate(P,plan);compiler.build(P,plan,checked)
        page=(P/'compositions/operation-one.html').read_text(encoding='utf-8')
        self.assertIn('stage-shell cinema',page);self.assertIn('data-media-start="16"',page)

    def test_19_cinema_image_roundtrip(self):
        plan=copy.deepcopy(self.plan);b=plan['beats'][1]
        image='assets/glass-lime/host.jpg'
        credits=read(P/'asset-credits.json')
        if not any(c['path']==image for c in credits):
            credits.append(dict(path=image,sha256=sha(P/image),sourcePage='synthetic:bundled-image-fixture'));dump(P/'asset-credits.json',credits)
        plan['beats'][1]=dict(id=b['id'],kind='media',start=16,end=20,image=image,sourceLabel='Synthetic image fixture',display={'style':'cinema'})
        plan['orchestration']['segments'][2].update(scenario='illustration',producer='editorial')
        uses=effect_planning.selected(plan,effect_planning.catalog())
        plan['orchestration']['candidateReview']=[dict(candidateIds=[c['id']],decision='inapplicable',segmentIds=[],reason='Synthetic selected-route fixture') for c in effect_planning.catalog() if c['id'] not in uses]
        checked=compiler.validate(P,plan);compiler.build(P,plan,checked)
        page=(P/'compositions/operation-one.html').read_text(encoding='utf-8')
        self.assertIn('stage-shell cinema',page);self.assertIn('<img ',page);self.assertNotIn('<video ',page)

    def test_20_both_handoffs_compile_without_chapters(self):
        for style in ('glass-slide','lime-leak'):
            plan=copy.deepcopy(self.plan);plan['navigation']={'progress':False};plan['rollTransitions']={'default':style}
            uses=effect_planning.selected(plan,effect_planning.catalog())
            plan['orchestration']['candidateReview']=[dict(candidateIds=[c['id']],decision='inapplicable',segmentIds=[],reason='Technical recipe case') for c in effect_planning.catalog() if c['id'] not in uses]
            checked=compiler.validate(P,plan);compiler.build(P,plan,checked)
            entries=read(P/'build-report.json')['rollTransitions']['entries']
            self.assertEqual([r['style'] for r in entries],[style,style])
            self.assertEqual([r['direction'] for r in entries],['A-to-B','B-to-A'])
            self.assertNotIn('slot-navigation-progress',(P/'index.html').read_text(encoding='utf-8'))

    def test_21_legacy_has_no_handoffs_or_new_required_reviews(self):
        plan=copy.deepcopy(self.plan);plan.pop('rollTransitions',None)
        plan['orchestration']['candidateReview']=[r for r in plan['orchestration']['candidateReview'] if not any(c.startswith('roll:') for c in r['candidateIds'])]
        lock=read(P/'input-lock.json');old=copy.deepcopy(lock);old.pop('rollTransitionsVersion')
        try:
            dump(P/'input-lock.json',old)
            checked=compiler.validate(P,plan);compiler.build(P,plan,checked)
            self.assertEqual(read(P/'build-report.json')['rollTransitions']['entries'],[])
            self.assertNotIn('gl-roll-host',(P/'index.html').read_text(encoding='utf-8'))
        finally:dump(P/'input-lock.json',lock)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Production);result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'tests':result.testsRun,'errors':[str(x[0]) for x in result.errors+result.failures],'project':str(P.relative_to(LAB)).replace('\\','/'),'scope':'synthetic AV freeze/full-plan compile and rejection contracts; no real narration art approval'}
    print(json.dumps(report,ensure_ascii=False))
    sys.exit(not result.wasSuccessful())
