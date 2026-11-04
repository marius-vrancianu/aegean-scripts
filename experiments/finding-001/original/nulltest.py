"""Null-model test of the 'Ya Diktu' root-matching method.
Machine encodes the paper's own licences: stop/sibilant/liquid mergers, laryngeals as pure-vowel
signs or unwritten, one unwritten weak radical, doubled signs collapse, prefix/suffix menus.
Lexicon: Hebrew verb lemmas only (Strong's, openscriptures) -- far smaller than the paper's pool
(Hebrew+Ugaritic+Akkadian+Aramaic+Arabic+Ge'ez+Amorite+Phoenician+Egyptian+Hurrian)."""
import re, random, json, itertools, sys, collections
random.seed(1)
import os; D=os.path.expanduser('~/yadiktu/')
# ---- Hebrew roots
xml=open(D+'HebrewStrong.xml',encoding='utf8').read()
CL={'א':'H','ה':'H','ח':'H','ע':'H','ב':'P','פ':'P','ף':'P','ג':'K','כ':'K','ך':'K','ק':'K',
    'ד':'D','ט':'T','ת':'T','צ':'S','ץ':'S','ז':'S','ס':'S','ש':'S','ל':'R','ר':'R',
    'מ':'M','ם':'M','נ':'N','ן':'N','ו':'W','י':'J'}
roots=set()
for m in re.finditer(r'<w pos="v"[^>]*xml:lang="(heb|arc)">([^<]+)</w>',xml):
    w=re.sub(r'[֑-ׇ]','',m.group(2))
    sk=''.join(CL.get(c,'') for c in w)
    if 2<=len(sk)<=4: roots.add(sk)
# also allow ṣ via T (paper's emphatic claim) and d/t interchange the paper uses: expand
def variants(sk):
    out={sk}
    opts=[{'T','S'} if c=='S' else {'D','T'} if c in 'DT' else {c} for c in sk]
    for p in itertools.product(*opts): out.add(''.join(p))
    return out
R=set()
for r in roots: R|=variants(r)
# ---- sign -> consonant class (None = pure vowel / laryngeal-or-nothing)
def cons(s):
    s=s.upper()
    if s=='*301': return 'N'
    if s in('A','E','I','O','U','AU','A3'): return None
    m=re.match(r'(PU2|PA3|RA2|RO2|TA2|TWE|TWO|DWE|DWO|NWA|SWA|SWI|PTE|RA3|AI)$',s)
    if m: return {'PU2':'P','PA3':'P','RA2':'R','RO2':'R','RA3':'R','TA2':'T','TWE':'T','TWO':'T','DWE':'D','DWO':'D','NWA':'N','SWA':'S','SWI':'S','PTE':'P','AI':None}[s]
    c=s[0]
    return {'J':'J','W':'W','Q':'K','K':'K','P':'P','T':'T','D':'D','S':'S','Z':'S','R':'R','M':'M','N':'N'}.get(c,'?')
PRE=[('A',),('TA',),('JA',),('I',),('U','NA'),('NA',),('WA',),('RA',),('A','TA'),('TA','NA'),('JA','TA'),('A','NA')]
SUF=[('ME',),('MA',),('TU',),('TI',),('TE',),('NU',),('JA',),('SE',),('I',),('KA',),('NA',),('NE',),('TI','NU'),('U','TI','NU'),('MI','NA'),('TE','TE')]
def cores(sy):
    """yield candidate consonant skeletons for a core syllable list"""
    # collapse doubled identical signs
    s2=[x for i,x in enumerate(sy) if i==0 or x!=sy[i-1]]
    slots=[cons(x) for x in s2]
    if '?' in slots: return
    # each vowel slot -> 'H' or nothing
    vidx=[i for i,c in enumerate(slots) if c is None]
    for choice in itertools.product([0,1],repeat=len(vidx)):
        sk=[]
        for i,c in enumerate(slots):
            if c is None:
                if choice[vidx.index(i)]: sk.append('H')
            else: sk.append(c)
        sk=''.join(sk)
        yield sk
        if len(sk)==2:   # one unwritten weak radical
            for pos in range(3):
                for w in 'HWJ': yield sk[:pos]+w+sk[pos:]
def parse(word):
    sy=tuple(word.split('-'))
    for p in [()]+PRE:
        if sy[:len(p)]!=p: continue
        for s in [()]+SUF:
            if len(s) and sy[len(sy)-len(s):]!=s: continue
            core=sy[len(p):len(sy)-len(s)]
            if not 1<=len(core)<=4: continue
            for sk in cores(list(core)):
                if 2<=len(sk)<=4 and sk in R:
                    return ('-'.join(p),'-'.join(core),'-'.join(s),sk)
    return None
if __name__=='__main__':
    print('Hebrew verb skeletons:',len(roots),' with paper\'s mergers:',len(R))
    for w in ['A-TA-I-*301-WA-JA','JA-DI-KI-TU','JA-SA-SA-RA-ME','U-NA-KA-NA-SI','I-PI-NA-MA','SI-RU-TE','TA-NA-RA-TE-U-TI-NU']:
        print(w,parse(w))
