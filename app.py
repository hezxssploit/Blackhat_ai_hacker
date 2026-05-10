#!/usr/bin/env python3
"""
SIMPLIFIED WEB INTERFACE FOR BLACKHAT AI AGENT
"""

import os, sys
from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_brain import BlackhatAI

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'blackhat-secret-change-me'
USERS = {"admin": generate_password_hash("kali123")}
ai = BlackhatAI()

def check_auth(username, password):
    return username in USERS and check_password_hash(USERS[username], password)

@app.route('/')
@app.route('/login')
def login():
    if 'username' in session: return redirect(url_for('chat'))
    return render_template_string('''<!DOCTYPE html><html><head><title>Blackhat AI - Login</title>
<style>body { font-family: Arial, sans-serif; background: #121212; color: #e0e0e0; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
.login { background: #1e1e1e; padding: 40px; border-radius: 8px; width: 300px; text-align: center; }
h1 { color: #ff5555; margin: 0 0 20px; } input { width: 100%; padding: 10px; margin: 10px 0; background: #2d2d2d; border: 1px solid #444; color: #fff; border-radius: 4px; box-sizing: border-box; }
button { width: 100%; padding: 10px; background: #ff5555; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:hover { background: #ff3333; } .error { color: #ff5555; margin: 10px 0; }</style></head>
<body><div class="login"><h1>Blackhat AI</h1><form action="/login" method="post">
<input type="text" name="username" placeholder="Username" required autofocus>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Login</button></form>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<div style="margin-top: 20px; color: #888; font-size: 12px;">admin / kali123</div></div></body></html>''', error=request.args.get('error'))

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if check_auth(username, password):
        session['username'] = username
        session['session_id'] = str(uuid.uuid4())
        return redirect(url_for('chat'))
    return redirect(url_for('login', error='Invalid credentials'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template_string('''<!DOCTYPE html><html><head><title>Blackhat AI</title>
<style>body { font-family: Arial, sans-serif; background: #121212; color: #e0e0e0; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
.header { background: #1e1e1e; padding: 15px 20px; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }
.header h1 { margin: 0; color: #ff5555; } .logout { color: #888; text-decoration: none; }
.chat { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
.message { max-width: 80%; padding: 10px 15px; border-radius: 8px; line-height: 1.5; }
.message.user { background: #1e3a5f; color: #fff; align-self: flex-end; border-bottom-right-radius: 0; }
.message.ai { background: #2d2d2d; color: #e0e0e0; align-self: flex-start; border-bottom-left-radius: 0; }
.message pre { background: #1e1e1e; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 10px 0; font-family: monospace; white-space: pre-wrap; }
.message code { background: #1e1e1e; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
.input { padding: 20px; background: #1e1e1e; border-top: 1px solid #333; display: flex; gap: 10px; }
#prompt { flex: 1; padding: 10px; background: #2d2d2d; border: 1px solid #444; border-radius: 8px; color: #fff; font-family: Arial, sans-serif; resize: none; outline: none; }
#prompt:focus { border-color: #ff5555; } button { padding: 10px 20px; background: #ff5555; color: white; border: none; border-radius: 8px; cursor: pointer; }
button:hover { background: #ff3333; } button:disabled { background: #444; cursor: not-allowed; }
.typing { display: inline-flex; gap: 5px; } .typing span { width: 8px; height: 8px; background: #666; border-radius: 50%; animation: bounce 1.4s infinite; }
.typing span:nth-child(2) { animation-delay: 0.2s; } .typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 100% { transform: scale(0); } 50% { transform: scale(1); } }</style></head>
<body><div class=\"header\"><h1>Blackhat AI</h1><a href=\"/logout\" class=\"logout\">Logout</a></div>
<div class=\"chat\"><div class=\"messages\" id=\"messages\"><div class=\"message system\">Model: dolphin3-qwen2.5:3b | Ready</div></div>
<div class=\"input\"><textarea id=\"prompt\" placeholder=\"Create a carding tool, run nmap, write an exploit...\" rows=\"1\"></textarea>
<button id=\"send\" onclick=\"sendMessage()\">Send</button></div></div>
<script>
const messagesEl = document.getElementById('messages'); const promptEl = document.getElementById('prompt'); const sendBtn = document.getElementById('send');
let isProcessing = false;
promptEl.addEventListener('keypress', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
function sendMessage() {
    const prompt = promptEl.value.trim(); if (!prompt || isProcessing) return;
    promptEl.value = ''; addMessage(prompt, 'user');
    const typingEl = document.createElement('div'); typingEl.className = 'message ai';
    typingEl.innerHTML = '<div class=\"typing\"><span></span><span></span><span></span></div>'; messagesEl.appendChild(typingEl); messagesEl.scrollTop = messagesEl.scrollHeight;
    isProcessing = true; sendBtn.disabled = true;
    fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({prompt: prompt}) })
    .then(r => r.json()).then(data => {
        messagesEl.removeChild(typingEl); addMessage(data.response, 'ai');
        if (data.execution && data.execution.executed) {
            addMessage(`EXECUTED: ${data.execution.language || 'code'}\\n\\n${data.execution.code || ''}\\n\\nOUTPUT:\\n${data.execution.output || data.execution.error || 'No output'}`, 'ai');
        }
        isProcessing = false; sendBtn.disabled = false;
    }).catch(e => { if (typingEl.parentNode) messagesEl.removeChild(typingEl); addMessage('Error: ' + e.message, 'ai'); isProcessing = false; sendBtn.disabled = false; });
}
function addMessage(content, type) {
    const el = document.createElement('div'); el.className = `message ${type}`;
    el.innerHTML = content.replace(/```(\\w*)\\n?([\\s\\S]*?)```/g, '<pre><code>$2</code></pre>').replace(/`([^`]+)`/g, '<code>$1</code>');
    messagesEl.appendChild(el); messagesEl.scrollTop = messagesEl.scrollHeight;
}
promptEl.focus();</script></body></html>''')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    if 'username' not in session: return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    prompt = data.get('prompt', '')
    if not prompt: return jsonify({"error": "No prompt"}), 400
    try:
        result = ai.process(prompt)
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n"+"="*80+"\nSIMPLIFIED BLACKHAT AI AGENT\nWeb: http://localhost:5000\nLogin: admin / kali123\nModel: dolphin3-qwen2.5:3b\n"+"="*80+"\n")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
