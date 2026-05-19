# OpenAI Verify API

HTTP API for `https://openai.com/research/verify/` to detect AI-generated images containing C2PA metadata and/or SynthID watermarks, and reports whether either is detected.

Uses [CloakBrowser](https://github.com/CloakHQ/CloakBrowser) to obtain a Turnstile token.

## Quick start

```bash
git clone https://github.com/ndlyyyyy/openai-verify-api.git
cd openai-verify-api
python -m pip install -e .
python -m openai_verify_api
```

Optional CLI arguments:

- `--host` (default: `127.0.0.1`)
- `--port` (default: `8000`)

## Verify a single file

```bash
curl -X POST http://127.0.0.1:8000/verify \
  -F "file=@/path/to/image.png"
```

Example response:

```json
{
  "filename": "image.png",
  "media_type": "image/png",
  "openai_generated": true,
  "upstream": {
    "object": "provenance_check",
    "created_at": 1779225920,
    "results": [
      {
        "type": "c2pa",
        "issuer": "OpenAI OpCo, LLC",
        "outcome": "detected",
        "validation_state": "trusted"
      },
      {
        "type": "synthid",
        "outcome": "detected"
      }
    ]
  }
}
```

## Run tests

```bash
python -m pytest -q
```
