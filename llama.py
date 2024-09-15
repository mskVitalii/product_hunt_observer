import json

import requests


def translate_to_russian(english_text):
    url = 'http://host.docker.internal:11434/api/generate'
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "llama3.1",
        "prompt": f"Translate the following text to Russian (without quotes and any additional information, just the "
                  f"translation): \"{english_text}\""
    }

    response = requests.post(url, json=data, headers=headers, stream=True)

    full_response = ""

    for line in response.iter_lines():
        if line:
            try:
                parsed_json = json.loads(line.decode('utf-8'))
                full_response += parsed_json.get("response", "")
            except json.JSONDecodeError as e:
                print(f"Error processing line: {line}, error: {e}")

    return full_response
