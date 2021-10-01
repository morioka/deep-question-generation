import streamlit as st
from ml_api.ml import QuestionGenerationAPI

import spacy
from spacy.pipeline import EntityRuler
from spacy import displacy

from collections import defaultdict

import pandas as pd

# https://qiita.com/irisu-inwl/items/9d49a14c1c67391565f8

@st.cache(allow_output_mutation=True)
def load_ml(ml):
    ml.load()
    return ml


@st.cache(allow_output_mutation=True)
def get_nlp():
    nlp = spacy.load('ja_ginza')
    try:
        entity_ruler = nlp.get_pipe("entity_ruler")
    except KeyError:
        entity_ruler = nlp.add_pipe("entity_ruler", before="ner")
    entity_ruler.initialize(lambda: [], nlp=nlp, patterns=[])
    return nlp, entity_ruler

def pickup_ne_candidates(doc):
    '''
    カッコで区切られた部分を固有表現の候補とする
    '''
    markers = [[ '「', '『', '"'],
               [ '」', '』', '"' ]]
    ne_hint, content, focus_marker = [], [], None
    ne_tokens, content_tokens, focus_types = [], [], []

    for token in doc:
        if focus_marker is not None:
            if token.text == markers[1][focus_marker]:  # 閉じカッコ
                # 閉じカッコ直前から遡って名詞・代名詞を固有表現候補に
                ne_hint = []
                for ti in reversed(range(content[0].i-1)):
                    t = doc[ti]
                    if t.pos_ in ['NOUN', 'PROPN']:
                        ne_hint.insert(0, t)
                    else:
                        break
                content_tokens.append(content)
                focus_types.append(markers[0][focus_marker])
                ne_tokens.append(ne_hint)

                content, focus_marker = [], None  # クリア
                continue
            elif token.text not in markers[0]:  # カッコ内 (さらなる開きカッコは考慮しない)
                content.append(token)
        if token.text in markers[0]:  # 開きカッコ
            focus_marker = markers[0].index(token.text)
            content = []
            continue

    return content_tokens, ne_tokens, focus_types


# カッコ前の名詞と固有表現との対応付け
ne_dict = defaultdict(lambda: 'Product')
ne_dict.update({
    '雑誌':             'Magazine',
    '誌':               'Magazine',
    '番組':             'Broadcast_Program',
    'ドラマ':           'Broadcast_Program',
    '映画':             'Movie',
    '作':               'Movie',
    'ロックバンド':     'Show_Organizaiton',
})


def summarize_sentences_none(nlp, text):
    '''
    テキストをそのまま返す。簡単な要約
    '''
    return text

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

def summarize_sentences(nlp, text, sentences_count=3):
    text1 = text.replace('\n', '')

    corpus = []
    originals = []
    doc = nlp(text1)
    for s in doc.sents:
        originals.append(s)
        tokens = []
        for t in s:
            tokens.append(t.lemma_)
        corpus.append(' '.join(tokens))

    del doc

    # 連結したcorpusを再度tinysegmenterでトークナイズさせる
    parser = PlaintextParser.from_string(''.join(corpus), Tokenizer('japanese'))

    summarizer = LexRankSummarizer()
    summarizer.stop_words = [' ']  # スペースも1単語として認識されるため

    # sentences_count に要約後の文の数を指定します。
    summary = summarizer(document=parser.document, sentences_count=sentences_count)

    # 元の文を表示
    return "".join([originals[corpus.index(sentence.__str__())].text for sentence in summary])


def summarize_sentences_head_and_tail(nlp, text):
    '''
    テキストの先頭文と末尾文を抜き出す。簡単な要約
    '''
    text1 = text.rstrip('\n').split('\n')
    
    return "".join([text1[0], text1[-1]])

def summarize_sentences_tail(nlp, text):
    '''
    テキストの末尾文を抜き出す。簡単な要約
    '''
    text1 = text.rstrip('\n').split('\n')
    
    return "".join([text1[-2], text1[-1]])

def ner_sentences(nlp, doc_text):
    doc = nlp(doc_text)

    tokens, ne_tokens, focus_types = pickup_ne_candidates(doc)
    patterns = []   # 新たなNEパターン
    ne = 'Product'  # 指定がなければ 'Product' とみなす

    # NHKバラエティ番組『LIFE！～人生に捧げるコント～』
    # token = [LIFE, ！, ～, 人生, に, 捧げる, コント, ～]
    # ne_token = [NHK, バラエティ, 番組]
    # focus_type = 『

    for t, n, f in zip(tokens, ne_tokens, focus_types):
        if f in ['『']:  # ニュース記事で新たな固有表現を導入する典型
            if len(n) > 0:
                ne = ne_dict[n[-1].text]  # カッコ直前のトークン列の末尾を代表NEと仮定
            else:
                None    # 省略の場合、直前の固有表現を引き継ぐと想定
            text = "".join([tok.text for tok in t])

            # 既に登録済のNEを除外
            if not [ ent for ent in doc.ents if ent.text == text and ent.label_ == ne]:
                patterns.append({"label": ne, "pattern": text})
    
    # 再度NER
    if len(patterns) > 0:
        print("add entity-ruler patterns: ", patterns)
        entity_ruler = nlp.get_pipe('entity_ruler')
        entity_ruler.add_patterns(patterns)
        doc = nlp(doc_text)

    return doc


