import subprocess

def run_prompt(prompt_file, input_data, model="dolphin3"):
    cmd = f"(cat {prompt_file}; echo; echo '{input_data}') | ollama run {model}"
    return subprocess.check_output(cmd, shell=True, text=True).strip()

