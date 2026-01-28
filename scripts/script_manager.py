
import os
import sys
import subprocess
from config import SCRIPTS_DIR, app_state

def save_script(script_name, script_code):
    """Save Python script to file"""
    filepath = os.path.join(SCRIPTS_DIR, f"{script_name}.py")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(script_code)

def load_script(script_name):
    """Load script content from file"""
    filepath = os.path.join(SCRIPTS_DIR, f"{script_name}.py")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def run_script(script_name):
    """Run Python script"""
    filepath = os.path.join(SCRIPTS_DIR, f"{script_name}.py")

    if not os.path.exists(filepath):
        print(f"Script {script_name}.py not found!")
        return

    if script_name in app_state.running_processes:
        stop_script(script_name)

    try:
        process = subprocess.Popen(
            [sys.executable, filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        app_state.running_processes[script_name] = process
        print(f"Started script: {script_name}.py (PID: {process.pid})")
    except Exception as e:
        print(f"Error running script: {e}")

def stop_script(script_name):
    """Stop running script"""
    if script_name in app_state.running_processes:
        process = app_state.running_processes[script_name]
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
        del app_state.running_processes[script_name]
        print(f"Stopped script: {script_name}.py")


def load_all_scripts():
    """Load all existing scripts from directory"""
    # Move import inside function to avoid circular dependency
    from scripts.script_nodes import add_script_node

    if os.path.exists(SCRIPTS_DIR):
        for filename in os.listdir(SCRIPTS_DIR):
            if filename.endswith('.py'):
                script_name = filename[:-3]
                add_script_node(script_name)
