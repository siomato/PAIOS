import requests

BASE = "http://127.0.0.1:8000"

response = requests.post(
    f"{BASE}/ask",
    json={"question": "What is Python?"},
    timeout=30,
)

print("HTTP:", response.status_code)
print(response.text)
response.raise_for_status()
