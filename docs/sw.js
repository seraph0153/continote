// 콘티노트 서비스워커: 앱을 오프라인에서도 열고, 이 기기에 저장한 악보 그림을 score/<해시> 주소로 내준다
const VERSION = 'continote-v1';
const RUNTIME = 'continote-runtime';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icons/icon-180.png', './icons/icon-192.png', './icons/icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== VERSION && k !== RUNTIME).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

function readScore(key) {
  return new Promise((ok, no) => {
    const r = indexedDB.open('continote', 1);
    r.onupgradeneeded = () => { const d = r.result; ['files', 'docs', 'contis'].forEach(n => { if (!d.objectStoreNames.contains(n)) d.createObjectStore(n); }); };
    r.onerror = () => no(r.error);
    r.onsuccess = () => {
      const q = r.result.transaction('files').objectStore('files').get(key);
      q.onsuccess = () => ok(q.result);
      q.onerror = () => no(q.error);
    };
  });
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // 악보 그림: 이 기기의 IndexedDB에서 읽는다(네트워크로 나가지 않음)
  if (url.origin === location.origin && url.pathname.includes('/score/')) {
    const key = url.pathname.split('/score/')[1];
    e.respondWith(readScore(key)
      .then(v => v && v.blob
        ? new Response(v.blob, {headers: {'Content-Type': v.type || v.blob.type || 'image/jpeg', 'Cache-Control': 'no-store'}})
        : new Response('', {status: 404}))
      .catch(() => new Response('', {status: 404})));
    return;
  }
  // 앱 화면: 새 버전을 먼저 받고, 인터넷이 없으면 저장해 둔 화면
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req)
      .then(r => { const copy = r.clone(); caches.open(VERSION).then(c => c.put('./index.html', copy)); return r; })
      .catch(() => caches.match('./index.html')));
    return;
  }
  // 글꼴·PDF 라이브러리·아이콘: 한 번 받으면 저장해 두고 쓴다
  if (url.origin === location.origin || /(^|\.)fonts\.(googleapis|gstatic)\.com$|^cdnjs\.cloudflare\.com$/.test(url.host)) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
      if (r.ok || r.type === 'opaque') { const copy = r.clone(); caches.open(RUNTIME).then(c => c.put(req, copy)); }
      return r;
    })));
  }
});
