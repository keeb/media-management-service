from mediaservice.ollama import run_prompt

filename = "WeCrashed.S01E01.1080p.WEBRip.x265-RARBG[eztv.re].mp4"
json_result = run_prompt("../../prompts/filename-to-json.prompt", filename)
save_path = run_prompt("../../prompts/json-to-save-path.prompt", json_result)
