import re,random,collections,json,sys,os
sys.path.insert(0,os.path.expanduser('~/yadiktu/src'))
from nulltest import parse,cons,R
random.seed(42)
s=open(os.path.expanduser('~/yadiktu/la.js')).read()
words=[]
for m in re.finditer(r'"transliteratedWords": \[(.*?)\]',s,re.S):
    for w in re.findall(r'"([^"]+)"',m.group(1)):
        sy=w.split('-')
        if len(sy)>=2 and all(cons(x) not in ('?',) and re.match(r'^(\*301|[A-Z]+\d?)$',x) for x in sy):
            words.append(w)
uniq=sorted(set(words))
syl=[x for w in words for x in w.split('-')]
def rate(ws):
    h=[w for w in ws if parse(w)]; return len(h)/len(ws),h
r_real,h=rate(uniq)
print('Linear A unique sign-groups (>=2 signs):',len(uniq),' hit rate %.3f'%r_real)
# null 1: random strings, same length distribution, corpus syllable frequencies
nulls=[]
for rep in range(20):
    fake=['-'.join(random.choice(syl) for _ in w.split('-')) for w in uniq]
    nulls.append(rate(fake)[0])
print('Random syllable strings (20 reps): mean %.3f  min %.3f  max %.3f'%(sum(nulls)/20,min(nulls),max(nulls)))
# by length
by=collections.defaultdict(list)
for w in uniq: by[len(w.split('-'))].append(w)
for L in sorted(by):
    if len(by[L])<10: continue
    fk=['-'.join(random.choice(syl) for _ in range(L)) for _ in range(2000)]
    print(f'  len {L}: real {rate(by[L])[0]:.3f} (n={len(by[L])})   random {rate(fk)[0]:.3f}')
# null 2: Linear B words of KNOWN Greek meaning
LB='''a-to-ro-qo ko-no-so pa-i-to po-ti-ni-ja wa-na-ka qa-si-re-u e-ra-wo ti-ri-po di-pa pa-te ma-te i-qo
ko-wo ko-wa e-re-ta ka-ke-u i-je-re-u i-je-re-ja do-e-ro do-e-ra te-o po-me ra-wa-ke-ta e-qe-ta
ka-ra-wi-po-ro ku-ru-so a-ku-ro ko-ri-ja-do-no ku-mi-no se-ri-no ma-ra-tu-wo e-ra-wa me-ri
ku-pa-ro wo-no si-to o-no ta-ra-si-ja a-pi-po-re-we qe-to ka-ra-te-ra ke-ra-me-u to-ko-so-wo-ko
a-re-ka-sa-da-ra e-ke-ra-wo pu-ro tu-ri-so a-mi-ni-so ra-pa-to ku-do-ni-ja e-ra-to a-ki-ri-ja
di-wo di-wi-ja e-ma-a2 po-se-da-o-ne a-ta-na-po-ti-ni-ja e-nu-wa-ri-jo pa-ja-wo-ne a-re
ka-ko pe-di-ra pa-ka-na e-ka-ra te-me-no ke-ke-me-na ko-to-na pe-mo o-pe-ro e-ke-e a-ke-re
de-ka-sa-to a-pu-do-si e-ko-si ti-mi-to-a-ke-e ra-wo e-ra-pe-me-na ka-na-pe-u a-re-pa-zo-o'''.split()
r_lb,hlb=rate(LB)
print(f'Linear B Greek words: n={len(LB)} hit rate {r_lb:.3f}')
for w in hlb[:25]: print('   ',w,parse(w))
json.dump({'la':r_real,'null':nulls,'lb':r_lb},open(os.path.expanduser('~/yadiktu/results.json'),'w'))
