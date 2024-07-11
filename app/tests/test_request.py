import requests

def stream_llm_request(prompt_text):
    url = "http://localhost:8000/api/llm/execute_llm"
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt_text}
    
    response = requests.post(url, headers=headers, json=data, stream=True)
    
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    prompt_text = "customers 테이블의 모든 정보 가져와줘"
    stream_llm_request(prompt_text)

