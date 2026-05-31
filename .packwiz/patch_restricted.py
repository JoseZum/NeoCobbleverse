"""Patch .pw.toml files of restricted mods to use direct CDN URL instead of CF metadata."""
import json
import os
import re
import glob

INSTANCE = r'C:\Users\jfzum\curseforge\minecraft\Instances\NeoCobbleverse'
SRC = os.path.join(INSTANCE, 'minecraftinstance.json')

with open(SRC, 'r', encoding='utf-8') as f:
    d = json.load(f)

restricted = {}
for a in d.get('installedAddons', []):
    if a.get('allowModDistribution') is False:
        pid = a.get('addonID')
        url = (a.get('installedFile') or {}).get('downloadUrl')
        if pid and url:
            restricted[pid] = {'name': a.get('name'), 'url': url}

print(f'{len(restricted)} restricted addons to patch')

candidates = (
    glob.glob(os.path.join(INSTANCE, 'mods', '*.pw.toml')) +
    glob.glob(os.path.join(INSTANCE, 'resourcepacks', '*.pw.toml')) +
    glob.glob(os.path.join(INSTANCE, '*.pw.toml'))
)

patched = 0
for path in candidates:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    m = re.search(r'project-id\s*=\s*(\d+)', text)
    if not m:
        continue
    pid = int(m.group(1))
    if pid not in restricted:
        continue
    info = restricted[pid]

    new_text = re.sub(
        r'(\[download\][^\[]*?)mode\s*=\s*"metadata:curseforge"\s*\n',
        lambda m: m.group(1) + f'url = "{info["url"]}"\n',
        text,
        count=1,
        flags=re.DOTALL
    )

    if new_text == text:
        print(f'  SKIP (already patched or no metadata mode): {os.path.basename(path)}')
        continue

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print(f'  patched: {os.path.basename(path)}  -> {info["name"]}')
    patched += 1

print(f'\nPatched {patched}/{len(restricted)} files')
