import json
import urllib.request

url = 'http://127.0.0.1:8000/generate'
data = {
    'answer_context': [
        { 'answer' : '中野', 'context': '私の名前は中野です。' }
    ]
}

headers = {
    'Content-Type': 'application/json',
}

req = urllib.request.Request(url, json.dumps(data).encode(), headers)
with urllib.request.urlopen(req) as res:
    body = json.load(res)
    for i in body['questions']:
        print(i['question'])
