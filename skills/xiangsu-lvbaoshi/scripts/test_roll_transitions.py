"""Boundary ownership, defaults, frozen assets and media-preserving assembly."""
import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from prepare import SKILL, sha
import roll_transitions as roll
import effect_planning


class RollTransitions(unittest.TestCase):
    def setUp(self):
        self.work=tempfile.TemporaryDirectory(prefix='green-roll-contract-')
        self.addCleanup(self.work.cleanup)
        self.p=Path(self.work.name)
        shutil.copytree(SKILL/'assets/roll-transitions',self.p/roll.ASSETS)
        self.lock={'rollTransitionsVersion':roll.VERSION,'resources':{
            'roll-transitions/'+f.name:sha(f) for f in (SKILL/'assets/roll-transitions').iterdir() if f.is_file()}}
        self.plan={'id':'test-film','profile':'glass-lime-editorial-kit/v1','duration':14,
                   'rollTransitions':{'default':'auto','beats':{}},'effects':[],
                   'beats':[{'id':'mechanism-one','kind':'animation','start':3,'end':6},
                            {'id':'material-one','kind':'media','start':9,'end':12}]}

    def test_new_default_and_old_lock(self):
        del self.plan['rollTransitions']
        self.assertNotIn('rollTransitions',roll.resolve(self.plan,{}))
        fresh=roll.resolve(self.plan,self.lock)
        self.assertEqual(len(roll.entries(fresh)),4)
        self.assertNotIn('rollTransitions',self.plan)
        with self.assertRaises(ValueError):roll.resolve(self.plan,{'rollTransitionsVersion':'future'})

    def test_both_recipes_are_bidirectional_and_repeatable(self):
        self.plan['rollTransitions']['beats']={'mechanism-one':'glass-slide','material-one':'lime-leak'}
        expected=[(3,'A-to-B','glass-slide'),(6,'B-to-A','glass-slide'),(9,'A-to-B','lime-leak'),(12,'B-to-A','lime-leak')]
        self.assertEqual([(e['cut'],e['direction'],e['style']) for e in roll.entries(self.plan)],expected)
        for _ in range(3):
            self.assertEqual(roll.entries(self.plan),roll.entries(copy.deepcopy(self.plan)))
        roll.validate(self.p,self.plan,self.lock)

    def test_auto_is_stable_and_can_choose_both(self):
        cfg=roll.config(self.plan)
        choices=[roll.style_for({'id':f'beat-{i}'},cfg) for i in range(20)]
        self.assertEqual(set(choices),set(roll.STYLES))
        self.assertEqual(choices,[roll.style_for({'id':f'beat-{i}'},cfg) for i in range(20)])

    def test_only_host_boundaries_not_b_b_or_film_edges(self):
        self.plan['beats'][1].update(start=6)
        self.assertEqual([e['cut'] for e in roll.entries(self.plan)],[3,12])
        self.plan['beats'][0]['start']=0;self.plan['beats'][1]['end']=14
        self.assertEqual(roll.entries(self.plan),[])

    def test_chapters_and_overlays_do_not_create_or_replace_handoffs(self):
        original=roll.entries(self.plan)
        self.plan['effects']=[{'id':'chapter-overlay','templateId':'L28','start':2,'end':4}]
        self.plan['navigation']={'progress':True}
        self.assertEqual(roll.entries(self.plan),original)
        self.plan['beats']=[]
        self.assertEqual(roll.entries(self.plan),[])

    def test_explicit_off_and_invalid_configuration(self):
        self.plan['rollTransitions']=False
        self.assertEqual(roll.entries(self.plan),[])
        for cfg in [None,True,[],{'default':'amber-leak'},{'beats':[]},{'beats':{'unknown':'glass-slide'}},{'beats':{'material-one':0}},{'duration':1}]:
            with self.subTest(cfg=cfg):
                self.plan['rollTransitions']=cfg
                with self.assertRaises(ValueError):roll.entries(self.plan)
        self.plan['rollTransitions']={'beats':{'material-one':False}}
        self.assertEqual(len(roll.entries(self.plan)),2)

    def test_reject_edge_short_gaps_and_unreadable_beats(self):
        for start,end in [(0.1,6),(6.1,12),(3,3.8)]:
            plan=copy.deepcopy(self.plan)
            if start==6.1:plan['beats'][1]['start']=start
            else:plan['beats'][0].update(start=start,end=end)
            with self.subTest(start=start,end=end):
                with self.assertRaises(ValueError):roll.validate(self.p,plan,self.lock)

    def test_reject_frozen_asset_drift(self):
        (self.p/roll.ASSETS/'runtime.js').write_text('changed',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'asset missing/changed'):roll.validate(self.p,self.plan,self.lock)

    def test_assembly_keeps_media_timing_and_annotation_ownership(self):
        self.plan['effects']=[{'id':'host-effect'}]
        self.plan['screenEffects']=[{'id':'mark','targetBeat':'material-one'}]
        source='<video id="host-source" data-start="0" data-duration="14" data-has-audio="true"></video>'
        layers=['<div id="slot-mechanism-one" data-start="3" data-duration="3"><video data-media-start="8"></video></div>',
                '<div id="slot-material-one" data-start="9" data-duration="3"></div>',
                '<div id="slot-mark"></div>','<div id="slot-host-effect"></div>',
                '<div id="slot-navigation-progress"></div>','<div id="slot-mav-captions-00"></div>']
        page=roll.assemble(source,layers,self.plan)
        self.assertIn(source,page)
        for layer in layers:self.assertEqual(page.count(layer),1)
        self.assertLess(page.index('slot-host-effect'),page.index('gl-roll-visual-mechanism-one'))
        self.assertLess(page.index('gl-roll-visual-material-one'),page.index('slot-mark'))
        self.assertLess(page.index('slot-mark'),page.index('slot-navigation-progress'))
        self.assertNotIn('data-start=',page.split('id="gl-roll-host"')[1].split('>')[0])
        self.assertIn('data-media-start="8"',page)

    def test_candidates_count_actual_directional_windows(self):
        self.plan['rollTransitions']={'default':'glass-slide'}
        choices=effect_planning.catalog();uses=effect_planning.selected(self.plan,choices)
        self.assertEqual(len(uses['roll:glass-slide']),4)
        stats=effect_planning.usage(self.plan,choices,uses,{})
        row=next(r for r in stats['candidates'] if r['id']=='roll:glass-slide')
        self.assertEqual((row['count'],row['seconds']),(4,2.56))

    def test_historical_candidate_review_is_unchanged(self):
        plan={'duration':14,'beats':[],'effects':[],'orchestration':{'segments':[],'objectReview':[],
              'candidateReview':[{'candidateIds':[c['id']],'decision':'inapplicable','segmentIds':[],'reason':'Historical empty technical fixture'}
                                 for c in effect_planning.catalog() if not c['id'].startswith('roll:')]}}
        report=effect_planning.audit(plan,required=True,lock={})
        self.assertEqual(report['unreviewed'],[])
        self.assertFalse(any(c['id'].startswith('roll:') for c in report['usage']['candidates']))


if __name__=='__main__':unittest.main(verbosity=2)
