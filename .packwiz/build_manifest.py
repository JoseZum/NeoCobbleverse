"""Convert CurseForge minecraftinstance.json -> manifest.json for packwiz import."""
import json
import sys
import os

SRC = r'C:\Users\jfzum\curseforge\minecraft\Instances\NeoCobbleverse\minecraftinstance.json'
OUT = r'C:\Users\jfzum\packwiz\NeoCobbleverse\manifest.json'

with open(SRC, 'r', encoding='utf-8') as f:
    d = json.load(f)

mc_version = d.get('gameVersion') or '1.21.1'
loader = d.get('baseModLoader', {}).get('name') or 'neoforge-21.1.233'

addons = d.get('installedAddons', [])
files = []
restricted = []
for a in addons:
    pid = a.get('addonID')
    fobj = a.get('installedFile') or {}
    fid = fobj.get('id')
    if not pid or not fid:
        continue
    allow = a.get('allowModDistribution', True)
    files.append({
        'projectID': pid,
        'fileID': fid,
        'required': True
    })
    if allow is False:
        restricted.append(a.get('name', f'project {pid}'))

manifest = {
    'minecraft': {
        'version': mc_version,
        'modLoaders': [{'id': loader, 'primary': True}]
    },
    'manifestType': 'minecraftModpack',
    'manifestVersion': 1,
    'name': 'NeoCobbleverse',
    'version': '1.0.0',
    'author': 'jfzum',
    'files': files,
    'overrides': 'overrides'
}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)

print(f'Wrote {OUT}')
print(f'MC: {mc_version}  Loader: {loader}')
print(f'Total files: {len(files)}')
if restricted:
    print(f'WARNING - {len(restricted)} mods marked allowModDistribution=false (manual download needed):')
    for n in restricted:
        print(f'  - {n}')
