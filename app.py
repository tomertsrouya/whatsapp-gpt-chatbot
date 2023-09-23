from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET-KEY'  # SECRET KEY CAN BE ANYTHING

# OPEN-AI CHAT GPT

openai.api_key = "Your-API-KEY"  # OPEN-AI API KEY
completion = openai.Completion()

start_chat_log = '''
System: 

Context:

'''

def ask(question, chat_log=None):
    print("Function 'ask' called with question:", question)

    if chat_log is None:
        chat_log = start_chat_log

    messages = [
        {"role": "system", "content": chat_log},
        {"role": "user", "content": question}
    ]

    print("Sending request to OpenAI with messages:", messages)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        answer = response.choices[0].message['content'].strip()
        print("Received response from OpenAI:", answer)
        return answer
    except openai.error.OpenAIError as e:
        print(f"Error: {e}")
        return str(e)


def append_interaction_to_chat_log(question, answer, chat_log=None):
    if chat_log is None:
        chat_log = start_chat_log
    return f'{chat_log}Human: {question}\nAI: {answer}\n'


account_sid = 'ACCOUNT-SID'
auth_token = 'AUTH-TOKEN' # Twilio Account Auth Token
client = Client(account_sid, auth_token)


# TWILIO

@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values['Body']
    print(incoming_msg)

    r = MessagingResponse()
    if incoming_msg:
        print("Received message:", incoming_msg)
        chat_log = session.get('chat_log')
        answer = ask(incoming_msg, chat_log)
        session['chat_log'] = append_interaction_to_chat_log(incoming_msg, answer, chat_log)
        r.message(answer)
        responded = True
    else:
        responded = False
    if not responded:
        r.message("Message Cannot Be Empty!")
    print("Sending response:", answer)

    return str(r)


if __name__ == '__main__':
    app.run(debug=True)
