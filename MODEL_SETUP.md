# Runtime Model Setup

GitHub Copilot access to Claude does **not** automatically give your Python program an Anthropic API connection.

For this lab you need runtime credentials supplied by the trainer.

## 1. Create your local environment file

### macOS / Linux

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

## 2. Edit .env

Set:

```text
ANTHROPIC_API_KEY=the-runtime-key-supplied-by-the-trainer
ANTHROPIC_MODEL=the-model-name-supplied-by-the-trainer
```

Do not paste the key into Python source.

Do not commit `.env`.

## 3. Verify

```bash
python check_env.py
python model_check.py
```

If `model_check.py` receives a response, the runtime model connection is ready.

If you were not given runtime credentials, tell the trainer before the coding checkpoint.
