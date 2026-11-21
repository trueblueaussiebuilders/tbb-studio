#!/usr/bin/env bash
# Install render dependencies for whichever voice engine voice.json selects.
#
# The apt step used to dominate the post build (38s on 2026-11-18, 6 min on 11-19, 12 min on 11-20), so:
#  - packages already on the runner are skipped (no apt at all if nothing is missing),
#  - Recommends are never pulled (ffmpeg's drag in ~100 MB of video drivers we don't use),
#  - the runner's existing package lists are tried first; `apt-get update` only runs if that fails,
#  - every apt call has a time limit, with one clean retry, so a stalled mirror can't hang the post.
set -euo pipefail
SECONDS=0
PKGS="ffmpeg libcairo2-dev pkg-config fonts-dejavu-core openssl"
APT_TIMEOUT=${APT_TIMEOUT:-420}
export DEBIAN_FRONTEND=noninteractive NEEDRESTART_SUSPEND=1

missing=""
for p in $PKGS; do
  dpkg-query -W -f='${Status}' "$p" 2>/dev/null | grep -q "install ok installed" || missing="$missing $p"
done

apt_install() {
  sudo -E timeout "$APT_TIMEOUT" apt-get install -y -qq --no-install-recommends -o Dpkg::Use-Pty=0 $missing
}
apt_update() {
  sudo -E timeout "$APT_TIMEOUT" apt-get update -qq || echo "::warning::apt-get update failed or timed out"
}
apt_repair() { sudo -E dpkg --configure -a >/dev/null 2>&1 || true; }

if [ -n "$missing" ]; then
  echo "apt: installing$missing"
  if ! apt_install; then
    echo "apt: refreshing package lists (${SECONDS}s)"
    apt_repair; apt_update
    if ! apt_install; then
      echo "::warning::apt install failed, retrying once (${SECONDS}s)"
      apt_repair; sleep 10; apt_update; apt_install
    fi
  fi
else
  echo "apt: nothing to install"
fi
command -v ffmpeg >/dev/null || { echo "::error::ffmpeg missing after install"; exit 1; }
echo "system packages ready in ${SECONDS}s"

pip install -q -r requirements.txt
ENGINE=${VOICE_ENGINE:-$(python3 -c "import json; print(json.load(open('voice.json')).get('engine', 'kokoro'))")}
echo "voice engine: $ENGINE"
case "$ENGINE" in
  chatterbox)
    pip install -q torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
    pip install -q chatterbox-tts==0.1.7 ;;
  kokoro)
    pip install -q "kokoro-onnx>=0.4" ;;
esac
echo "install done in ${SECONDS}s"
