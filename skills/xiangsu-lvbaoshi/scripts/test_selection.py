"""Verify complete, reachable candidates and transparent use/alternative reporting."""
import copy,json,unittest
from unittest.mock import patch
import effect_planning as planning
import production_layers

class Selection(unittest.TestCase):
    def test_complete_retained_catalog(self):
        choices=planning.catalog();ids={c['id'] for c in choices}
        self.assertEqual(len(ids),len(choices))
        retained=json.loads((planning.SKILL/'references/effect-catalog.json').read_text(encoding='utf-8'))
        self.assertEqual({'effect:'+c['id'] for c in retained},{c for c in ids if c.startswith('effect:')})
        self.assertTrue({'reference:R01','reference:R02','reference:R03','reference:R04','reference:R05','screen:callout','host:companions','exit:domain-warp','navigation:progress'}<=ids)
        self.assertTrue(all(c['baseWeight']==1 for c in choices))

    def test_each_candidate_has_a_reachable_match(self):
        for choice in planning.catalog():
            plan={'duration':6,'beats':[],'effects':[]}
            entry={'id':'example','start':0,'end':6}
            if choice['id'].startswith('finish:'):plan['hostFinish']={'enabled':True}
            elif choice['id']=='animation:lemo-opuscar':plan['beats']=[{**entry,'kind':'animation','provider':'lemo-opuscar'}]
            elif choice['id'].startswith('route:'):plan['beats']=[{**entry,**choice['match']}]
            elif choice['id'].startswith('screen:'):plan['screenEffects']=[{**entry,'mode':'callout'}]
            elif choice['id']=='host:companions':plan['companions']=[entry]
            elif choice['id'].startswith('reference:'):
                entry.update(choice['match']);field='beats' if entry['templateId'] in ('R04','R05') else 'editorialScenes'
                plan[field]=[{**entry,**({'kind':'editorial'} if field=='beats' else {})}]
            elif choice['id']=='navigation:progress':plan['navigation']={'progress':True}
            elif choice['id']=='display:cinema':plan['beats']=[{**entry,'kind':'media','display':{'style':'cinema'}}]
            elif choice['id'].startswith('roll:'):
                plan.update(duration=10,beats=[{**entry,'kind':'media','start':2,'end':8}],rollTransitions={'default':choice['match']['rollTransitionStyle']})
            else:plan['effects']=[{**entry,**choice['match']}]
            self.assertIn(choice['id'],planning.selected(plan,planning.catalog()),choice['id'])

    def test_future_reference_is_not_filtered_to_an_old_shortlist(self):
        added=dict(id='reference:R06',group='fixture',trigger='fixture only',match={'templateId':'R06'},objectRole='none')
        with patch('production_layers.specifications',return_value=production_layers.specifications()+[added]):
            choices=planning.catalog()
            selected=planning.selected({'editorialScenes':[{'id':'future','start':0,'end':6,'templateId':'R06'}]},choices)
            self.assertEqual(selected['reference:R06'],['editorialScenes:future'])

    def test_unused_new_candidate_cannot_skip_required_review(self):
        plan={'duration':6,'beats':[],'effects':[],'orchestration':{'segments':[{'id':'s'}],'objectReview':[],
            'candidateReview':[dict(candidateIds=[c['id']],decision='unavailable',segmentIds=[],reason='Technical fixture has no narration or supplied media') for c in planning.catalog() if c['id']!='exit:domain-warp']}}
        with self.assertRaisesRegex(ValueError,'unreviewed candidates: exit:domain-warp'):planning.audit(plan,required=True)

    def test_zero_use_alternatives_and_motion_counts_are_visible(self):
        plan={'duration':10,'beats':[],'effects':[dict(id='one',start=0,end=4,templateId='L02',motion='B',exitMotion='domain-warp'),dict(id='two',start=4,end=7,templateId='L02',motion='D')],
            'editorialScenes':[dict(id='words',start=7,end=10,templateId='R01')]}
        choices=planning.catalog();selected=planning.selected(plan,choices)
        report=planning.usage(plan,choices,selected,{'reference:R05':{'decision':'considered','segmentIds':['s']}})
        rows={r['id']:r for r in report['candidates']};motions={r['id']:r for r in report['motions']}
        self.assertEqual((rows['effect:L02']['count'],rows['effect:L02']['seconds']),(2,7))
        self.assertEqual(rows['exit:domain-warp']['count'],1)
        self.assertEqual(rows['exit:domain-warp']['seconds'],.52)
        self.assertEqual(rows['reference:R05']['alternativeSegmentIds'],['s'])
        self.assertEqual(rows['reference:R05']['count'],0)
        self.assertEqual((motions['B']['count'],motions['D']['count']),(1,1))
        self.assertEqual(set(motions),{'A','B','C','D'})

if __name__=='__main__':unittest.main(verbosity=2)
