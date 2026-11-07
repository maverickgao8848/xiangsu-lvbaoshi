"""Frozen MAV whole-token caption segmentation; no typography overrides."""
import re
def captions(tokens, authored=None, duration=None):
    if authored:
        clean=[t for t in tokens if not re.fullmatch(r'[\s。，？！、,.!?]+',t['text'])]
        stream=''.join(t['text'] for t in clean);cursor=0;result=[]
        # Preserve whole ASR tokens, including CJK words; never invent internal times.
        if any(not t['text'] or not re.fullmatch(r'[\u3400-\u9fffA-Za-z0-9]+',t['text']) for t in clean):raise ValueError('Authored captions require whole aligned CJK/Latin tokens')
        boundaries={0};offset=0;characters=[]
        for token in clean:
            offset+=len(token['text']);boundaries.add(offset)
            characters.extend([token]*len(token['text']))
        for item in authored:
            phrase=item['match'];end=cursor+len(phrase)
            if not phrase or stream[cursor:end]!=phrase:raise ValueError('Caption does not match source at '+str(cursor)+': '+phrase)
            if end not in boundaries:raise ValueError('Caption splits an aligned word: '+phrase)
            display=item.get('text',phrase)
            if not display or len(display)>22:raise ValueError('Caption too long/empty')
            result.append({'start':characters[cursor]['start'],'end':min(characters[end-1]['end']+.15,characters[end]['start'] if end<len(characters) else characters[end-1]['end']+.15),'text':display,'sourceMatch':phrase})
            cursor=end
        if cursor!=len(stream):raise ValueError('Authored captions omit source words')
        if duration is not None:
            for cue in result:cue['end']=min(cue['end'],duration)
        return result
    chunks=[];chunk=[]
    for i,t in enumerate(tokens):
        chunk.append(t);nxt=tokens[i+1] if i+1<len(tokens) else None
        if len(''.join(w['text'] for w in chunk))>=16 or t['text'] in '。，？！、' or not nxt or nxt['start']-t['end']>.45:
            text=''.join(w['text'] for w in chunk).strip('。，？！、')
            if text:chunks.append({'start':chunk[0]['start'],'end':min(t['end']+.18,nxt['start'] if nxt else t['end']+.18),'text':text})
            chunk=[]
    if duration is not None:
        for cue in chunks:cue['end']=min(cue['end'],duration)
    return chunks

