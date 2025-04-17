from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import uuid
import os

# Gemini Chat
from gemini_chat import generate as generate_with_gemini

# Load environment vars (optional)
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "dev-secret")
socketio = SocketIO(app, cors_allowed_origins="*")

# Hardcoded Gemini API key (use env var for prod)
GEMINI_API_KEY = "AIzaSyCqMbsrXn42qt2VAVDnudhWTTOPiFz5tj4"

# In-memory store for user emotional context
user_contexts = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    session['user_id'] = str(uuid.uuid4())
    user_contexts[session['user_id']] = {
        'messages': [],
        'turns': 0,
        'awaiting_poem': False
    }
    print(f"Client connected: {session['user_id']}")

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    user_contexts.pop(user_id, None)
    print(f"Client disconnected: {user_id}")

@socketio.on('message')
def handle_message(data):
    user_message = data.get('message', '').strip()
    user_id = session.get('user_id', 'unknown')
    
    if not user_message:
        return

    emit('message', {
        'user': 'user',
        'message': user_message
    }, broadcast=True, include_self=False)

    context = user_contexts.get(user_id)
    if not context:
        context = user_contexts[user_id] = {'messages': [], 'turns': 0, 'awaiting_poem': False}

    context['messages'].append(user_message)
    context['turns'] += 1

    # After 2 user inputs, generate the poem
    if context['turns'] >= 2:
        full_context = " ".join(context['messages'])

        prompt = f"""
You are an empathetic poet bot. Based on the following emotional conversation from a grieving user,
generate a short poem (4–8 lines) that reflects their emotional state. Be gentle, sincere, and personal.
Avoid clichés, and never name the person directly. Just capture the *feeling* and *loss*.

Conversation context:
\"\"\"
{full_context}
\"\"\"

Poem:
"""
        messages = [("user", prompt)]
        poem = generate_with_gemini(messages, GEMINI_API_KEY)

        if poem:
            poem_html = poem.replace(".", "<br>").strip()
            emit('message', {
                'user': 'assistant',
                'message': poem_html
            }, broadcast=True)
        else:
            emit('message', {
                'user': 'assistant',
                'message': "I'm here for you, but I need a moment to find the right words."
            }, broadcast=True)

        # Reset context after poem
        context['messages'] = []
        context['turns'] = 0
        context['awaiting_poem'] = False

    else:
        # Empathetic response before poem
        follow_ups = [
            "That sounds really heavy. Can you tell me a bit more about how you're feeling?",
            "I hear you. What part of this loss or emotion feels the hardest?",
            "Thank you for sharing. Would you mind sharing one memory or feeling that stands out?"
        ]
        follow_up = follow_ups[context['turns'] % len(follow_ups)]

        emit('message', {
            'user': 'assistant',
            'message': follow_up
        }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8000)
