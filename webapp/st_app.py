import streamlit as st
from ml_api.ml import QuestionGenerationAPI

# https://qiita.com/irisu-inwl/items/9d49a14c1c67391565f8

@st.cache(allow_output_mutation=True)
def load_ml(ml):
    ml.load()
    return ml

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

    context_text = title = st.text_area('conxtext', '日本で一番高い山は富士山です。') 
    answer_text = title = st.text_input('answer', '富士山') 

    generate_button = st.button('Generate question')
    st.write('generated_question')
    if generate_button:
        generated_questions = generate(ml, [
                [answer_text, context_text]
            ])
        st.write(generated_questions[0])

if __name__ == '__main__':
    main()
