#!/usr/bin/env bash
# Install render dependencies for whichever voice engine voice.json selects.
set -euo pipefail
sudo apt-get update -qq
sudo apt-get install -y -qq ffmpeg libcairo2-dev pkg-config fonts-dejavu-core openssl
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
