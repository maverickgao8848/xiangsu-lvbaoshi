"""Cinema configuration safety and deterministic renderer inputs."""
import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from prepare import SKILL
import material_display


class Cinema(unittest.TestCase):
    def setUp(self):
        self.workspace=tempfile.TemporaryDirectory(prefix='glass-lime-cinema-')
        self.addCleanup(self.workspace.cleanup)
        self.p=Path(self.workspace.name)
        shutil.copytree(SKILL/'assets/material-display',self.p/'assets/glass-lime/material-display')
        self.plan={'beats':[dict(id='one',kind='media',start=0,end=6,image='assets/example.png',display={'style':'cinema'})],'effects':[]}

    def test_valid_kinds(self):
        for kind in material_display.KINDS:
            plan=copy.deepcopy(self.plan);plan['beats'][0]['kind']=kind
            material_display.validate(self.p,plan)

    def test_reject_bad_options(self):
        for cfg in [None,{}, {'style':'television'}, {'style':'cinema','fit':'cover'}, {'style':'cinema','scale':1.3}, {'style':'cinema','light':float('nan')}, {'style':'cinema','scale':True}, {'style':'cinema','unused':1}]:
            with self.subTest(config=cfg):
                plan=copy.deepcopy(self.plan);plan['beats'][0]['display']=cfg
                with self.assertRaises(ValueError):material_display.validate(self.p,plan)

    def test_reject_unsupported_layers(self):
        for kind in ['editorial','interface','material']:
            plan=copy.deepcopy(self.plan);plan['beats'][0]['kind']=kind
            with self.assertRaises(ValueError):material_display.validate(self.p,plan)

    def test_reject_ambiguous_media(self):
        self.plan['beats'][0]['video']='assets/example.mp4'
        with self.assertRaises(ValueError):material_display.validate(self.p,self.plan)

    def test_reject_short_reading(self):
        self.plan['beats'][0]['end']=1.9
        with self.assertRaises(ValueError):material_display.validate(self.p,self.plan)

    def test_reject_unmapped_pixel_callouts(self):
        self.plan['screenEffects']=[dict(targetBeat='one')]
        with self.assertRaises(ValueError):material_display.validate(self.p,self.plan)

    def test_reject_asset_drift(self):
        (self.p/'assets/glass-lime/material-display/style.css').write_text('drift',encoding='utf-8')
        with self.assertRaises(ValueError):material_display.validate(self.p,self.plan)

    def test_optional(self):
        del self.plan['beats'][0]['display']
        shutil.rmtree(self.p/'assets/glass-lime/material-display')
        material_display.validate(self.p,self.plan)


if __name__=='__main__':unittest.main(verbosity=2)
