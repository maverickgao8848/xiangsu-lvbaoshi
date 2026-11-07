"""Validate the A navigation-progress contract and its standalone composition build."""
import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from prepare import SKILL, dump
import navigation
import effect_planning


class NavigationProgress(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix='glass-lime-navigation-')
        self.p = Path(self.workspace.name)
        (self.p / 'assets/glass-lime').mkdir(parents=True)
        shutil.copytree(SKILL / 'assets/navigation-progress', self.p / 'assets/glass-lime/navigation-progress')
        (self.p / 'compositions').mkdir()
        self.chapters = [
            {'number': '01', 'title': '开场', 'start': 0},
            {'number': '02', 'title': '关系', 'start': 22},
            {'number': '03', 'title': '机制', 'start': 58},
            {'number': '04', 'title': '结论', 'start': 94},
        ]
        dump(self.p / 'chapters.json', self.chapters)
        self.plan = {'id': 'nav-test', 'duration': 126, 'navigation': {'progress': True}}

    def tearDown(self):
        self.workspace.cleanup()

    def reject(self, change):
        plan = copy.deepcopy(self.plan)
        change(plan)
        with self.assertRaises(ValueError):
            navigation.validate(self.p, plan, {'nav-test'})

    def test_01_resolve_and_validate(self):
        chapters = navigation.resolve(self.p, 126)
        self.assertEqual([c['end'] for c in chapters], [22, 58, 94, 126])
        ids = {'nav-test'}
        self.assertEqual(navigation.validate(self.p, self.plan, ids), chapters)
        self.assertIn('navigation-progress', ids)

    def test_02_build_composition_and_layer(self):
        layer, info = navigation.build(self.p, self.plan, '/* fonts */')
        page = (self.p / 'compositions/navigation-progress.html').read_text(encoding='utf-8')
        self.assertIn('data-composition-id="navigation-progress"', page)
        self.assertIn('GLNavProgress.mount', page)
        self.assertIn('开场', page)
        self.assertIn('navigation-progress', layer)
        self.assertIn('z-index:46', layer)
        self.assertEqual(info['chapterCount'], 4)
        self.assertEqual(info['chapters'][-1]['end'], 126)

    def test_03_catalog_and_selection(self):
        choices = effect_planning.catalog()
        self.assertIn('navigation:progress', {choice['id'] for choice in choices})
        selected = effect_planning.selected(self.plan, choices)
        self.assertIn('navigation:progress', selected)

    def test_04_dict_chapters_file(self):
        dump(self.p / 'chapters.json', {'chapters': self.chapters})
        self.assertEqual(len(navigation.resolve(self.p, 126)), 4)

    def test_05_single_chapter(self):
        dump(self.p / 'chapters.json', [{'number': '01', 'title': '全片', 'start': 0}])
        chapters = navigation.resolve(self.p, 126)
        self.assertEqual((chapters[0]['start'], chapters[0]['end']), (0, 126))

    def test_06_reject_missing_file(self):
        (self.p / 'chapters.json').unlink()
        with self.assertRaisesRegex(ValueError, 'chapters.json'):
            navigation.resolve(self.p, 126)

    def test_07_reject_first_chapter_not_zero(self):
        dump(self.p / 'chapters.json', [{'number': '01', 'title': '开场', 'start': 2}])
        with self.assertRaisesRegex(ValueError, 'first chapter'):
            navigation.resolve(self.p, 126)

    def test_08_reject_unsorted(self):
        dump(self.p / 'chapters.json', [
            {'number': '01', 'title': '开场', 'start': 0},
            {'number': '02', 'title': '关系', 'start': 30},
            {'number': '03', 'title': '机制', 'start': 20},
        ])
        with self.assertRaisesRegex(ValueError, 'increase strictly'):
            navigation.resolve(self.p, 126)

    def test_09_reject_duplicate_number(self):
        dump(self.p / 'chapters.json', [
            {'number': '01', 'title': '开场', 'start': 0},
            {'number': '01', 'title': '关系', 'start': 30},
        ])
        with self.assertRaisesRegex(ValueError, 'unique'):
            navigation.resolve(self.p, 126)

    def test_10_reject_long_title(self):
        dump(self.p / 'chapters.json', [{'number': '01', 'title': '这是一个超过十四个字符的章节标题', 'start': 0}])
        with self.assertRaisesRegex(ValueError, 'titles'):
            navigation.resolve(self.p, 126)

    def test_11_reject_short_tail(self):
        dump(self.p / 'chapters.json', [
            {'number': '01', 'title': '开场', 'start': 0},
            {'number': '02', 'title': '结论', 'start': 125.5},
        ])
        with self.assertRaisesRegex(ValueError, 'one second'):
            navigation.resolve(self.p, 126)

    def test_12_accept_disabled_and_reject_extra_navigation(self):
        disabled = copy.deepcopy(self.plan)
        disabled['navigation']['progress'] = False
        self.assertIsNone(navigation.validate(self.p, disabled, {'nav-test'}))
        self.reject(lambda plan: plan.update(navigation={'progress': True, 'chapters': []}))

    def test_16_strict_duration_threshold_and_explicit_override(self):
        for duration, enabled in [(179, False), (180, False), (180.001, True), (181, True)]:
            with self.subTest(duration=duration):
                source = {'duration': duration}
                self.assertEqual(navigation.effective_plan(source)['navigation']['progress'], enabled)
                self.assertNotIn('navigation', source)
        self.assertFalse(navigation.effective_plan({'duration': 240, 'navigation': {'progress': False}})['navigation']['progress'])
        self.assertTrue(navigation.effective_plan({'duration': 60, 'navigation': {'progress': True}})['navigation']['progress'])

    def test_17_new_freeze_default_and_historical_compatibility(self):
        plan = {'id': 'nav-test', 'duration': 240}
        self.assertFalse(navigation.effective_plan(plan, {})['navigation']['progress'])
        self.assertTrue(navigation.effective_plan(plan, {'navigationDefaultsVersion': navigation.DEFAULTS_VERSION})['navigation']['progress'])
        with self.assertRaisesRegex(ValueError, 'defaults version'):
            navigation.effective_plan(plan, {'navigationDefaultsVersion': 'unknown'})

    def test_18_long_draft_exposes_chapter_requirement(self):
        from plan import skeleton
        dump(self.p / 'input-lock.json', {'profile': 'glass-lime-editorial-kit/v1', 'duration': 181, 'navigationDefaultsVersion': navigation.DEFAULTS_VERSION})
        dump(self.p / 'words.json', {'tokens': []})
        draft = skeleton(self.p)
        self.assertTrue(draft['navigation']['progress'])
        self.assertTrue(any('chapters.json' in i['need'] for i in draft['orchestration']['segments'][0]['inputs']))

    def test_19_default_navigation_is_selected_without_opt_in(self):
        selected = effect_planning.selected({'id': 'long', 'duration': 181}, effect_planning.catalog())
        self.assertIn('navigation:progress', selected)

    def test_13_reject_id_collision(self):
        plan = copy.deepcopy(self.plan)
        plan['id'] = 'navigation-progress'
        with self.assertRaisesRegex(ValueError, 'collides'):
            navigation.validate(self.p, plan, {'navigation-progress'})

    def test_14_reject_frozen_asset_drift(self):
        style = self.p / 'assets/glass-lime/navigation-progress/style.css'
        style.write_text(style.read_text(encoding='utf-8') + '\n/* drift */\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'renderer changed'):
            navigation.validate(self.p, self.plan, {'nav-test'})

    def test_15_build_without_navigation_removes_stale(self):
        navigation.build(self.p, self.plan, '/* fonts */')
        self.assertTrue((self.p / 'compositions/navigation-progress.html').is_file())
        plan = {'id': 'nav-test', 'duration': 126}
        layer, info = navigation.build(self.p, plan, '/* fonts */')
        self.assertIsNone(layer)
        self.assertIsNone(info)
        self.assertFalse((self.p / 'compositions/navigation-progress.html').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
