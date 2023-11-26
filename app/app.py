from flask import Flask, render_template, request, jsonify
import os
from chat import ChatSession

app = Flask(__name__)
chat_session = None
with open("./prompts/system_message.txt", "r") as f:
    sys_msg = f.read()


@app.route('/')
def index():
    global chat_session
    chat_session = ChatSession(sys_msg)
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.form['user_message']
    rag_strategy = request.form['rag_strategy']
    top_n = request.form['limit']
    cosine_threshold = request.form['cosine_threshold']
    print(f"Using RAG strategy: {rag_strategy} to service query: {user_message}")
    chatRes = chat_session.answer_query(user_message, rag_strategy=rag_strategy,
                                        top_n=int(top_n), cosine_threshold=float(cosine_threshold))
    response_with_line_breaks = chatRes.response.replace('\n', '<br>')
    #print("Response: ", response_with_line_breaks)
    #print("Steps: ", chatRes.steps)
    return jsonify({'response': response_with_line_breaks, 'steps': chatRes.steps})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    #app.run(debug=True)
