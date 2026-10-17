#!/usr/bin/env bash
# Fetches Fabric Loader's version JSON, Fabric API and Meteor Client for Minecraft 1.20.1 and writes the
# assets the launcher copies into the game directory on first start.
#   usage: build-mods.sh <assets-dir>
set -euo pipefail
A="$(mkdir -p "$1" && cd "$1" && pwd)"
GAME=1.20.1
LOADER=0.15.11
METEOR_VERSION=0.5.4
METEOR_SHA256=90d558f4d32bf96cc5464b869bc69c0f677a1be62e94cb897acf117c0bf82b97
METEOR_URLS=(
  "https://raw.githubusercontent.com/ManInMyVan/meteor-archive/main/files/meteor-client/meteor-client-${METEOR_VERSION}.jar"
  "https://raw.githubusercontent.com/Galax71/meteor-archive-and-Baritone-archive/master/files/meteor-client/meteor-client-${METEOR_VERSION}.jar"
)
mkdir -p "$A/custom/mods" "$A/custom/versions"

# Meteor Client: pinned by SHA-256
ok=0
for url in "${METEOR_URLS[@]}"; do
  if curl -fsSL --retry 3 -o "$A/custom/mods/meteor-client-${METEOR_VERSION}.jar" "$url" \
     && echo "${METEOR_SHA256}  $A/custom/mods/meteor-client-${METEOR_VERSION}.jar" | sha256sum -c -; then ok=1; break; fi
done
[ "$ok" = 1 ] || { echo "could not fetch a Meteor jar matching the pinned SHA-256"; exit 1; }

# Fabric API: newest build for 1.20.1, checked against Maven's own SHA-1
M=https://maven.fabricmc.net/net/fabricmc/fabric-api/fabric-api
FAPI=$(curl -fsSL --retry 3 "$M/maven-metadata.xml" | grep -o '<version>[^<]*+1\.20\.1</version>' | sed 's/<[^>]*>//g' | sort -V | tail -1)
[ -n "$FAPI" ] || { echo "no Fabric API for 1.20.1 found"; exit 1; }
echo "Fabric API $FAPI"
curl -fsSL --retry 3 -o "$A/custom/mods/fabric-api-$FAPI.jar" "$M/$FAPI/fabric-api-$FAPI.jar"
want=$(curl -fsSL --retry 3 "$M/$FAPI/fabric-api-$FAPI.jar.sha1")
echo "$want  $A/custom/mods/fabric-api-$FAPI.jar" | sha1sum -c -

# Fabric Loader: the launcher-profile JSON from Fabric's meta API
curl -fsSL --retry 3 -o /tmp/fabric-version.json "https://meta.fabricmc.net/v2/versions/loader/$GAME/$LOADER/profile/json"
ID=$(python3 -c "import json;d=json.load(open('/tmp/fabric-version.json'));assert d['inheritsFrom']=='$GAME';print(d['id'])")
cp /tmp/fabric-version.json "$A/custom/versions/$ID.json"
echo "Fabric version id: $ID"

# Pojav only: one profile, so it is the one the launcher starts with (Copper creates an instance in code)
if [ "${WRITE_PROFILE:-1}" = 1 ]; then
python3 - "$A/launcher_profiles.json" "$ID" <<'PY'
import json, sys
path, vid = sys.argv[1], sys.argv[2]
json.dump({
    "profiles": {"meteor-1-20-1": {"name": "Meteor Client 1.20.1", "lastVersionId": vid}},
    "selectedProfile": "meteor-1-20-1",
}, open(path, "w"), indent=2)
PY
cat "$A/launcher_profiles.json"
fi
ls -l "$A/custom/mods" "$A/custom/versions"
