# Ollama CLI Interface

## Overview

This Python script (`prompt.py`) provides a simple command-line interface to interact with a local [Ollama](https://ollama.com/) server. It sends prompts to your locally running AI models and formats the responses in a clean, consistent way.

## Features

- Sends prompts to the Ollama API and retrieves responses
- Suppresses all warnings from underlying libraries
- Allows model specification with `-m/--model` option
- Logs all interactions to `chat_history.txt` in JSON format with timestamp and username
- Formats responses with a clean prefix (`>>`) for readability

## Prerequisites

- Python 3.6+
- [Ollama](https://ollama.com/) installed and running locally
- Required Python packages: `requests`

## Installation

1. Make sure the script is executable:

```bash
chmod +x /path/to/prompt.py
```

2. Set up an alias in your shell configuration file (`.bashrc`, `.zshrc`, etc.):

```bash
# For bash (add to ~/.bashrc)
alias ask="/path/to/prompt.py"

# For zsh (add to ~/.zshrc)
alias ask="/path/to/prompt.py"
```

3. Reload your shell configuration:

```bash
source ~/.bashrc  # or source ~/.zshrc for ZSH users
```

## Usage

Once your alias is set up, you can ask questions directly:

```bash
ask what is the capital of France?
>> Paris
```

To specify a different model:

```bash
ask -m llama3:8b what's the meaning of life?
>> 42
```

## Changing the Default Model

The script currently uses `gemma3:12b` as the default model. To change it:

1. Open the script in your favorite editor:

```bash
vim /path/to/prompt.py
```

2. Find line 128 where the default model is specified:

```python
parser.add_argument("-m", "--model", default="gemma3:12b", help="The model to use (default: gemma3:12b)")
```

3. Change `gemma3:12b` to your preferred model (e.g., `llama3:8b`, `mistral:7b`, etc.)

4. Save the file

## Available Models

To see which models you have installed in Ollama:

```bash
ollama list
```

To download a new model:

```bash
ollama pull <model-name>
```

## Logs

All interactions are logged to `chat_history.txt` in the same directory as the script. Each entry includes:

- Timestamp
- Username
- Model used
- Prompt sent
- Response received

## Troubleshooting

- If you get "Could not connect to Ollama server" errors, make sure Ollama is running
- If a model is not found, use `ollama pull <model-name>` to download it
- For other issues, check that your Ollama server is properly configured
