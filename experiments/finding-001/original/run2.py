import re,random,collections,os,sys,itertools
sys.path.insert(0,os.path.expanduser('~/yadiktu/src'))
import nulltest as N
from nulltest import cons
random.seed(7)
exec(open(os.path.expanduser('~/yadiktu/src/run.py')).read().split("r_real,h=rate")[0].split('random.seed(42)')[1])  # reuse corpus loading
def rate(ws): return sum(1 for w in ws if N.parse(w))/len(ws)
def bylen(ws):
    d=collections.defaultdict(list)
    for w in ws: d[min(len(w.split('-')),5)].append(w)
    return d
LB=[w.upper() for w in open(os.path.expanduser('~/yadiktu/src/run.py')).read().split("LB='''")[1].split("'''")[0].split()]
realR=set(N.R); base=sorted(N.roots)
print('A. Real Hebrew lexicon:  LA %.3f   LinearB-Greek %.3f'%(rate(uniq),rate(LB)))
for k,v in sorted(bylen(uniq).items()): print(f'   LA len{k}{"+" if k==5 else ""} n={len(v)} {rate(v):.3f}', end='')
print()
for k,v in sorted(bylen(LB).items()): print(f'   LB len{k}{"+" if k==5 else ""} n={len(v)} {rate(v):.3f}', end='')
print()
# B. fake Semitic: random skeletons, same size, same length dist, same per-letter class freq
freq=collections.Counter(c for r in base for c in r); letters=list(freq); wts=[freq[c] for c in letters]
fr=[]
for rep in range(20):
    fake=set()
    while len(fake)<len(base):
        fake.add(''.join(random.choices(letters,wts,k=len(random.choice(base)))))
    FR=set()
    for r in fake: FR|=N.variants(r)
    N.R.clear(); N.R|=FR
    fr.append((rate(uniq),rate(LB)))
N.R.clear(); N.R|=realR
la=[a for a,b in fr]; lb=[b for a,b in fr]
print('B. Random pseudo-lexicons (20 reps, same size & letter freqs):')
print('   LA mean %.3f [%.3f-%.3f]   LinearB-Greek mean %.3f [%.3f-%.3f]'%(sum(la)/20,min(la),max(la),sum(lb)/20,min(lb),max(lb)))
# C. bigger lexicon effect: what if lexicon doubled (paper pools ~8 languages)
print('C. Lexicon size sensitivity (random lexicons of k x Hebrew size):')
for k in (0.5,1,2,4):
    fake=set()
    while len(fake)<int(len(base)*k):
        fake.add(''.join(random.choices(letters,wts,k=len(random.choice(base)))))
    FR=set()
    for r in fake: FR|=N.variants(r)
    N.R.clear(); N.R|=FR
    print(f'   {k}x ({len(fake)} roots): LA {rate(uniq):.3f}   len>=5 LA {rate([w for w in uniq if len(w.split("-"))>=5]):.3f}')
N.R.clear(); N.R|=realR
