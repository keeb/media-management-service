import subprocess
import shlex


def run_prompt(prompt_file, input_data, model="dolphin3"):
    cmd = f"(cat {prompt_file}; echo; echo {shlex.quote(input_data)}) | ollama run --think=false {model}"
    return subprocess.check_output(cmd, shell=True, text=True).strip()
