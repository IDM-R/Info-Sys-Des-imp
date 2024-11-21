from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# サンプルデータ（項目ごとの内容を保持）
ITEM_CONTENTS = {
    "item-1": "これはアイテム1の内容です。",
    "item-2": "これはアイテム2の内容です。",
    "item-3": "これはアイテム3の内容です。",
    "item-4": "これはアイテム4の内容です。",
    "item-5": "これはアイテム5の内容です。",
    "item-6": "これはアイテム6の内容です。",
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_item_content', methods=['POST'])
def get_item_content():
    item_id = request.json.get('item_id')  # フロントエンドから送られるID
    content = ITEM_CONTENTS.get(item_id, "このアイテムの内容はありません。")
    return jsonify({"content": content})

if __name__ == '__main__':
    app.run(debug=True)
