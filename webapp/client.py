import json
import urllib.request
import argparse

import sys

parser = argparse.ArgumentParser('deep-question-generatoin api client')
parser.add_argument('--endpoint', default='http://127.0.0.1:8000/generate')
parser.add_argument('--format', choices=['csv', 'tsv','jaqket-wikipedia-entities'], default='csv')
args = parser.parse_args()

url = args.endpoint

headers = {
    'Content-Type': 'application/json',
}

for line in sys.stdin:
    if args.format == 'csv':
        parts = line.split(',', 1)  # csv
    elif args.format == 'tsv':
        parts = line.split('\t', 1)  # tsv
    else:
        parts_ = json.loads(line)
        parts = [parts_['title'], parts_['text']]

    answer, context = [part.strip() for part in parts]

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
