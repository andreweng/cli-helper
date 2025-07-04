#!/usr/bin/env python3

'''
Script that sends prompts to a local Ollama server.

Features:
- Sends prompts to the Ollama API and retrieves responses
- Suppresses all warnings from the urllib3 library
- Allows model specification with -m/--model option
- Logs all interactions to chat_history.txt in JSON format with timestamp and username
'''

import requests
import json
import argparse
import warnings
import urllib3
import os
import sys
import re
import subprocess
import datetime
import getpass
from contextlib import contextmanager

@contextmanager
def suppress_stdout_stderr():
    """Context manager to suppress stdout and stderr output."""
    # Save original stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    null_fd = os.open(os.devnull, os.O_RDWR)
    # Redirect stdout/stderr to devnull
    try:
        sys.stdout = os.fdopen(null_fd, 'w')
        sys.stderr = sys.stdout
        yield
    finally:
        # Restore stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr

def send_prompt(user_prompt, model="gemma3:12b", url="http://localhost:11434/api/generate"):
    """
    Send a prompt to the local Ollama server and return the response.
    
    Args:
        user_prompt (str): The prompt to send to the model
        model (str): The model name to use (default: gemma3:12b)
        url (str): The Ollama server endpoint (default: localhost:11434)
    
    Returns:
        str: The response from the model or error message
    """
    system_prompt = "You are a senior Site Reliability Engineer and Systems Administrator. You will provide short concise answers to technical questions no longer than 140 characters. Do not provide a follow up, do not provide any other responses other than the answer."
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": f"{system_prompt}\n\nUser: {user_prompt}",
        "stream": False
    }
    
    # Try with provided/default URL (localhost)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            return response.json().get("response", "")
    except (requests.RequestException, json.JSONDecodeError):
        pass
        
    # If localhost failed and we're using it, try with WSL nameserver IP
    if "localhost" in url:
        try:
            # Read /etc/resolv.conf to get WSL nameserver IP
            with open("/etc/resolv.conf", "r") as f:
                resolv_conf = f.read()
                # Extract the nameserver IP
                match = re.search(r'nameserver\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', resolv_conf)
                if match:
                    wsl_ip = match.group(1)
                    wsl_url = url.replace("localhost", wsl_ip)
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        response = requests.post(wsl_url, headers=headers, json=data, timeout=10)
                    if response.status_code == 200:
                        return response.json().get("response", "")

        except (FileNotFoundError, requests.RequestException, json.JSONDecodeError):
            pass
    
    # If all attempts failed
    return "Cannot contact ollama server."

# Command execution functionality removed as requested

def log_interaction(prompt, response, model):
    """
    Log the interaction to chat_history.txt in the script directory with timestamp and user.
    Format: JSON object with timestamp, username, model, prompt, and response fields
    """
    # Get script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    log_path = os.path.join(script_dir, "chat_history.txt")
    
    # Get current time in syslog format (e.g., Jun 27 22:20:11)
    timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S")
    
    # Get current username
    username = getpass.getuser()
    
    # Create log entry as JSON
    log_entry = json.dumps({
        "timestamp": timestamp,
        "username": username,
        "model": model,
        "prompt": prompt,
        "response": response
    })
    
    # Write to log file
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Warning: Could not log to chat_history.txt: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Send a prompt to a local Ollama server.")
    parser.add_argument("prompt", nargs="+", help="The prompt to send to the model")
    parser.add_argument("-m", "--model", default="gemma3:12b", help="The model to use (default: gemma3:12b)")
    args = parser.parse_args()
    
    # Join the prompt arguments into a single string
    user_prompt = " ".join(args.prompt)
    
    response = send_prompt(user_prompt, model=args.model)
    print(f">> {response}")
    
    # Log the interaction
    log_interaction(user_prompt, response, args.model)

if __name__ == "__main__":
    # Set environment variable to ignore all warnings (from ollama_prompt.py)
    os.environ['PYTHONWARNINGS'] = 'ignore'
    
    # Redirect stderr to /dev/null to suppress all warnings
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    
    try:
        main()
    finally:
        # Restore stderr
        sys.stderr.close()
        sys.stderr = original_stderr
