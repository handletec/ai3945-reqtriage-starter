# GitHub Copilot Runtime Setup

This lab uses your existing GitHub Copilot access for two separate jobs:

1. **VS Code Copilot Chat with Claude** helps you write `run_agent()`.
2. **GitHub Copilot SDK** is called by your Python program while the agent is running.

These are separate uses of Copilot, even though they use the same GitHub account.

## No Anthropic API key is required

The normal classroom path does **not** require an Anthropic API key.

Your Python program uses the GitHub Copilot SDK and the GitHub account you authenticate with through Copilot CLI.

## 1. Install GitHub Copilot CLI

Choose one method.

### Windows

```powershell
winget install GitHub.Copilot
```

### macOS or Linux with Homebrew

```bash
brew install --cask copilot-cli
```

### Cross-platform with npm

Requires Node.js 22 or later.

```bash
npm install -g @github/copilot
```

## 2. Sign in

Run:

```bash
copilot login
```

Complete the GitHub OAuth sign-in in your browser.

Use the same GitHub account that has your Copilot entitlement.

Verify the CLI exists:

```bash
copilot --version
```

If your Copilot access is provided by an organization, that organization must allow Copilot CLI.

## 3. Install the Python SDK

After activating your Python virtual environment:

```bash
python -m pip install -r requirements.txt
```

The project pins:

```text
github-copilot-sdk==1.0.16
```

The SDK can reuse the credentials stored by `copilot login`.

## 4. Verify runtime access

Run:

```bash
python check_env.py
python model_check.py
```

Expected pattern:

```text
Connecting through your signed-in GitHub Copilot account...
Model responded: READY
Copilot runtime connection works.
```

The runtime model defaults to:

```text
auto
```

This lets GitHub choose a model available to your Copilot account.

The trainer may optionally ask you to set `COPILOT_MODEL` to a specific model, but this is not required for the core lab.

## Why the SDK has no tools

This lab deliberately creates the Copilot SDK client in `mode="empty"` and the session with:

```text
available_tools=[]
```

That means Copilot itself is not allowed to use shell, filesystem, or coding tools during the runtime call.

The runtime model can only return our JSON action request.

**Your Python code** decides whether `track_package()` is allowed and executes it.

That separation is the point of the exercise.

## Official references

- GitHub Copilot CLI installation: https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli
- GitHub Copilot CLI authentication: https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/authenticate-copilot-cli
- GitHub Copilot SDK authentication: https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/authenticate
