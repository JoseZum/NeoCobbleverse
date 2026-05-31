"""Build a server-side mods bundle by excluding known client-only mods."""
import os
import re
import shutil
import zipfile

INSTANCE = r'C:\Users\jfzum\curseforge\minecraft\Instances\NeoCobbleverse'
MODS_SRC = os.path.join(INSTANCE, 'mods')
CONFIG_SRC = os.path.join(INSTANCE, 'config')
DEFCONF_SRC = os.path.join(INSTANCE, 'defaultconfigs')

OUT_DIR = os.path.join(INSTANCE, 'server-pack')
OUT_ZIP = os.path.join(INSTANCE, 'NeoCobbleverse-server-v1.0.0.zip')

# Client-only mods. Match by lowercase filename prefix (without version).
CLIENT_ONLY_PREFIXES = [
    'advancementplaques',
    'badoptimizations',
    'betterf3',
    'betterf1',
    'betterthirdperson',
    '[neoforge-1.21.1]accurateblockplacement',
    'bridgingmod',
    'continuity',
    'controlling',
    'dynamiccrosshair',
    'eg_particle_interactions',
    'emi-',
    'emojiful',
    'enchdesc',
    'entity_model_features',
    'entity_texture_features',
    'entityculling',
    'extrasounds',
    'fusion-',
    'iceberg',
    'immediatelyfast',
    'invmove',
    'invmovecompats',
    'iris-',
    'lumymon',
    'minecraft-cursor',
    'modernfix',
    'moreculling',
    'mousetweaks',
    'musicnotification',
    'nethermap',
    'notenoughanimations',
    'notenoughcrashes',
    'ok_zoomer',
    'particlerain',
    'particular',
    'pickupnotifier',
    'ping-wheel',
    'presencefootsteps',
    'punchy',
    'reeses-sodium-options',
    'resourcepackoverrides',
    'respackopts',
    'screenshot_viewer',
    'skinlayers3d',
    'sodium-',
    'sodium-extra',
    'sodium-neoforge',
    'sound-physics-remastered',
    'soundsbegone',
    'stackdeobfuscatorfabric',
    'tia-',
    'wakes-',
    'windy-',
    'xaerominimap',
    'xaeroworldmap',
    'yet_another_config_lib',
    'distanthorizons',
    'defaultoptions',
    'cobblemon-battle-positions',
    'zfastnoise',
]
# NOTE: kept as both/lib (safe on server):
#   accessories, trinkets, connector, forgified-fabric-api,
#   fabric-language-kotlin, midnightlib, owo-lib, libjf,
#   particle_core, fzzy_config, sable, globalpacks,
#   immersive_melodies, ping-wheel, emojiful, notenoughcrashes

def is_client_only(filename):
    fn = filename.lower()
    for p in CLIENT_ONLY_PREFIXES:
        if fn.startswith(p):
            return True
    return False

# 1. Clean output dir
if os.path.exists(OUT_DIR):
    shutil.rmtree(OUT_DIR)
os.makedirs(os.path.join(OUT_DIR, 'mods'))

# 2. Copy server-safe jars
all_jars = sorted([f for f in os.listdir(MODS_SRC) if f.endswith('.jar')])
kept = []
skipped = []
for jar in all_jars:
    if is_client_only(jar):
        skipped.append(jar)
    else:
        shutil.copy2(os.path.join(MODS_SRC, jar), os.path.join(OUT_DIR, 'mods', jar))
        kept.append(jar)

# 3. Copy config dir (server reads same configs)
shutil.copytree(CONFIG_SRC, os.path.join(OUT_DIR, 'config'))

# 3a. Strip references to client-only mod items from CobbleDollars configs
import json
CLIENT_ITEM_PREFIXES = ('lumymon:',)
def strip_client_items(obj):
    if isinstance(obj, list):
        return [strip_client_items(x) for x in obj
                if not (isinstance(x, dict) and isinstance(x.get('item'), str)
                        and any(x['item'].startswith(p) for p in CLIENT_ITEM_PREFIXES))]
    if isinstance(obj, dict):
        return {k: strip_client_items(v) for k, v in obj.items()}
    return obj

for cfg in ['cobbledollars/bank.json', 'cobbledollars/default_shop.json']:
    p = os.path.join(OUT_DIR, 'config', cfg)
    if not os.path.exists(p):
        continue
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
    cleaned = strip_client_items(data)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)
    print(f'  cleaned server config: {cfg}')

# 4. Copy defaultconfigs if exists
if os.path.exists(DEFCONF_SRC):
    shutil.copytree(DEFCONF_SRC, os.path.join(OUT_DIR, 'defaultconfigs'))

# 5. Write a README inside the server pack
with open(os.path.join(OUT_DIR, 'README_SERVER.txt'), 'w', encoding='utf-8') as f:
    f.write(f'NeoCobbleverse Server Pack v1.0.0\n')
    f.write(f'==================================\n')
    f.write(f'Minecraft: 1.21.1\n')
    f.write(f'NeoForge:  21.1.233\n')
    f.write(f'Mods kept: {len(kept)}\n')
    f.write(f'Mods stripped (client-only): {len(skipped)}\n\n')
    f.write('Install on a NeoForge 21.1.233 dedicated server:\n')
    f.write('1. Upload mods/, config/ and defaultconfigs/ to the server root\n')
    f.write('2. Restart\n\n')
    f.write('--- Stripped client-only mods ---\n')
    for s in skipped:
        f.write(f'  {s}\n')

# 6. Zip it
with zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for root, _, files in os.walk(OUT_DIR):
        for fn in files:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, OUT_DIR)
            zf.write(full, rel)

size_mb = os.path.getsize(OUT_ZIP) / 1024 / 1024

print(f'Jars kept:    {len(kept)}')
print(f'Jars stripped:{len(skipped)}')
print(f'Server pack:  {OUT_ZIP}')
print(f'Size:         {size_mb:.1f} MB')
print()
print('--- Stripped (client-only) ---')
for s in skipped:
    print(f'  - {s}')
