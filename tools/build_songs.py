"""찬양 목록 폴더의 악보 파일 이름에서 곡명과 키를 뽑아 songs.json을 만든다."""
import json, os, re, sys, unicodedata

ROOT = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else '~/Desktop/00 찬양자료/찬양 목록')
OUT = sys.argv[2] if len(sys.argv) > 2 else 'songs.json'
EXT = re.compile(r'\.(jpe?g|png|gif|jfif|bmp|pdf)$', re.I)
KEY = re.compile(r'(?:^|(?<=[^A-Za-z]))([A-G](?:b|#)?m?)(?:\s*\(\s*([A-G](?:b|#)?m?)\s*\))?(?=$|[^A-Za-z])')
FOLDER_KEY = {'G코드찬양모음': 'G'}
SKIP = {'00 전조 표', '일신배경', '학부모초청예배', '2025 아청일청 사순절 묵상집 최종', '찬양콘티 워크 플로우 - Songs', '주일찬양 250831'}
# 파일 이름 괄호에 적힌 절기 표기 → 앱에서 쓰는 절기 이름
SEASON = {'성탄': '성탄', '대림': '대림', '신년': '신년', '송구영신': '신년', '고난': '고난', '사순': '고난', '종려': '고난',
          '부활': '부활', '성령강림': '성령강림', '감사': '감사', '추수감사': '감사', '맥추감사': '감사'}
SEASON_RE = re.compile(r'\(\s*(' + '|'.join(sorted(SEASON, key=len, reverse=True)) + r')\s*\)|\s(' + '|'.join(SEASON) + r')$')
# 파일 이름에 표기가 없어도 절기에 부르는 곡 (제목 앞부분, 띄어쓰기 없이)
CURATED = {'고요한밤거룩한밤': '성탄', '그맑고환한': '성탄', '그어린주예수': '성탄', '기쁘다구주오셨네': '성탄', '오거룩한밤': '성탄',
           '이땅위에오신': '성탄', '저들밖에': '성탄', '참반가운': '성탄', '천사찬송하기를': '성탄', '천사들의노래가': '성탄',
           '탄일종': '성탄', '흰눈사이로': '성탄', '곧오소서임마누엘': '성탄', '오랫동안기다리던': '대림',
           '갈보리산위에': '고난', '거기너있었는가': '고난', '겟세마네동산에서': '고난', '고난의길': '고난', '그참혹한십자가에': '고난',
           '내가예수를못박았습니다': '고난', '주달려죽은십자가': '고난', '참참참피흘리신': '고난',
           '무덤에머물러': '부활', '주님께영광다시사신주': '부활'}

def nfc(s): return unicodedata.normalize('NFC', s)

def parse(name, default_key=None):
    base = name
    while EXT.search(base): base = EXT.sub('', base)
    base = nfc(base).replace('_', ' ').strip()
    season = ''
    for sm in SEASON_RE.finditer(base): season = SEASON[sm.group(1) or sm.group(2)]
    base = SEASON_RE.sub('', base).strip()
    m = None
    for m in KEY.finditer(base): pass
    if m:
        title, key, rel = base[:m.start()], m.group(1), m.group(2)
    else:
        title, key, rel = base, default_key, None
    title = re.sub(r'\s+', ' ', title).strip(' -_.(')
    title = re.sub(r'\(\s*$', '', title).strip()
    title = re.sub(r'\s+0\d$', '', title).strip()
    tm = re.search(r'\s(' + '|'.join(SEASON) + r')$', title)
    if tm: season, title = season or SEASON[tm.group(1)], title[:tm.start()].strip()
    return title, key, rel, season

songs = {}
for dirpath, dirs, files in os.walk(ROOT):
    rel_dir = os.path.relpath(dirpath, ROOT)
    top = nfc(rel_dir.split(os.sep)[0])
    if top in ('개역개정-한글', 'nanum-all', '찬송가 nwc'): continue
    for f in files:
        if not EXT.search(f): continue
        title, key, relkey, season = parse(f, FOLDER_KEY.get(top))
        if not title or title in SKIP: continue
        gid = re.sub(r'[\s()\[\],.!~\-]', '', title)
        s = songs.setdefault(gid, {'t': title, 'v': []})
        if len(title) > len(s['t']): s['t'] = title
        season = season or next((v for k, v in CURATED.items() if gid.startswith(k)), '')
        if season: s['s'] = season
        path = nfc(os.path.normpath(os.path.join(rel_dir, f)))
        v = [key or '', path]
        if relkey: v.append(relkey)
        s['v'].append(v)

out = sorted(songs.values(), key=lambda s: s['t'])
for s in out: s['v'].sort()
json.dump(out, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'))
keyed = sum(1 for s in out if any(v[0] for v in s['v']))
print('season:', {t: sum(1 for x in out if x.get('s') == t) for t in set(SEASON.values())})
print(f'{len(out)} songs ({keyed} with key), {sum(len(s["v"]) for s in out)} files -> {OUT} ({os.path.getsize(OUT)//1024} KB)')
