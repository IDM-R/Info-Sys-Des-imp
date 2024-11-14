from flask import Flask, render_template, request, jsonify
import datetime

app = Flask(__name__)

# ダミーデータの格納（本番ではDBを使用）
opinions = []

@app.route('/')
def index():
    return render_template('index.html', opinions=opinions)

@app.route('/add_opinion', methods=['POST'])
def add_opinion():
    opinion_text = request.form['opinion']
    opinion = {
        "text": opinion_text,
        "feedback": [],
        "timestamp": datetime.datetime.now().strftime("%H:%M")
    }
    opinions.append(opinion)
    return jsonify(success=True)

@app.route('/add_feedback', methods=['POST'])
def add_feedback():
    opinion_index = int(request.form['opinion_index'])
    feedback_text = request.form['feedback']
    timestamp = datetime.datetime.now().strftime("%H:%M")
    opinions[opinion_index]["feedback"].append({"text": feedback_text, "timestamp": timestamp})
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