@st.cache(allow_output_mutation=True)
def generate(ml, answer_context_list):
    return ml.generate_questions(answer_context_list)


def main():
    st.title('deep-question-generation sample')

    '''
    this is a [t5-base-japanese-question-generation](https://huggingface.co/sonoisa/t5-base-japanese-question-generation) sample.
    '''

    ml = QuestionGenerationAPI()
    ml = load_ml(ml)

    nlp, ruler = get_nlp()

    context_text = title = st.text_area('conxtext', context_default) 
    answer_text = title = st.text_input('answer', answer_default) 

    generate_button = st.button('Generate question')
    if generate_button:

        for (context, context_type) in [
            [summarize_sentences_none(nlp, context_text), 'そのまま'],
#            [summarize_sentences(nlp, context_text), '抽出型要約 sumy'],
            [summarize_sentences_head_and_tail(nlp, context_text), '先頭末尾'],
            [summarize_sentences_tail(nlp, context_text), '末尾2文'],
        ]:

            st.markdown("""---""")

            st.write(f'context ({context_type})')
            st.write(context)
            st.write('answer specified:')
            st.write(answer_text)

            doc = ner_sentences(nlp, context)
            st.write('first sentence:')
            for sent in doc.sents:
                st.write(sent.text)
                break

            st.write('generated_question:')
            generated_questions = generate(ml, [
                    [answer_text, context_text]
                ])
            st.write(generated_questions[0])


            # NEをanswerとしてquestion-generation
            ner_questions = []
            for ent in doc.ents:
                generated_questions = generate(ml, [
                        [ent.text, context_text]
                    ])
                ner_questions.append([
                    ent.text,
                    ent.label_,
                    ent.start_char,
                    ent.end_char,
                    generated_questions[0]
                ])
            df = pd.DataFrame(ner_questions, columns=['ent', 'label', 'start', 'end', 'question'])
            st.write('auto-generated_question:')
            st.table(df)

            del doc, df

if __name__ == '__main__':
    context_default = '日本で一番高い山は富士山です。'
    answer_default = '富士山' 

    # https://paradisefive.net/8589.html
    # 5/19(水) 16:02
#オリコン
#新垣結衣と星野源が結婚を発表「互いに支え合い豊かな時間を積み重ねていけたら」【コメント全文】
#（左から）星野源、新垣結衣　photo：KOBA（星野）、古謝知幸／ピースモンキー（新垣）　（C）oricon ME inc.
    context_default = """女優の新垣結衣（32）と歌手で俳優の星野源（40）が19日、所属事務所を通じて結婚することを発表した。
連名で「関係者の皆様　新緑の候、皆様におかれましてはご清栄のこととお慶び申し上げます。平素は格別のご高配を賜り、厚く御礼申し上げます」とし「私たち、星野源と新垣結衣は、このたび結婚する運びとなりました事をご報告させていただきます」と発表。
「これからも互いに支え合い豊かな時間を積み重ねていけたらと思っております。未熟な二人ではございますが、温かく見守っていただけますと幸いです」と呼びかけ「今後ともご指導ご鞭撻を賜りますようお願い申し上げます。最後になりますが、新型コロナウイルスの感染拡大が１日でも早く終息する事を、心よりお祈り申し上げます」と記した。
■コメント全文
関係者の皆様
新緑の候、皆様におかれましてはご清栄のこととお慶び申し上げます。
平素は格別のご高配を賜り、厚く御礼申し上げます。
私たち、星野源と新垣結衣は、このたび結婚する運びとなりました事をご報告させていただきます。
これからも互いに支え合い豊かな時間を積み重ねていけたらと思っております。
未熟な二人ではございますが、温かく見守っていただけますと幸いです。
今後ともご指導ご鞭撻を賜りますようお願い申し上げます。
最後になりますが、新型コロナウイルスの感染拡大が１日でも早く終息する事を、心よりお祈り申し上げます。

2021年5月19日
星野源　新垣結衣

星野は、1981年1月28日生まれ、埼玉県出身。シンガー・ソングライターとして活躍する一方、2013年に映画『箱入り息子の恋』で主演したほか、NHKバラエティ番組『LIFE！～人生に捧げるコント～』など、数々のドラマや映画、舞台に出演。新垣は1988年6月11日生まれ、沖縄県出身。ティーン誌『nicola』のモデルを経て、女優に。ドラマ『ドラゴン桜』（TBS系）、『マイ☆ボス マイ☆ヒーロー』（日本テレビ系）など数多くのドラマや映画に出演している。
2人は2016年のドラマ『逃げるは恥だが役に立つ』（TBS系、通称：逃げ恥）で共演し、夫婦役を演じた。また同ドラマの“恋ダンス”が大きな話題をよんだ。
"""
    answer_default = '逃げるは恥だが役に立つ'
    main()
