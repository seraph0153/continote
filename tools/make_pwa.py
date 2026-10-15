"""공개용 콘티노트(웹앱) 만들기: src/conti.src.html → docs/index.html

claude.ai 아티팩트판과 같은 원본에서 출발해, claude.ai 전용 기능을 바꾼다.
- 곡 목록: 내장 목록 없이 시작, 사용자가 불러온 악보 파일 이름으로 만든다
- 악보·곡 목록·기록: 이 기기의 IndexedDB에 저장(서버로 보내지 않음), 악보 그림은 서비스워커가 score/<해시>로 내준다
- Claude 추천·초안: 뺀다
- 예배 종류: 사용자가 설정
- 파일 저장: 저장 위치 고르기(지원 브라우저) / 폰은 공유 창
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(ROOT, 'src', 'conti.src.html'), encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:100])
    s = s.replace(old, new)


def rep_between(start, end, new):
    global s
    i = s.index(start)
    j = s.index(end, i)
    s = s[:i] + new + s[j:]


# ---------------------------------------------------------------- 문서 머리
HEAD = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="기준곡 하나로 시작하는 찬양 콘티. 같은 키 후보곡, 화음 듣기, 마디 진행, A4 콘티 파일까지 무료로 쓰는 찬양 인도자 도구.">
<meta name="theme-color" content="#24368f">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/icon-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="콘티노트">
<style>
:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px/1.5 system-ui,-apple-system,sans-serif}
img{max-width:100%}
[hidden]{display:none!important}
</style>
'''
rep('<title>찬양 콘티</title>', HEAD + '<title>콘티노트</title>')
s = s.replace('</style>\n\n<div class="wrap">', '</style>\n</head>\n<body>\n<div class="wrap">', 1)
assert '</head>\n<body>' in s
s = s.replace('<body>\n<div class="wrap">', '<body>\n<div class="wrap">\n  <div id="installBar"></div>', 1)
s = s.rstrip() + '\n</body>\n</html>\n'

# ---------------------------------------------------------------- 화면
rep('<h1 class="brand">찬양 콘티<small>기준곡 하나로 시작하는 한 주의 찬양 순서</small></h1>',
    '<h1 class="brand">콘티노트<small>기준곡 하나로 시작하는 찬양 콘티</small></h1>')
rep('''    <button class="btn histbtn" id="histBtn" type="button">기록</button>''',
    '''    <button class="btn histbtn" id="histBtn" type="button">기록</button>
    <button class="btn" id="setBtn" type="button">설정</button>
    <button class="btn primary" id="installBtn" type="button" hidden>앱 설치</button>''')
rep('''        <button role="tab" id="tab-draft" aria-selected="false" aria-controls="p-draft">초안<small>묵상으로 한 번에</small></button>\n''', '')
rep('''      <div role="tabpanel" id="p-draft" aria-labelledby="tab-draft" hidden></div>\n''', '')
rep('<label class="hint" for="med">이번 주 묵상 · 본문</label>', '<label class="hint" for="med">이번 주 묵상 · 본문 (기록에 함께 저장돼요)</label>')
rep('<div class="dlg-head"><h3 id="smTitle">악보 연결</h3>', '<div class="dlg-head"><h3 id="smTitle">악보</h3>')
rep('''<input type="file" id="folderIn" webkitdirectory multiple hidden>''', '''<dialog class="dlg" id="setDlg" aria-labelledby="setTitle">
  <div class="dlg-head"><h3 id="setTitle">설정</h3><button class="icon" type="button" data-close aria-label="닫기">✕</button></div>
  <div class="dlg-body" id="setBody"></div>
</dialog>
<input type="file" id="folderIn" webkitdirectory multiple hidden>
<input type="file" id="filesIn" accept="image/*" multiple hidden>
<input type="file" id="addIn" accept="image/*" multiple hidden>
<input type="file" id="restoreIn" accept="application/json,.json" hidden>''')
rep('<script id="songs-data" type="application/json">__SONGS__</script>\n', '')
rep(".toast{position:fixed;", """.svc-list{display:flex;flex-direction:column;gap:8px}
.svc-row{display:grid;grid-template-columns:minmax(0,1fr) auto auto auto auto;gap:6px 8px;align-items:center}
.svc-row select{border:1px solid var(--line-strong);background:var(--paper);border-radius:6px;padding:6px;font-size:14px}
.svc-row .tapadd{margin:0;white-space:nowrap}
@media (max-width:560px){.svc-row{grid-template-columns:minmax(0,1fr) auto auto;}}
.onboard{border:1px dashed var(--line-strong);border-radius:10px;padding:14px;display:flex;flex-direction:column;gap:10px;margin-bottom:10px}
.onboard b{font-family:var(--f-display);font-size:18px}
.edit-form{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px;margin-bottom:12px;border:1px solid var(--line);border-radius:8px;background:var(--surface)}
.edit-form input{flex:1 1 200px;min-width:0}
.edit-form select{border:1px solid var(--line-strong);background:var(--paper);border-radius:6px;padding:6px;font-size:14px}
.install-bar{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;margin:0 0 12px;padding:12px 14px;border-radius:12px;background:var(--navy);color:var(--navy-ink)}
.install-bar b{font-size:15px}
.install-bar .ib-text{flex:1 1 220px;font-size:13.5px;line-height:1.5}
.install-bar ol{margin:4px 0 0;padding-left:20px}
.install-bar .btn{background:var(--navy-ink);color:var(--navy);border-color:var(--navy-ink);font-weight:600}
.install-bar .btn.ib-close{background:transparent;color:var(--navy-ink);border-color:currentColor;font-weight:400}
.install-bar a.btn{text-decoration:none;display:inline-block}
.share-ico{display:inline-block;width:1.15em;height:1.15em;vertical-align:-.2em;margin:0 2px}
.share-box{display:flex;flex-wrap:wrap;gap:12px 16px;align-items:center}
.share-box canvas{width:160px;height:160px;border-radius:8px;background:#ffffff;padding:8px}
.share-url{font-family:var(--f-mono);font-size:13px;overflow-wrap:anywhere}
.toast{position:fixed;""")

# ---------------------------------------------------------------- 곡 목록: 비어서 시작
rep("const SONGS = JSON.parse(document.getElementById('songs-data').textContent);", "const SONGS = [];")

# ---------------------------------------------------------------- 예배: 사용자가 설정
rep_between("const SVC = {", "const pad = n =>", r'''const DEFAULT_SVC = {
  sun1: {name: '주일 1부', count: 4, dow: 0, label: '주일 1부', skipEdge: false},
  sun2: {name: '주일 오후', count: 4, dow: 0, label: '주일 오후예배', skipEdge: false},
  wed: {name: '수요예배', count: 4, dow: 3, label: '수요예배', skipEdge: false},
  fri: {name: '금요기도회', count: 6, dow: 5, label: '금요기도회', skipEdge: false}
};
const SVC_STORE = 'continote.services.v1';
let SVC = (() => { try { const v = JSON.parse(localStorage.getItem(SVC_STORE) || 'null'); if (v && Object.keys(v).length) return v; } catch (e) {} return JSON.parse(JSON.stringify(DEFAULT_SVC)); })();
const saveSvc = () => { try { localStorage.setItem(SVC_STORE, JSON.stringify(SVC)); } catch (e) {} };
const firstSvc = () => Object.keys(SVC)[0];
''')
rep('''function nextDate(svc) {
  const now = new Date(), d = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  while (d.getDay() !== SVC[svc].dow) d.setDate(d.getDate() + 1);
  if (svc === 'pm') while (firstOrLastSunday(d)) d.setDate(d.getDate() + 7);
  return ymd(d);
}''', '''function nextDate(svc) {
  const sv = SVC[svc] || SVC[firstSvc()];
  const now = new Date(), d = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  while (d.getDay() !== sv.dow) d.setDate(d.getDate() + 1);
  if (sv.skipEdge) while (firstOrLastSunday(d)) d.setDate(d.getDate() + 7);
  return ymd(d);
}''')

# ---------------------------------------------------------------- 상태
rep("const STORE = 'chanyang-conti.v2';", "const STORE = 'continote.state.v1';")
rep("function fresh(svc = 'fri') {", "function fresh(svc = firstSvc()) {")
rep_between("function exampleState() {", "function save() {", r'''function load() {
  try {
    const raw = localStorage.getItem(STORE);
    if (raw) {
      const s = Object.assign(fresh(), JSON.parse(raw));
      if (!SVC[s.svc]) s.svc = firstSvc();
      if (s.tab === 'draft') s.tab = 'rec';
      return s;  // 곡 번호는 곡 목록을 읽은 뒤 relinkState()로 다시 맞춘다
    }
  } catch (e) {}
  return fresh();
}
// 곡 목록이 바뀐 뒤 콘티의 곡 번호를 제목으로 다시 찾는다(없어진 곡은 제목만 남김)
function relinkState() {
  state.slots = state.slots.map(x => {
    if (!x) return null;
    const song = SONGS[x.id];
    if (song && song.t === x.t) return x;
    const by = BY_NORM.get(norm(x.t));
    return {...x, id: by ? by.id : -1};
  });
  if (state.base) {
    const b = SONGS[state.base.id] && SONGS[state.base.id].t === state.base.t ? SONGS[state.base.id] : BY_NORM.get(norm(state.base.t || ''));
    state.base = b ? {...state.base, id: b.id} : null;
  }
}
''')

# ---------------------------------------------------------------- 기준곡: 곡이 없을 때 안내
rep("""  if (!song) { fill(view, h('p', {class: 'hint', style: 'margin-bottom:10px', text: '모티브가 되는 메인곡을 먼저 고르세요. 이 곡의 키가 콘티 전체의 키가 돼요.'})); return; }""",
    """  if (!song && !SONGS.length) {
    fill(view, h('div', {class: 'onboard'},
      h('b', {text: '먼저 악보를 불러오세요'}),
      h('p', {class: 'hint', text: '가지고 있는 악보 그림 파일을 불러오면 파일 이름으로 곡 목록이 만들어져요. "시선 D.png"처럼 곡명 뒤에 키를 붙여 두면 키도 자동으로 들어가요. 악보는 이 기기 안에만 저장돼요.'}),
      h('div', {class: 'row-btns'}, h('button', {class: 'btn primary', type: 'button', onclick: openScoreDialog}, '악보 불러오기'))));
    return;
  }
  if (!song) { fill(view, h('p', {class: 'hint', style: 'margin-bottom:10px', text: '모티브가 되는 메인곡을 먼저 고르세요. 이 곡의 키가 콘티 전체의 키가 돼요.'})); return; }""")

# ---------------------------------------------------------------- Claude 기능 빼기
rep("    aiBox('rank'),\n", '')
rep_between("function renderDraft() {", "/* ---------- 악보:", '')
rep_between("/* ---------- Claude ---------- */", "function renderPick() {", '')
rep("""function renderPick() {
  ['rec', 'all', 'draft'].forEach(t => {""", """function renderPick() {
  ['rec', 'all'].forEach(t => {""")
rep("  if (state.tab === 'draft') renderDraft();\n", '')
rep("['rec', 'all', 'draft'].forEach(t => $('#tab-' + t)", "['rec', 'all'].forEach(t => $('#tab-' + t)")

# ---------------------------------------------------------------- 콘티 메모·빈 칸·예시
rep("""  if (state.svc === 'fri') { const send = new Date(d); send.setDate(d.getDate() - 1); note.textContent = `${send.getMonth() + 1}월 ${send.getDate()}일 목요일 오전에 보내기`; }
  else if (state.svc === 'pm' && d.getDay() === 0 && firstOrLastSunday(d)) { note.textContent = '이 날은 첫째 주나 마지막 주라 오후 찬양이 없는 주예요.'; note.className = 'paper-note warn'; }
  else if (d.getDay() !== SVC[state.svc].dow) { note.textContent = `${SVC[state.svc].name} 요일과 날짜가 달라요.`; note.className = 'paper-note warn'; }
  else note.textContent = state.svc === 'am' ? '격주로 드리는 주일 오전 찬양' : '첫째·마지막 주를 뺀 주일 오후';""",
"""  const sv = SVC[state.svc];
  if (sv && sv.skipEdge && firstOrLastSunday(d)) { note.textContent = '이 날은 첫째 주나 마지막 주라 빠지는 주예요.'; note.className = 'paper-note warn'; }
  else if (sv && d.getDay() !== sv.dow) { note.textContent = `${sv.name} 요일(${WD[sv.dow]})과 날짜가 달라요.`; note.className = 'paper-note warn'; }
  else note.textContent = sv ? `매주 ${WD[sv.dow]}요일 · ${sv.count}곡` : '';""")
rep("text: state.svc === 'fri' && i === n - 1 ? '통성기도로 넘어갈 곡' : '비어 있음'", "text: '비어 있음'")
rep("state = fresh('fri'); recLimit = {}; aiRank = null; commit(); toast('새 금요찬양 콘티를 시작해요');", "state = fresh(); recLimit = {}; aiRank = null; commit(); toast('새 콘티를 시작해요');")
rep("  state.svc = c.svc in SVC ? c.svc : 'fri';", "  state.svc = c.svc in SVC ? c.svc : firstSvc();")

# ---------------------------------------------------------------- 악보: 이 기기(IndexedDB)에 저장
SCORES = r'''/* ---------- 악보·곡 목록: 이 기기(IndexedDB)에 저장, 어디에도 보내지 않음 ---------- */
const fnv = str => { let x = 0x811c9dc5; for (const ch of str) { x ^= ch.codePointAt(0); x = Math.imul(x, 0x01000193) >>> 0; } return x.toString(16).padStart(8, '0'); };
const KNOWN = new Map(), PH = new Map();
const INDEX = new Map();      // 저장된 악보: 경로 해시 → true
const LOCAL = new Map();      // 이번에 고른 파일(저장 전에도 바로 보기)
const VER = new Map(), BLOBURL = new Map(), LOADING = new Set(), LURL = new WeakMap();
let PV = null, PV_URLS = [], upRun = null, upMsg = '', upErr = false, USAGE = null, EXTRA = {}, SMC = false;

// IndexedDB: files(해시 → {blob,type,path}), docs('songs' → {경로: [제목, 키, 절기]}), contis(id → 콘티)
const req = r => new Promise((ok, no) => { r.onsuccess = () => ok(r.result); r.onerror = () => no(r.error); });
let IDBP = null;
function idb() {
  if (!IDBP) IDBP = new Promise((ok, no) => {
    const r = indexedDB.open('continote', 1);
    r.onupgradeneeded = () => { const d = r.result; ['files', 'docs', 'contis'].forEach(n => { if (!d.objectStoreNames.contains(n)) d.createObjectStore(n); }); };
    r.onsuccess = () => ok(r.result);
    r.onerror = () => no(r.error);
  });
  return IDBP;
}
const done = t => new Promise((ok, no) => { t.oncomplete = () => ok(); t.onerror = () => no(t.error); t.onabort = () => no(t.error); });
async function dbGet(store, key) { const d = await idb(); return req(d.transaction(store).objectStore(store).get(key)); }
async function dbPut(store, key, val) { const d = await idb(); const t = d.transaction(store, 'readwrite'); t.objectStore(store).put(val, key); return done(t); }
async function dbDel(store, key) { const d = await idb(); const t = d.transaction(store, 'readwrite'); t.objectStore(store).delete(key); return done(t); }
async function dbClear(store) { const d = await idb(); const t = d.transaction(store, 'readwrite'); t.objectStore(store).clear(); return done(t); }
async function dbKeys(store) { const d = await idb(); return req(d.transaction(store).objectStore(store).getAllKeys()); }
async function dbAll(store) { const d = await idb(); const st = d.transaction(store).objectStore(store); const [ks, vs] = await Promise.all([req(st.getAllKeys()), req(st.getAll())]); return ks.map((k, i) => [k, vs[i]]); }
const histSort = (a, b) => String(b.date).localeCompare(String(a.date)) || String(a.svc).localeCompare(String(b.svc));

(async () => {
  await null;  // 아래 함수·상수가 모두 정의된 뒤에 시작
  try {
    EXTRA = (await dbGet('docs', 'songs')) || {};
    rebuildSongs();
    (await dbKeys('files')).forEach(k => INDEX.set(k, true));
    HIST = (await dbAll('contis')).map(([id, v]) => ({id, ...v})).sort(histSort);
    rebuildUsage();
  } catch (e) { toast('이 브라우저에서는 저장 공간을 쓸 수 없어요. 개인 정보 보호 모드인지 확인해 주세요'); }
  relinkState(); commit(); renderHistBtn(); renderScoreStatus();
  try { if (navigator.storage && navigator.storage.persist) navigator.storage.persist(); } catch (e) {}
})();

const SEASON_MAP = {'성탄': '성탄', '대림': '대림', '신년': '신년', '송구영신': '신년', '고난': '고난', '사순': '고난', '종려': '고난',
  '부활': '부활', '성령강림': '성령강림', '감사': '감사', '추수감사': '감사', '맥추감사': '감사'};
// 파일 이름에 절기 표시가 없어도 절기에 부르는 곡(제목 앞부분, 띄어쓰기 없이)
const CURATED = {'고요한밤거룩한밤': '성탄', '그맑고환한': '성탄', '그어린주예수': '성탄', '기쁘다구주오셨네': '성탄', '오거룩한밤': '성탄',
  '이땅위에오신': '성탄', '저들밖에': '성탄', '참반가운': '성탄', '천사찬송하기를': '성탄', '천사들의노래가': '성탄', '탄일종': '성탄',
  '곧오소서임마누엘': '성탄', '오랫동안기다리던': '대림', '갈보리산위에': '고난', '거기너있었는가': '고난', '겟세마네동산에서': '고난',
  '그참혹한십자가에': '고난', '내가예수를못박았습니다': '고난', '주달려죽은십자가': '고난', '무덤에머물러': '부활', '주님께영광다시사신주': '부활'};
const IMG_EXT = /\.(jpe?g|png|gif|jfif|webp|bmp)$/i;
// 파일 이름 "곡명 키(관계조) 00.jpg" → {title, key, season}
function parseName(name) {
  let base = name.normalize('NFC');
  while (/\.(jpe?g|png|gif|jfif|bmp|webp|pdf)$/i.test(base)) base = base.replace(/\.(jpe?g|png|gif|jfif|bmp|webp|pdf)$/i, '');
  base = base.replace(/_/g, ' ').trim();
  let season = '';
  const words = Object.keys(SEASON_MAP).sort((a, b) => b.length - a.length).join('|');
  base = base.replace(new RegExp('\\(\\s*(' + words + ')\\s*\\)', 'g'), (m0, w) => { season = SEASON_MAP[w]; return ''; }).trim();
  const re = /(?:^|(?<=[^A-Za-z]))([A-G](?:b|#)?m?)(?:\s*\(\s*([A-G](?:b|#)?m?)\s*\))?(?=$|[^A-Za-z])/g;
  let m, last = null;
  while ((m = re.exec(base))) last = m;
  let title = last ? base.slice(0, last.index) : base;
  title = title.replace(/\s+/g, ' ').replace(/^[\s\-_.(]+|[\s\-_.(]+$/g, '').replace(/\(\s*$/, '').replace(/\s+0\d$/, '').trim();
  const tm = new RegExp('\\s(' + words + ')$').exec(title);
  if (tm) { season = season || SEASON_MAP[tm[1]]; title = title.slice(0, tm.index).trim(); }
  return {title, key: last ? last[1] : '', season};
}
function addSongFile(path, info) {
  const n = norm(info.title);
  if (!n || KNOWN.has(path)) return false;
  let s = BY_NORM.get(n);
  if (!s) { s = {t: info.title, v: [], id: SONGS.length, n, c: cho(n), keys: [], kn: []}; SONGS.push(s); BY_NORM.set(n, s); }
  s.v.push([info.key || '', path]);
  const season = info.season || Object.entries(CURATED).find(([k]) => n.startsWith(k))?.[1] || '';
  if (season && !s.s) s.s = season;
  const pk = parseKey(info.key);
  if (pk && !s.keys.includes(info.key)) { const kn = keyName(pk); s.keys.push(info.key); s.kn.push(kn); KEY_COUNT[kn] = (KEY_COUNT[kn] || 0) + 1; }
  KNOWN.set(path, s); PH.set(path, fnv(path));
  return true;
}
function rebuildSongs() {
  SONGS.length = 0; BY_NORM.clear(); KNOWN.clear(); PH.clear();
  for (const k in KEY_COUNT) delete KEY_COUNT[k];
  for (const [path, v] of Object.entries(EXTRA)) if (Array.isArray(v)) addSongFile(path, {title: String(v[0] || ''), key: String(v[1] || ''), season: String(v[2] || '')});
}
const saveSongs = () => dbPut('docs', 'songs', EXTRA).catch(() => toast('곡 목록을 저장하지 못했어요'));
const uploadedCount = () => INDEX.size;
const mb = b => (b / 1048576).toFixed(b < 10485760 ? 1 : 0) + 'MB';
const swOn = () => !!(navigator.serviceWorker && navigator.serviceWorker.controller);
// 그림 주소: 방금 고른 파일 → 서비스워커(score/해시) → 서비스워커가 없으면 직접 읽기
function srcFor(path) {
  const f = LOCAL.get(path);
  if (f) { let u = LURL.get(f); if (!u) { u = URL.createObjectURL(f); LURL.set(f, u); } return u; }
  const hh = PH.get(path) || fnv(path);
  if (!INDEX.has(hh)) return null;
  if (swOn()) return `score/${hh}?v=${VER.get(hh) || 0}`;
  if (BLOBURL.has(hh)) return BLOBURL.get(hh);
  if (!LOADING.has(hh)) {
    LOADING.add(hh);
    dbGet('files', hh).then(v => { if (v && v.blob) BLOBURL.set(hh, URL.createObjectURL(v.blob)); }).catch(() => {})
      .finally(() => { LOADING.delete(hh); if (PV) renderPreview(); });
  }
  return null;
}
async function ensureSrc(path) {
  const s0 = srcFor(path); if (s0) return s0;
  const hh = PH.get(path) || fnv(path);
  if (!INDEX.has(hh)) return null;
  const v = await dbGet('files', hh).catch(() => null);
  if (!v || !v.blob) return null;
  const u = URL.createObjectURL(v.blob); BLOBURL.set(hh, u); return u;
}
async function putBlob(path, blob, type) {
  const hh = PH.get(path) || fnv(path);
  await dbPut('files', hh, {blob, type: type || blob.type || 'image/jpeg', path});
  INDEX.set(hh, true); VER.set(hh, (VER.get(hh) || 0) + 1);
  if (BLOBURL.has(hh)) { URL.revokeObjectURL(BLOBURL.get(hh)); BLOBURL.delete(hh); }
}
async function removeScore(path) {
  const hh = PH.get(path) || fnv(path);
  LOCAL.delete(path);
  await dbDel('files', hh);
  INDEX.delete(hh);
  delete EXTRA[path];
  await saveSongs();
  rebuildSongs(); relinkState(); commit();
}
function renderScoreStatus() {
  const b = $('#scoreBtn');
  b.textContent = upRun ? `악보 저장 중 ${upRun.done}/${upRun.total}` : (SONGS.length ? `악보 ${uploadedCount().toLocaleString()}장` : '악보 불러오기');
}
function openScoreDialog() {
  const d = $('#sm');
  if (!d.open) { if (d.showModal) d.showModal(); else d.setAttribute('open', ''); }
  renderScoreDialog(); estimateStorage();
}
function estimateStorage() {
  try { navigator.storage.estimate().then(e => { USAGE = e; renderScoreDialog(); }); } catch (e) {}
}
const canFolder = () => 'webkitdirectory' in document.createElement('input') && !/iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
function renderScoreDialog() {
  if (!$('#sm').open) return;
  const kids = [
    h('div', {class: 'stat'}, h('b', {text: `${uploadedCount().toLocaleString()}장 · ${SONGS.length.toLocaleString()}곡`}), h('span', {text: '이 기기에 저장된 악보와 곡이에요. 어디에도 올라가지 않아요.'})),
    h('div', {class: 'row-btns'},
      canFolder() ? h('button', {class: 'btn primary', type: 'button', disabled: !!upRun, onclick: () => $('#folderIn').click()}, '악보 폴더 불러오기') : null,
      h('button', {class: canFolder() ? 'btn' : 'btn primary', type: 'button', disabled: !!upRun, onclick: () => $('#filesIn').click()}, '악보 파일·사진 고르기')),
    h('p', {class: 'hint', text: '파일 이름을 "곡명 키.jpg"로 해 두면(예: 시선 D.png, 은혜 Em(G).jpg) 곡명과 키가 자동으로 들어가요. (성탄) (부활)처럼 괄호로 절기도 표시할 수 있어요. 같은 곡의 다른 키 악보는 한 곡으로 묶여요. 이미 있는 악보는 건너뛰어요.'})
  ];
  if (upRun) {
    const pct = upRun.total ? Math.round(upRun.done / upRun.total * 100) : 0;
    kids.push(h('div', {class: 'bar', role: 'progressbar', 'aria-valuenow': pct, 'aria-valuemin': 0, 'aria-valuemax': 100}, h('i', {style: `width:${pct}%`})),
      h('div', {class: 'row-btns'}, h('span', {class: 'hint', text: `${upRun.done.toLocaleString()} / ${upRun.total.toLocaleString()}장 저장 중`}),
        h('button', {class: 'btn sm', type: 'button', disabled: upRun.stop, onclick: () => { upRun.stop = true; renderScoreDialog(); }}, upRun.stop ? '멈추는 중…' : '멈추기')));
  }
  if (upMsg) kids.push(h('p', {class: 'hint' + (upErr ? ' err' : ''), text: upMsg}));
  kids.push(h('details', {class: 'builder'},
    h('summary', {text: '곡 직접 추가 (사진 이름이 IMG_1234처럼 되어 있을 때)'}),
    h('div', {class: 'builder-body'},
      h('input', {class: 'field', id: 'mTitle', placeholder: '곡 제목', 'aria-label': '곡 제목', style: 'flex:1 1 200px;min-width:0'}),
      h('select', {id: 'mKey', 'aria-label': '키'}, h('option', {value: '', text: '키'}), [...MAJ, ...MIN].map(k => h('option', {value: k, text: k}))),
      h('button', {class: 'btn sm primary', type: 'button', onclick: () => { if (!$('#mTitle').value.trim()) { toast('곡 제목을 먼저 적어 주세요'); $('#mTitle').focus(); return; } $('#addIn').click(); }}, '악보 고르고 추가'))));
  if (USAGE && USAGE.quota) kids.push(h('p', {class: 'hint', text: `저장 공간 ${mb(USAGE.usage || 0)} 사용 중 · 이 기기에서 ${mb(USAGE.quota)}까지 쓸 수 있어요`}));
  kids.push(SMC
    ? h('div', {class: 'confirm', role: 'alert'}, h('span', {text: '저장된 악보와 곡 목록을 모두 지울까요? 콘티 기록은 남아요. 되돌릴 수 없어요.'}),
        h('button', {class: 'btn sm danger', type: 'button', onclick: clearAllScores}, '모두 지우기'),
        h('button', {class: 'btn sm', type: 'button', onclick: () => { SMC = false; renderScoreDialog(); }}, '취소'))
    : (SONGS.length ? h('div', {class: 'row-btns'}, h('button', {class: 'btn sm danger', type: 'button', onclick: () => { SMC = true; renderScoreDialog(); }}, '악보와 곡 목록 모두 지우기')) : null));
  fill($('#smBody'), ...kids);
}
async function clearAllScores() {
  try { await dbClear('files'); } catch (e) {}
  EXTRA = {}; await saveSongs();
  INDEX.clear(); LOCAL.clear(); rebuildSongs(); relinkState(); SMC = false;
  commit(); renderScoreStatus(); renderScoreDialog(); estimateStorage();
  toast('악보와 곡 목록을 지웠어요');
}
const TYPES = {jpg: 'image/jpeg', jpeg: 'image/jpeg', jfif: 'image/jpeg', png: 'image/png', gif: 'image/gif', webp: 'image/webp'};
async function prepare(file, name) {
  const type = TYPES[(name.split('.').pop() || '').toLowerCase()];
  if (type && file.size <= 3 * 1048576) return {blob: file, type};
  // bmp나 3MB 넘는 그림은 폭 2400px 이하 JPEG로 다시 저장
  const bmp = await createImageBitmap(file);
  const sc = Math.min(1, 2400 / bmp.width), cv = document.createElement('canvas');
  cv.width = Math.round(bmp.width * sc); cv.height = Math.round(bmp.height * sc);
  const g = cv.getContext('2d'); g.fillStyle = '#ffffff'; g.fillRect(0, 0, cv.width, cv.height); g.drawImage(bmp, 0, 0, cv.width, cv.height);
  const blob = await new Promise(r => cv.toBlob(r, 'image/jpeg', 0.85));
  return {blob, type: 'image/jpeg'};
}
const SKIP_NAME = /^(thumbs\.db|desktop\.ini|\.ds_store|icon\r?)$/i;
// 폴더나 여러 파일을 불러와 곡 목록에 넣고 악보를 이 기기에 저장한다
async function importFiles(files, fromFolder) {
  if (upRun) return;
  const list = [];
  for (const f of files) {
    const rel = (f.webkitRelativePath || f.name).normalize('NFC'), segs = rel.split('/'), name = segs[segs.length - 1];
    if (!IMG_EXT.test(name) || SKIP_NAME.test(name)) continue;
    list.push([fromFolder && segs.length > 1 ? segs.slice(1).join('/') : name, f]);
  }
  if (!list.length) { toast('불러올 악보 그림이 없어요. jpg·png 파일을 골라 주세요'); return; }
  upRun = {stop: false, done: 0, total: list.length, added: 0, skipped: 0, failed: 0};
  upMsg = ''; upErr = false;
  openScoreDialog();
  let lock = null;
  try { lock = await navigator.wakeLock?.request('screen'); } catch (e) {}
  for (const [path, f] of list) {
    if (upRun.stop) break;
    try {
      if (!KNOWN.has(path)) {
        const info = parseName(path.split('/').pop());
        if (!info.title) { upRun.failed++; upRun.done++; continue; }
        EXTRA[path] = [info.title, info.key, info.season];
        addSongFile(path, info); upRun.added++;
      }
      if (INDEX.has(PH.get(path) || fnv(path))) upRun.skipped++;
      else { const {blob, type} = await prepare(f, path); await putBlob(path, blob, type); }
      LOCAL.set(path, f);
    } catch (e) {
      upRun.failed++;
      if (e && e.name === 'QuotaExceededError') { upRun.stop = true; upMsg = '기기 저장 공간이 모자라요. 여기까지 저장했어요.'; upErr = true; }
    }
    upRun.done++;
    if (upRun.done % 25 === 0) { await saveSongs(); renderScoreStatus(); renderScoreDialog(); }
  }
  await saveSongs();
  try { await lock?.release(); } catch (e) {}
  const run = upRun; upRun = null;
  if (!upErr) upMsg = (run.stop ? '멈췄어요. ' : '') + `${run.done.toLocaleString()}장을 읽어 새 악보 ${run.added.toLocaleString()}장을 곡 목록에 넣었어요.`
    + (run.skipped ? ` 이미 있던 ${run.skipped.toLocaleString()}장은 건너뛰었어요.` : '') + (run.failed ? ` ${run.failed}장은 읽지 못했어요.` : '');
  relinkState(); commit(); renderScoreStatus(); renderScoreDialog(); estimateStorage();
  if (PV) renderPreview();
  if ($('#ex').open) openExport();
}
async function addManual(files) {
  const title = $('#mTitle') ? $('#mTitle').value.trim() : '', key = $('#mKey') ? $('#mKey').value : '';
  if (!title || !files.length) return;
  let i = 0;
  for (const f of files) {
    if (!/^image\//.test(f.type) && !IMG_EXT.test(f.name)) continue;
    const path = `직접 추가/${Date.now()}-${i++}-${f.name}`;
    EXTRA[path] = [title, key, ''];
    addSongFile(path, {title, key, season: ''});
    try { const {blob, type} = await prepare(f, f.name); await putBlob(path, blob, type); LOCAL.set(path, f); } catch (e) {}
  }
  await saveSongs();
  relinkState(); commit(); renderScoreStatus(); renderScoreDialog();
  toast(`${title} 악보 ${i}장을 넣었어요`);
}
// 곡 이름·키 고치기: 이 곡의 모든 악보 이름을 바꾸고, 지금 보는 키 악보의 키를 바꾼다
function editSong(song, key, newTitle, newKey) {
  const t = newTitle.trim(); if (!t) { toast('곡 제목을 적어 주세요'); return; }
  for (const v of song.v) { const cur = EXTRA[v[1]]; if (cur) EXTRA[v[1]] = [t, (v[0] || '') === key ? newKey : cur[1], cur[2] || '']; }
  saveSongs(); rebuildSongs(); relinkState(); commit();
  const ns = BY_NORM.get(norm(t));
  if (ns && PV) { PV.song = ns; PV.key = groupVariants(ns).has(newKey) ? newKey : [...groupVariants(ns).keys()][0]; PV.edit = false; renderPreview(); }
  toast('곡 정보를 고쳤어요');
}

'''
rep_between("/* ---------- 악보: 이 기기 폴더(LOCAL) 또는 앱에 올린 파일(INDEX) ---------- */", "function groupVariants(song) {", SCORES)

# 미리보기
rep("""async function rotate(path, d) {
  const deg = ((PV.rot[path] || 0) + d + 360) % 360;
  const src = srcFor(path);""", """async function rotate(path, d) {
  const deg = ((PV.rot[path] || 0) + d + 360) % 360;
  const src = await ensureSrc(path);""")
rep("""    if (ASSETS && DB) { await putAsset(path, blob, imgType(path)); await flushIndex(); }
    if (LOCAL.has(path)) LOCAL.set(path, new File([blob], path.split('/').pop(), {type: imgType(path)}));
    clearRot(path); toast(ASSETS && DB ? '돌린 악보를 저장했어요' : '이 기기에서만 돌려 두었어요');
  } catch (e) { toast(UPERR[e && e.code] || '저장하지 못했어요. 다시 눌러 주세요'); }""",
"""    await putBlob(path, blob, imgType(path));
    if (LOCAL.has(path)) LOCAL.set(path, new File([blob], path.split('/').pop(), {type: imgType(path)}));
    clearRot(path); toast('돌린 악보를 저장했어요');
  } catch (e) { toast('저장하지 못했어요. 다시 눌러 주세요'); }""")
rep("""async function doRemove(path) {
  PV.busy = path; renderPreview();
  try { clearRot(path); await removeScore(path); toast('악보를 지웠어요'); }
  catch (e) { toast('지우지 못했어요. 다시 눌러 주세요'); }
  PV.busy = null; PV.confirm = null; renderPreview(); renderScoreStatus();
}""", """async function doRemove(path) {
  PV.busy = path; renderPreview();
  try { clearRot(path); await removeScore(path); toast('악보를 지웠어요'); }
  catch (e) { toast('지우지 못했어요. 다시 눌러 주세요'); }
  PV.busy = null; PV.confirm = null; renderScoreStatus();
  const ns = BY_NORM.get(PV.song.n);
  if (!ns) { $('#pv').close(); return; }
  PV.song = ns;
  if (!groupVariants(ns).has(PV.key)) PV.key = [...groupVariants(ns).keys()][0];
  renderPreview();
}""")
rep("  const writer = !!(ASSETS && DB);", "  const writer = true;")
rep("h('span', {class: 'src', text: x.up ? '앱에 올라간 악보' : '이 기기 폴더에서 보는 중'}),", "h('span', {class: 'src', text: x.up ? '이 기기에 저장된 악보' : '방금 고른 파일'}),")
rep("h('span', {text: x.up ? '이 악보를 앱에서 지울까요? 맥에 있는 원본 파일은 그대로 남아요.' : '이 기기 연결에서 이 악보를 뺄까요? 원본 파일은 그대로 남아요.'}),",
    "h('span', {text: '이 악보를 콘티노트에서 지울까요? 원본 파일은 그대로 남아요.'}),")
rep("""    h('p', {text: '이 곡 악보가 아직 앱에 없어요.'}),
    h('p', {class: 'hint', text: '위의 "악보" 버튼에서 "찬양 목록" 폴더를 연결하거나 앱에 올려 두면 바로 보여요. 지금 이 곡만 보려면 파일을 골라 주세요.'}),""",
    """    h('p', {text: '이 곡 악보가 아직 없어요.'}),
    h('p', {class: 'hint', text: '악보 파일을 고르면 이 곡에 저장돼요.'}),""")
rep("else if (shown.length < items.length) body.append(h('p', {class: 'hint', text: `${items.length - shown.length}장은 아직 앱에 없어요.`}));",
    "else if (shown.length < items.length) body.append(h('p', {class: 'hint', text: `${items.length - shown.length}장은 아직 저장되지 않았어요.`}));\n"
    "  if (PV.edit) body.prepend(h('form', {class: 'edit-form', onsubmit: e => { e.preventDefault(); editSong(song, PV.key, $('#eTitle').value, $('#eKey').value); }},\n"
    "    h('input', {class: 'field', id: 'eTitle', value: song.t, 'aria-label': '곡 제목'}),\n"
    "    h('select', {id: 'eKey', 'aria-label': '이 악보의 키'}, h('option', {value: '', text: '키 없음'}), [...MAJ, ...MIN].map(k => h('option', {value: k, selected: k === PV.key, text: k}))),\n"
    "    h('button', {class: 'btn sm primary', type: 'submit'}, '저장'),\n"
    "    h('button', {class: 'btn sm', type: 'button', onclick: () => { PV.edit = false; renderPreview(); }}, '취소')));")
rep("""      has ? '콘티에 들어감' : (to && to !== k ? `콘티에 넣기 · ${k}→${to}` : '콘티에 넣기')));
  renderPad();""", """      has ? '콘티에 들어감' : (to && to !== k ? `콘티에 넣기 · ${k}→${to}` : '콘티에 넣기')),
    h('button', {class: 'btn', type: 'button', onclick: () => { PV.edit = !PV.edit; renderPreview(); }}, '곡 이름·키 고치기'));
  renderPad();""")
rep_between("async function pickOne(e, path) {", "/* ---------- 마디 진행:", r'''async function pickOne(e, path) {
  const f = e.target.files && e.target.files[0];
  if (!f || !path) return;
  LOCAL.set(path, f);
  renderPreview(); renderScoreStatus();
  try { const {blob, type} = await prepare(f, f.name || path); await putBlob(path, blob, type); toast('이 악보를 저장했어요'); }
  catch (err) { toast('저장하지 못했어요. 이번에만 보여요'); }
  renderPreview(); renderScoreStatus();
  if ($('#ex').open) openExport();
}

''')

# ---------------------------------------------------------------- 기록: 이 기기에 저장
rep("  if (!DB) { if (!silent) toast('기록 저장은 claude.ai에서 이 앱을 열었을 때만 돼요'); return false; }\n", '')
rep("    await DB.doc('contis/' + histId()).set(doc);", "    await dbPut('contis', histId(), doc);\n    HIST = HIST.filter(x => x.id !== histId()).concat([{id: histId(), ...doc}]).sort(histSort);\n    rebuildUsage(); onHist();")
rep("try { await DB.doc('contis/' + c.id).delete(); toast('기록을 지웠어요'); }",
    "try { await dbDel('contis', c.id); HIST = HIST.filter(x => x.id !== c.id); rebuildUsage(); onHist(); toast('기록을 지웠어요'); }")
rep("  if (!DB) { fill(body, h('p', {class: 'hint', text: '콘티 기록은 claude.ai에서 이 앱을 열었을 때 쓸 수 있어요.'})); return; }\n", '')
rep("toast(e && e.code === 'quota_exceeded' ? '기록 저장 공간이 다 찼어요. 오래된 기록을 지워 주세요' : '기록에 저장하지 못했어요. 다시 눌러 주세요');",
    "toast('기록에 저장하지 못했어요. 다시 눌러 주세요');")

# ---------------------------------------------------------------- 파일 저장: 위치 고르기 / 폰은 공유
rep("""const getDownloads = async () => {
  if (DL !== undefined) return DL;
  try { DL = window.claude && window.claude.use ? await window.claude.use('downloads') : null; } catch (e) { DL = null; }
  return DL;
};""", r'''const MIME = {png: 'image/png', pdf: 'application/pdf', jpg: 'image/jpeg', json: 'application/json'};
const isTouch = () => matchMedia('(pointer: coarse)').matches;
// 폰: 공유 창(카카오톡·파일에 저장) / 크롬·엣지: 저장 위치 고르기 / 그 밖: 다운로드 폴더
async function saveFiles(list) {
  const files = list.map(({filename, data}) => { const ext = filename.split('.').pop().toLowerCase(); return new File([data], filename, {type: MIME[ext] || 'application/octet-stream'}); });
  try {
    if (isTouch() && navigator.canShare && navigator.canShare({files})) { await navigator.share({files}); return {status: 'saved'}; }
    if (files.length === 1 && window.showSaveFilePicker) {
      const f = files[0], ext = f.name.split('.').pop().toLowerCase();
      const hnd = await window.showSaveFilePicker({suggestedName: f.name, types: [{description: ext.toUpperCase(), accept: {[f.type]: ['.' + ext]}}]});
      const w = await hnd.createWritable(); await w.write(f); await w.close();
      return {status: 'saved'};
    }
  } catch (e) {
    if (e && e.name === 'AbortError') throw {code: 'declined'};
  }
  for (const f of files) {
    const url = URL.createObjectURL(f), a = document.createElement('a');
    a.href = url; a.download = f.name; document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  }
  return {status: 'saved'};
}
const getDownloads = async () => { DL = DL || {save: req0 => saveFiles([req0])}; return DL; };''')
rep("async function saveAllPng() { for (let i = 0; i < EX.blobs.length; i++) if (!(await savePng(i))) return; EX.msg = `이미지 ${EX.blobs.length}장을 모두 저장했어요.`; renderExport(); }",
    """async function saveAllPng() {
  try { await saveFiles(EX.blobs.map((b, i) => ({filename: `${exName()} ${pad(i + 1)}.png`, data: b}))); EX.msg = `이미지 ${EX.blobs.length}장을 저장했어요.`; recordAfterExport(); }
  catch (e) { EX.msg = dlMsg(e); }
  renderExport();
}""")
rep("      const src = path ? srcFor(path) : null;", "      const src = path ? await ensureSrc(path) : null;")
rep("""      h('span', {text: `악보 ${missing}곡이 아직 앱에 없어요. 지금 앱에 올라간 악보는 ${uploadedCount().toLocaleString()} / ${KNOWN.size.toLocaleString()}장이에요. 맥에서 "찬양 목록" 폴더를 연결하면 바로 채워지고, 이어서 "앱에 올리기"를 끝까지 하면 폰에서도 다 들어가요.`}),
      h('button', {class: 'btn sm', type: 'button', onclick: () => $('#folderIn').click()}, '"찬양 목록" 폴더 연결'),
      h('button', {class: 'btn sm', type: 'button', onclick: () => { $('#scoreBtn').click(); }}, '악보 올리기 창 열기')) : null,""",
    """      h('span', {text: `악보 ${missing}곡이 아직 없어요. 곡마다 파일을 고르거나 악보를 불러오세요.`}),
      h('button', {class: 'btn sm', type: 'button', onclick: openScoreDialog}, '악보 불러오기')) : null,""")
rep("h('span', {class: 'warn', text: '악보가 아직 앱에 없어요'}),", "h('span', {class: 'warn', text: '악보가 아직 없어요'}),")
rep("""    h('p', {class: 'hint', text: '저장할 폴더는 앱이 직접 고를 수 없고, 저장 확인 뒤 브라우저나 폰이 정해요. 맥에서 저장할 때마다 폴더를 고르려면 크롬은 설정 → 다운로드 → "다운로드 전에 각 파일의 저장 위치 확인"을, 사파리는 설정 → 일반 → 파일 다운로드 위치 → "각 다운로드마다 묻기"를 켜 두세요. 아이폰은 저장을 누르면 뜨는 공유 창에서 "파일에 저장"을 고르면 폴더를 고를 수 있고, 카카오톡으로 바로 보낼 수도 있어요.'}),""",
    """    h('p', {class: 'hint', text: '컴퓨터의 크롬·엣지에서는 저장할 때 폴더를 고를 수 있어요. 다른 브라우저는 다운로드 폴더에 저장돼요. 폰에서는 공유 창이 떠서 카카오톡으로 바로 보내거나 "파일에 저장"을 고를 수 있어요.'}),""")

# ---------------------------------------------------------------- 이벤트
rep("""  renderScoreDialog();
  if (ASSETS) ASSETS.list().then(r => { USAGE = r.usage; renderScoreDialog(); }).catch(() => {});
});
$('#folderIn').addEventListener('change', e => { const files = [...(e.target.files || [])]; e.target.value = ''; connectFolder(files); });""",
    """  renderScoreDialog(); estimateStorage();
});
$('#folderIn').addEventListener('change', e => { const files = [...(e.target.files || [])]; e.target.value = ''; importFiles(files, true); });
$('#filesIn').addEventListener('change', e => { const files = [...(e.target.files || [])]; e.target.value = ''; importFiles(files, false); });
$('#addIn').addEventListener('change', e => { const files = [...(e.target.files || [])]; e.target.value = ''; addManual(files); });""")

SETTINGS = r'''
/* ---------- 설정: 예배 종류, 백업, 설치 ---------- */
function renderSettings() {
  if (!$('#setDlg').open) return;
  const ids = Object.keys(SVC);
  const rows = ids.map(id => {
    const v = SVC[id];
    return h('div', {class: 'svc-row'},
      h('input', {class: 'field', value: v.name, 'aria-label': '예배 이름', oninput: e => { v.name = e.target.value; v.label = e.target.value; if (state.svc === id) state.label = v.label; saveSvc(); renderTop(); renderSheet(); }}),
      h('select', {'aria-label': v.name + ' 곡 수', onchange: e => { v.count = Number(e.target.value); saveSvc(); if (state.svc === id) setService(id); else renderTop(); }},
        [2, 3, 4, 5, 6, 7, 8, 9, 10].map(n => h('option', {value: n, selected: n === v.count, text: n + '곡'}))),
      h('select', {'aria-label': v.name + ' 요일', onchange: e => { v.dow = Number(e.target.value); saveSvc(); if (state.svc === id) state.date = nextDate(id); commit(); }},
        [...WD].map((w, i) => h('option', {value: i, selected: i === v.dow, text: w + '요일'}))),
      h('label', {class: 'tapadd'}, h('input', {type: 'checkbox', checked: !!v.skipEdge, onchange: e => { v.skipEdge = e.target.checked; saveSvc(); if (state.svc === id) state.date = nextDate(id); commit(); }}), '첫째·마지막 주 빼기'),
      h('button', {class: 'icon', type: 'button', 'aria-label': v.name + ' 지우기', disabled: ids.length <= 1, onclick: () => { delete SVC[id]; saveSvc(); if (state.svc === id) setService(firstSvc()); else commit(); renderSettings(); }}, '✕'));
  });
  const ios = /iPhone|iPad|iPod/i.test(navigator.userAgent);
  fill($('#setBody'),
    h('div', {class: 'group-h'}, h('span', {text: '예배'}), h('span', {text: '위쪽 버튼에 이 순서로 보여요'})),
    h('div', {class: 'svc-list'}, rows),
    h('div', {class: 'row-btns'},
      h('button', {class: 'btn sm', type: 'button', onclick: () => { const id = 's' + Date.now().toString(36); SVC[id] = {name: '새 예배', count: 4, dow: 0, label: '새 예배', skipEdge: false}; saveSvc(); renderTop(); renderSettings(); }}, '+ 예배 추가'),
      h('button', {class: 'btn sm', type: 'button', onclick: () => { SVC = JSON.parse(JSON.stringify(DEFAULT_SVC)); saveSvc(); if (!SVC[state.svc]) setService(firstSvc()); else commit(); renderSettings(); }}, '기본으로')),
    h('div', {class: 'group-h', style: 'margin-top:14px'}, h('span', {text: '백업'}), h('span', {text: '곡 목록 · 기록 · 설정'})),
    h('p', {class: 'hint', text: '콘티노트의 자료는 모두 이 기기 안에만 저장돼요. 기기를 바꾸거나 브라우저 기록을 지우기 전에 백업 파일을 만들어 두세요. 악보 그림은 백업에 들어가지 않으니, 새 기기에서는 악보를 다시 불러오세요.'}),
    h('div', {class: 'row-btns'},
      h('button', {class: 'btn', type: 'button', onclick: makeBackup}, '백업 파일 만들기'),
      h('button', {class: 'btn', type: 'button', onclick: () => $('#restoreIn').click()}, '백업 불러오기')),
    h('div', {class: 'group-h', style: 'margin-top:14px'}, h('span', {text: '앱으로 설치'})),
    (() => { const x = installHelp(); if (!x) return h('p', {class: 'hint', text: ios ? '사파리 공유 버튼 → "홈 화면에 추가"를 누르면 앱처럼 쓸 수 있어요.' : '크롬·엣지 주소창 오른쪽의 설치 아이콘이나 메뉴의 "앱 설치"를 누르면 앱처럼 쓸 수 있어요. 폰에서는 아래 QR 코드를 찍어 여세요.'});
      const box = h('div', {class: 'install-bar', style: 'margin:0'}); fill(box, ...helpNode(x, false)); return box; })(),
    h('div', {class: 'group-h', style: 'margin-top:14px'}, h('span', {text: '함께 쓰기'}), h('span', {text: '폰으로 열기 · 다른 분께 알리기'})),
    (() => { const cv = h('canvas', {width: 320, height: 320, 'aria-label': '콘티노트 주소 QR 코드'}); drawQR(cv);
      return h('div', {class: 'share-box'}, cv, h('div', {style: 'display:flex;flex-direction:column;gap:8px;min-width:0;flex:1 1 200px'},
        h('p', {class: 'hint', text: '폰 카메라로 QR 코드를 찍으면 바로 열려요.'}),
        h('div', {class: 'share-url', text: APP_URL}),
        h('div', {class: 'row-btns'}, h('button', {class: 'btn primary', type: 'button', onclick: shareApp}, navigator.share ? '공유하기' : '주소 복사')))); })(),
    h('div', {class: 'group-h', style: 'margin-top:14px'}, h('span', {text: '콘티노트'}), h('span', {text: '무료'})),
    h('p', {class: 'hint', text: '찬양 인도자를 위한 무료 콘티 도구예요. 악보와 자료는 서버로 보내지 않아요. 악보의 저작권은 각 저작권자에게 있으니 교회 안에서 바르게 사용해 주세요.'}));
}
async function makeBackup() {
  const data = {app: 'continote', version: 1, savedAt: new Date().toISOString(), songs: EXTRA, contis: HIST, services: SVC, seasonOv: state.seasonOv, seq: state.seq};
  try { await saveFiles([{filename: `콘티노트 백업 ${ymd(new Date())}.json`, data: JSON.stringify(data)}]); toast('백업 파일을 만들었어요'); }
  catch (e) { if (!e || e.code !== 'declined') toast('백업 파일을 저장하지 못했어요'); }
}
async function restoreBackup(file) {
  try {
    const data = JSON.parse(await file.text());
    if (!data || data.app !== 'continote') { toast('콘티노트 백업 파일이 아니에요'); return; }
    if (data.songs && typeof data.songs === 'object') {
      for (const [p, v] of Object.entries(data.songs)) if (Array.isArray(v) && !EXTRA[p]) EXTRA[p] = v.slice(0, 3).map(x => String(x || ''));
      await saveSongs(); rebuildSongs();
    }
    if (Array.isArray(data.contis)) for (const c of data.contis) if (c && c.id && c.date) { const {id, ...rest} = c; await dbPut('contis', String(id), rest); }
    HIST = (await dbAll('contis')).map(([id, v]) => ({id, ...v})).sort(histSort);
    if (data.services && typeof data.services === 'object' && Object.keys(data.services).length) { SVC = data.services; saveSvc(); if (!SVC[state.svc]) state.svc = firstSvc(); }
    if (data.seasonOv && typeof data.seasonOv === 'object') state.seasonOv = {...state.seasonOv, ...data.seasonOv};
    rebuildUsage(); relinkState(); commit(); renderHistBtn(); renderSettings(); renderScoreStatus();
    toast('백업을 불러왔어요. 악보 그림은 다시 불러와 주세요');
  } catch (e) { toast('백업 파일을 읽지 못했어요'); }
}
$('#setBtn').addEventListener('click', () => { const d = $('#setDlg'); if (!d.open) { if (d.showModal) d.showModal(); else d.setAttribute('open', ''); } renderSettings(); });
$('#setDlg').addEventListener('click', e => { const d = $('#setDlg'); if (e.target === d || e.target.closest('[data-close]')) d.close(); });
$('#restoreIn').addEventListener('change', e => { const f = e.target.files && e.target.files[0]; e.target.value = ''; if (f) restoreBackup(f); });
/* ---------- 설치 안내: 기기·브라우저마다 가장 쉬운 방법 ---------- */
const APP_URL = 'https://seraph0153.github.io/continote/';
const UA = navigator.userAgent;
const DEV = {
  ios: /iPhone|iPad|iPod/.test(UA) || (!/Android/.test(UA) && navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1),
  android: /Android/.test(UA),
  kakao: /KAKAOTALK/i.test(UA),
  inApp: /KAKAOTALK|NAVER\(inapp|Instagram|FBAN|FBAV|Line\/|DaumApps|BAND\//i.test(UA),
  standalone: matchMedia('(display-mode: standalone)').matches || navigator.standalone === true
};
DEV.iosSafari = DEV.ios && /Safari/.test(UA) && !/CriOS|FxiOS|EdgiOS/.test(UA) && !DEV.inApp;
const SHARE_SVG = '<svg class="share-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/><path d="M8 7l4-4 4 4"/><path d="M5 11v8a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-8"/></svg>';
let installEvt = null;
function installHelp() {
  if (DEV.standalone) return {title: '설치되어 있어요', text: '홈 화면의 콘티노트 아이콘으로 열고 있어요.'};
  if (DEV.kakao) return {title: '카카오톡 안에서는 설치가 안 돼요', text: '아래 버튼으로 기본 브라우저에서 연 뒤 설치하세요.',
    link: {href: 'kakaotalk://web/openExternal?url=' + encodeURIComponent(APP_URL), label: '기본 브라우저로 열기'}};
  if (DEV.inApp && DEV.android) return {title: '이 앱 안에서는 설치가 안 돼요', text: '아래 버튼으로 크롬에서 연 뒤 설치하세요.',
    link: {href: 'intent://' + APP_URL.replace(/^https:\/\//, '') + '#Intent;scheme=https;package=com.android.chrome;end', label: '크롬으로 열기'}};
  if (DEV.inApp) return {title: '이 앱 안에서는 설치가 안 돼요', text: '화면 구석의 ··· 메뉴에서 "Safari로 열기"(또는 "다른 브라우저로 열기")를 누른 뒤 설치하세요.'};
  if (installEvt) return {title: '콘티노트를 앱으로 설치하세요', text: '홈 화면에 아이콘이 생기고, 인터넷이 없어도 열려요.', button: '홈 화면에 설치'};
  if (DEV.iosSafari) return {title: '홈 화면에 설치하기', steps: [`아래쪽 공유 버튼 ${SHARE_SVG} 누르기`, '목록을 올려 "홈 화면에 추가" 누르기', '오른쪽 위 "추가" 누르기']};
  if (DEV.ios) return {title: '홈 화면에 설치하기', steps: [`주소창 옆 공유 버튼 ${SHARE_SVG} 누르기`, '"홈 화면에 추가" 누르기 (안 보이면 Safari에서 여세요)']};
  if (DEV.android) return {title: '홈 화면에 설치하기', steps: ['오른쪽 위 ⋮ 메뉴 누르기', '"홈 화면에 추가" 또는 "앱 설치" 누르기']};
  return null;
}
function helpNode(x, inBar) {
  const text = h('div', {class: 'ib-text'}, h('b', {text: x.title}));
  if (x.text) text.append(h('div', {text: x.text}));
  if (x.steps) { const ol = h('ol'); x.steps.forEach(st => { const li = document.createElement('li'); li.innerHTML = st; ol.append(li); }); text.append(ol); }
  const acts = [];
  if (x.link) acts.push(h('a', {class: 'btn', href: x.link.href}, x.link.label));
  if (x.button) acts.push(h('button', {class: 'btn', type: 'button', onclick: doInstall}, x.button));
  if (inBar) acts.push(h('button', {class: 'btn ib-close', type: 'button', onclick: () => { try { localStorage.setItem('continote.installHint', 'off'); } catch (e) {} renderInstallBar(); }}, '닫기'));
  return [text, ...acts];
}
function renderInstallBar() {
  const bar = $('#installBar');
  let off = false; try { off = localStorage.getItem('continote.installHint') === 'off'; } catch (e) {}
  const x = installHelp();
  const mobile = DEV.ios || DEV.android;
  if (!x || DEV.standalone || off || !(mobile || installEvt)) { bar.className = ''; fill(bar); return; }
  bar.className = 'install-bar'; bar.setAttribute('role', 'region'); bar.setAttribute('aria-label', '앱 설치 안내');
  fill(bar, ...helpNode(x, true));
}
async function doInstall() {
  if (!installEvt) return;
  installEvt.prompt();
  try { await installEvt.userChoice; } catch (e) {}
  installEvt = null; $('#installBtn').hidden = true; renderInstallBar(); renderSettings();
}
window.addEventListener('beforeinstallprompt', e => { e.preventDefault(); installEvt = e; $('#installBtn').hidden = false; renderInstallBar(); renderSettings(); });
window.addEventListener('appinstalled', () => { $('#installBtn').hidden = true; installEvt = null; renderInstallBar(); toast('콘티노트를 설치했어요'); });
$('#installBtn').addEventListener('click', doInstall);
renderInstallBar();
// 함께 쓰기: QR 코드와 공유
let qrLib = null;
async function drawQR(canvas) {
  try {
    if (!window.QRious) qrLib = qrLib || new Promise((ok, no) => { const sc = document.createElement('script'); sc.src = 'https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js'; sc.onload = ok; sc.onerror = no; document.head.append(sc); });
    await qrLib;
    new window.QRious({element: canvas, value: APP_URL, size: 320, level: 'M', background: '#ffffff', foreground: '#14182b'});
  } catch (e) { canvas.replaceWith(h('p', {class: 'hint', text: 'QR 코드는 인터넷이 연결되어 있을 때 보여요.'})); }
}
async function shareApp() {
  const data = {title: '콘티노트', text: '기준곡 하나로 시작하는 무료 찬양 콘티 앱', url: APP_URL};
  try { if (navigator.share) { await navigator.share(data); return; } } catch (e) { if (e && e.name === 'AbortError') return; }
  try { await navigator.clipboard.writeText(APP_URL); toast('주소를 복사했어요'); } catch (e) { toast(APP_URL); }
}
if ('serviceWorker' in navigator && location.protocol !== 'file:') {
  navigator.serviceWorker.register('sw.js').catch(() => {});
  navigator.serviceWorker.addEventListener('controllerchange', () => { renderScoreStatus(); if (PV) renderPreview(); });
}
if (location.hostname === 'localhost') window.__ct = {importFiles, SONGS, INDEX, state: () => state};
'''
rep("""$('#trayGo').addEventListener('click',""", SETTINGS.strip('\n') + "\n$('#trayGo').addEventListener('click',")

# ---------------------------------------------------------------- 남은 claude.ai 흔적이 없는지 확인
for bad in [r'window\.claude', r'\bASSETS\b', r'(?<![A-Za-z])DB\.', r'\bSAMPLE\b', r'flushIndex', r'connectFolder', r'\bUPERR\b', r'renderDraft', r'aiBox\(', r'askDraft', r'__SONGS__', r'claude\.ai']:
    assert not re.search(bad, s), bad

out = os.path.join(ROOT, 'docs', 'index.html')
open(out, 'w', encoding='utf-8').write(s)
print(out, len(s) // 1024, 'KB')
