"""claude.ai 아티팩트판: src/conti.src.html + private/songs.json → private/app/conti.html (개인용, 배포하지 않음)"""
import os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(root, 'src', 'conti.src.html'), encoding='utf-8').read()
songs = open(os.path.join(root, 'private', 'songs.json'), encoding='utf-8').read().replace('</', '<\\/')
os.makedirs(os.path.join(root, 'private', 'app'), exist_ok=True)
out = os.path.join(root, 'private', 'app', 'conti.html')
open(out, 'w', encoding='utf-8').write(src.replace('__SONGS__', songs))
print(out, os.path.getsize(out) // 1024, 'KB')
