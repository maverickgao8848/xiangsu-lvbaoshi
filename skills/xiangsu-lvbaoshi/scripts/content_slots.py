"""Typed production slots derived from actual template HTML, never demo facts."""
from html.parser import HTMLParser
import json,re,subprocess
from pathlib import Path
class Slots(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.stack=[];self.text=[];self.images=[]
    def handle_starttag(self,tag,attrs):
        if tag=='img':self.images.append(dict(attrs).get('src',''))
        if tag not in ('img','br','hr','input','meta','link'):self.stack.append(tag)
    def handle_endtag(self,tag):
        if tag in self.stack:
            while self.stack.pop()!=tag:pass
    def handle_data(self,value):
        if value.strip() and 'svg' not in self.stack and not re.fullmatch(r'[\s↗→↓↑＋+−×·•]+',value):self.text.append(value.strip())
def render(entries,assets=None):
    script=Path(__file__).with_name('render_templates.mjs')
    return json.loads(subprocess.check_output(['node',str(script)]+([str(assets)] if assets else []),input=json.dumps(entries).encode()))
def slots(body):
    p=Slots();p.feed(body);return {'text':p.text,'images':p.images}
if __name__=='__main__':
    from prepare import SKILL,read
    entries=[dict(id=x['id'],templateId=x['id']) for x in read(SKILL/'references/effect-catalog.json')]
    print(json.dumps({x['id']:slots(x['body']) for x in render(entries)},ensure_ascii=True,indent=2))
