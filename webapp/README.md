'''bash
% ./start.sh
INFO:     Started server process [8979]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

% echo 北岳,日本で二番目に高い山は北岳です。 | python ./client.py
日本で2番目に高い山は何ですか?
% cat ./answer_context.tsv
北岳    日本で二番目に高い山は北岳です。
% cat ./answer_context.tsv | python ./client.py --format tsv
日本で2番目に高い山は何ですか?
% gzip -dc all_entities.json.gz | head | python ./client.py --format jaqket-wikipedia-entities
acchusは何の神ですか?
親鸞の末娘の名前は何ですか?
ジャック・デリダはどんな哲学者でしたか?
アステカ神話で地母神とされているのは誰ですか?
龍斎は誰の別名ですか?
「指輪物語」、「シルマリルの物語」はどこから来ましたか?
鳥羽天皇の生母は誰ですか?
小説が直接本として出版されることを何と言いますか?
クモの神性は何ですか?
露出を自動的に制御し、被写体の明度に応じた露出値を得る写真機は何と呼ばれていますか?
'''
