from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from generateQuiz.type2text.url2text import url2text
from generateQuiz.type2text.doc2text import doc2text
import ast
PROMPT_TEMPLATE = """
Do task only based on this context:

{context}

---

Generate {quantity} {difficulty} {question} for this context {format}
"""

url_yt = "https://www.youtube.com/shorts/g9fIWtSexLs?feature=share"
url_web = "https://www.w3schools.com/python/python_dictionaries.asp"

# Declaring 5 basic types of question to generate
question = {
    'MCQ':"""in this dict format in list
                [/{'question' = "question_text",
                'option1': "option_a",
                'option2': "option_b",
                'option2': "option_c",
                'answer' = key_of_correct_option /}]""",
    'Short answer questions': """with short hints in this dict format in list
   [ /{'question': "question",
    'hint1': "first_hint",
    'hint2': "second_hint",
    'hint3': "third_hint",
    'answer': "answer" /} ]   
    
    """,
    'True or False questions': """ in this dict format in list. only use True or False in the options
                [/{'question': question_text,
                'option1': True,
                'option2': False,
                'answer': correct_option /}]""",
    'Real World Problem Solving questions' : """with short hints in this dict format in list
    [/{'question': "question",
    'hint1': "first_hint",
    'hint2': "second_hint",
    'hint3': "third_hint",
    'answer': "answer" /} ]   
    
    """

}

# converts data['q_type'] data into usable key for question dictionary
def get_question_type(q_type):
    if q_type == 'mcq':
        return 'MCQ'
    elif q_type == 'shaq':
        return 'Short answer questions'
    elif q_type == 'tfq':
        return 'True or False questions'
    else:
        return 'Real World Problem Solving questions'


def generateQuiz(data):  # context_type, question_type, question_format
    data['q_type'] = get_question_type(data['q_type'])
    quizzes = []

    if data['con_type'] == 'url':
        query_text = data['q_type']
        context_text = url2text(data['url'])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(quantity = data['quantity'], context=context_text, question=query_text, format=question[data['q_type']], difficulty=data['difficulty'])

        model = ChatOpenAI()
        response_text = model.predict(prompt)
        for quiz in ast.literal_eval(response_text):
            quizzes.append(quiz)
        return quizzes

    elif data['con_type'] == 'document':
        texts = doc2text(data['doc'][1], slice(data['doc'][2], data['doc'][0]))
   
        for context in texts:
            query_text = data['q_type']
            context_text = context
            prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            prompt = prompt_template.format(quantity = data['quantity'], context=context_text, question=query_text, format=question[data['q_type']], difficulty=data['difficulty'])

            model = ChatOpenAI()
            response_text = model.predict(prompt)
            print(response_text)
            response_text = ast.literal_eval(response_text)
            for quiz in response_text:
                quizzes.append(quiz)
        return quizzes

    elif data['con_type'] == 'text':
        query_text = data['q_type']
        context_text = data['text']
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(quantity = data['quantity'], context=context_text, question=query_text, format=question[data['q_type']], difficulty=data['difficulty'])

        model = ChatOpenAI()
        response_text = model.predict(prompt)

        for quiz in ast.literal_eval(response_text):
            quizzes.append(quiz)
        return quizzes
#try:
 #   quizzes = ast.literal_eval(generateQuiz('doc',list(question.keys())[0],question['MCQ']))
#except:
 #   quizzes = generateQuiz('doc',list(question.keys())[0],question['MCQ'])
