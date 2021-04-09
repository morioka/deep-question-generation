import json
import urllib.request
import argparse

import sys


url = 'http://127.0.0.1:8000/generate'

headers = {
    'Content-Type': 'application/json',
}

for i in sys.stdin:
    answer, context = [ ii.strip() for ii in i.split(',', 1) ]  # CSV

    data = {
        'answer_context': [
            { 'answer' : answer,
              'context': context
              } 
            ]
    }

    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        body = json.load(res)
        for q in body['questions']:
            print(q['question'])
