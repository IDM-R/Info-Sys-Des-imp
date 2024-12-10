from flask import Flask, render_template, request, session, redirect, flash, jsonify, abort, url_for
from datetime import datetime
import pytz
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, relationship
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user, AnonymousUserMixin

from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///isd.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = os.urandom(24) #なんでもいいが、暗号化するのに使うurandomを使うことが多い。24バイトだか24文字、ということを示す。この文は必須

login_manager = LoginManager()
login_manager.init_app(app)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(app)

class MyAnonymousUser(AnonymousUserMixin):
    groups = []

login_manager.anonymous_user = MyAnonymousUser




class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    groups = db.relationship("Group", secondary="user_group", back_populates="members")

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    members = db.relationship("User", secondary="user_group", back_populates="groups")
    description = db.Column(db.Text, nullable=True)  # グループの説明
    messages = db.relationship('Message', backref='group', lazy=True)  # メッセージとのリレーション
    roles = db.Column(db.Text, nullable=True)  # 役割分担

class UserGroup(db.Model):
    __tablename__ = 'user_group'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    start_index = db.Column(db.Integer, nullable=False)  # 開始位置
    end_index = db.Column(db.Integer, nullable=False)    # 終了位置
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='comments', lazy=True)




class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    group = db.relationship('Group', backref=db.backref('items', lazy=True))
    themes = db.relationship('Theme', backref='related_item', lazy=True)  # 'item' から 'related_item' に変更

class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    item = db.relationship('Item')  

class TextBox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)  # テキストボックスの内容
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)  # 紐づくアイテム
    item = db.relationship('Item', backref=db.backref('textboxes', lazy=True))  # Itemとのリレーション
    like_count = db.Column(db.Integer, default=0)  # いいねの数を保存する新しいカラム
    







@login_manager.user_loader #これは書くだけで大丈夫そう(?)
def load_user(user_id):
    return User.query.get(int(user_id))
    

with app.app_context():
    db.create_all()



@app.route('/', methods=['GET','POST'])
@login_required
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        user_groups = current_user.groups
        return render_template('index.html', posts=posts, groups=user_groups)

    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email') 
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            error_message = "そのユーザー名は既に使用されています。別のユーザー名を選んでください。"
            return render_template('signup.html', error_message=error_message)
        
        new_user = User(email=email, username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect('/login')
    return render_template('signup.html')

    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
        else:
            error_message = "ユーザー名またはパスワードが間違っています。"
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')
    
@app.route('/logout')
@login_required #ログインしているからログアウトされる、という前提条件
def logout():
    logout_user()
    return redirect('/login')

    

@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        group_name = request.form.get('group_name')
        selected_members = request.form.getlist('members')  # 選択されたメンバーリストを取得
        
        # 現在のユーザーを追加
        if str(current_user.id) not in selected_members:
            selected_members.append(str(current_user.id))
        
        # デバッグ出力
        print("選択されたメンバー:", selected_members)

        if len(selected_members) < 2:  # メンバーが2人未満の場合
            flash('グループは2人以上のメンバーで作成してください！', 'error')
            return redirect('/create_group')

        # グループを作成
        new_group = Group(name=group_name)
        db.session.add(new_group)
        db.session.commit()

        # 選択されたメンバーをグループに追加
        for member_id in selected_members:
            user_group = UserGroup(user_id=int(member_id), group_id=new_group.id)
            db.session.add(user_group)

        db.session.commit()

        flash(f'グループ "{group_name}" を作成しました！', 'success')
        return redirect('/')
    
    # GETリクエスト時の処理
    users = User.query.filter(User.id != current_user.id).all()  # 自分以外のユーザーを取得
    return render_template('create_group.html', users=users)


    
    
@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def group_page(group_id):
    group = Group.query.get_or_404(group_id)
    user_groups = current_user.groups  # 現在のユーザーが所属するグループを取得
    items = Item.query.filter_by(group_id=group_id).all()  # グループに関連するアイテムを取得
    members=group.members

    # アイテムごとのテーマを取得
    for item in items:
        item.themes  # これで関連するテーマを取得可能

    if request.method == 'POST':
        item_title = request.form.get('item_title')  # フォームからタイトルを取得

        if item_title:
            # 修正済み
            new_item = Item(title=item_title, group_id=group_id)
            db.session.add(new_item)
            db.session.commit()
            flash('項目が追加されました！', 'success')
        else:
            flash('項目を入力してください。', 'error')

        return redirect(f'/group/{group_id}')  # 同じページにリダイレクト

    return render_template('group.html', group=group,members=members, groups=user_groups, items=items)




@app.route('/group/<int:group_id>/save', methods=['POST'])
@login_required
def save_group_data(group_id):
    data = request.json
    for item_id, item_data in data.items():
        item = Item.query.get(item_id)
        if item:
            item.title = item_data['content']  # content -> titleに変更
            db.session.commit()
    return jsonify({"message": "データが保存されました！"}), 200


@app.route('/group/<int:group_id>/edit/<int:item_id>', methods=['POST'])
@login_required
def edit_item(group_id, item_id):
    item = Item.query.get_or_404(item_id)

    if item.group_id != group_id:
        return jsonify({"message": "無効な操作です。"}), 400

    data = request.get_json()
    new_title = data.get('content')  # content -> titleに変更

    if new_title:
        item.title = new_title  # content -> titleに変更
        db.session.commit()
        return jsonify({"message": "項目が更新されました！"}), 200
    else:
        return jsonify({"message": "タイトルが空です。"}), 400




@app.route('/group/<int:group_id>/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(group_id, item_id):
    item = Item.query.get_or_404(item_id)

    # グループと一致しているか確認
    if item.group_id != group_id:
        flash('不正なリクエストです。', 'error')
        return redirect(f'/group/{group_id}')

    # アイテムに関連付けられたテーマを削除
    themes = Theme.query.filter_by(item_id=item_id).all()
    for theme in themes:
        db.session.delete(theme)

    # アイテムに関連付けられたTextBoxを削除
    text_boxes = TextBox.query.filter_by(item_id=item_id).all()
    for textbox in text_boxes:
        db.session.delete(textbox)

    # アイテム自体を削除
    db.session.delete(item)
    db.session.commit()
    flash('アイテムと関連するデータが削除されました。', 'success')
    return redirect(f'/group/{group_id}')




@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def item_page(item_id):
    item = Item.query.get_or_404(item_id)  # 選択された項目を取得
    group = Group.query.get(item.group_id)  # 項目が属するグループを取得
    user_groups = current_user.groups
    items = Item.query.filter_by(group_id=group.id).all()  # 同じグループの項目を取得
    themes = item.themes  # アイテムに関連するテーマを取得
    textboxes = TextBox.query.filter_by(item_id=item_id).all()
    comments = Comment.query.filter_by(item_id=item_id).all()  # アイテムに関連するコメントを取得

    if request.method == 'POST':
        # 項目のタイトル更新
        if 'new_title' in request.form:
            new_title = request.form.get('new_title')
            if new_title:
                item.title = new_title
                db.session.commit()
                flash('タイトルが更新されました！', 'success')
            else:
                flash('タイトルは空にできません。', 'error')

        # テーマ追加処理
        elif 'theme_content' in request.form:
            theme_content = request.form.get('theme_content')
            if theme_content:
                new_theme = Theme(content=theme_content, item_id=item_id)
                db.session.add(new_theme)
                db.session.commit()
                flash('テーマが追加されました！', 'success')
            else:
                flash('テーマを入力してください。', 'error')

        return redirect(f'/item/{item_id}')  # リダイレクトして変更を反映

        # コメント追加処理（インデックス番号を使用）
        if 'comment_content' in request.form and 'start_index' in request.form and 'end_index' in request.form:
            comment_content = request.form.get('comment_content')  # コメント内容
            start_index = request.form.get('start_index')  # 開始位置
            end_index = request.form.get('end_index')  # 終了位置

            if comment_content and start_index is not None and end_index is not None:
                new_comment = Comment(
                    item_id=item_id,
                    content=comment_content,
                    start_index=int(start_index),  # インデックス番号は整数型に変換
                    end_index=int(end_index),
                    user_id=current_user.id
                )
                db.session.add(new_comment)
                db.session.commit()
                flash('コメントが追加されました！', 'success')
            else:
                flash('コメント内容とインデックス番号は必須です。', 'error')

        # 他の処理が追加される場合のためリダイレクト
        return redirect(f'/item/{item_id}')

    # GETリクエストの処理
    return render_template(
        'item_page.html',
        item=item,
        group=group,
        groups=user_groups,
        items=items,
        themes=themes,
        textboxes=textboxes,
        comments=comments
    )






@app.route('/item/<int:item_id>/add_text', methods=['POST'])
@login_required
def add_text(item_id):
    item = Item.query.get_or_404(item_id)
    new_text = request.form.get('new_text')  # フォームから送信されたテキストを取得

    if new_text:
        # 既存のcontentに新しいテキストを追加
        item.content += f" {new_text}"  # 必要に応じて適切な区切りを追加
        db.session.commit()
        flash('テキストが追加されました！', 'success')
    else:
        flash('テキストが空です。', 'error')

    return redirect(f'/item/{item_id}')

@app.route('/item/<int:item_id>/delete_theme/<int:theme_id>', methods=['POST'])
@login_required
def delete_theme(item_id, theme_id):
    theme = Theme.query.get_or_404(theme_id)

    if theme.item_id != item_id:
        flash('無効な操作です。', 'error')
        return redirect(f'/item/{item_id}')

    db.session.delete(theme)
    db.session.commit()

    flash('テーマが削除されました！', 'success')
    return redirect(f'/item/{item_id}')


@app.route('/item/<int:item_id>/add_textbox', methods=['POST'])
@login_required
def add_textbox(item_id):
    item = Item.query.get_or_404(item_id)  # アイテムが存在しない場合404エラーを発生させる
    content = request.form.get('textbox_content', '')  # フォームから内容を取得

    if not content:
        flash('テキストボックスの内容が空です。', 'error')
        return redirect(f'/item/{item_id}')
    
    # 新しいテキストボックスを作成
    new_textbox = TextBox(content=content, item_id=item.id, like_count=0)
    db.session.add(new_textbox)
    db.session.commit()
    flash('新しいテキストボックスを追加しました！', 'success')
    return redirect(f'/item/{item_id}')




@app.route('/item/<int:item_id>/delete_textbox/<int:textbox_id>', methods=['POST'])
def delete_textbox(item_id, textbox_id):
    # データベースから対象のテキストボックスを取得
    textbox = TextBox.query.get_or_404(textbox_id)

    # テキストボックスが該当するアイテムに属しているか確認
    if textbox.item_id != item_id:
        abort(403)  # 不正な操作の場合は403エラーを返す

    # テキストボックスを削除
    db.session.delete(textbox)
    db.session.commit()

    flash('テキストボックスが削除されました。')
    return redirect(url_for('item_page', item_id=item_id))

@app.route('/textbox/<int:textbox_id>/like', methods=['POST'])
@login_required
def like_textbox(textbox_id):
    textbox = TextBox.query.get_or_404(textbox_id)
    textbox.like_count += 1  # いいねを1増加
    db.session.commit()
    return jsonify({'like_count': textbox.like_count})  # 更新後のカウントを返す




@app.route('/group/<int:group_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_group_content(group_id):
    target = request.args.get('target')  # GETパラメータで対象を指定
    if not target:
        flash("編集対象が指定されていません。", "error")
        return redirect(f'/group/{group_id}')
    
    group = Group.query.get_or_404(group_id)
    
    if request.method == 'POST':
        new_content = request.form.get('content')
        if target == 'テーマ':
            group.description = new_content
        elif target == '役割':
            # 改行区切りのリストをカンマ区切りに変換して保存
            group.roles = ','.join(line.strip() for line in new_content.splitlines() if line.strip())
        elif target == 'メモ':
            # メモを削除して、新しいメモのみを保存
            Message.query.filter_by(group_id=group_id).delete()  # 既存のメモを削除
            new_message = Message(content=new_content, group_id=group_id, user_id=current_user.id)
            db.session.add(new_message)
        db.session.commit()
        flash(f"{target} が更新されました。", "success")
        return redirect(f'/group/{group_id}')

    current_content = ''
    if target == 'テーマ':
        current_content = group.description or ''
    elif target == '役割':
        # カンマ区切りのデータを改行区切りに変換
        current_content = '\n'.join(group.roles.split(',')) if group.roles else ''
    elif target == 'メモ':
        current_content = ''  # メモ編集時には空にして新しい内容を入力させる

    return render_template(
        'edit.html',
        title=f"{target} を編集",
        current_content=current_content,
        save_url=url_for('edit_group_content', group_id=group_id, target=target),
        back_url=url_for('group_page', group_id=group_id)
    )



@app.route('/group/save_box', methods=['POST'])
@login_required
def save_box():
    data = request.get_json()  # フロントエンドから送信されたJSONデータを取得

    # データを検証
    description = data.get('description', '')
    roles = data.get('roles', [])
    memo = data.get('memo', [])

    if not description:
        return jsonify({"success": False, "message": "説明が空です"}), 400

    # グループの新しいデータを保存
    new_group = Group(
        description=description,
        roles=",".join(roles),
    )
    db.session.add(new_group)

    # メモを追加
    for memo_content in memo:
        new_message = Message(
            content=memo_content,
            group=new_group,
            user_id=current_user.id
        )
        db.session.add(new_message)

    # コミット
    db.session.commit()

    return jsonify({"success": True, "message": "新しいボックスが保存されました！"})


@app.route('/textbox/<int:textbox_id>/add_marker', methods=['POST'])
@login_required
def add_marker(textbox_id):
    data = request.json
    content = data.get('content')
    start_index = data.get('start_index')
    end_index = data.get('end_index')

    if not content or start_index is None or end_index is None:
        return jsonify({"error": "Invalid data"}), 400

    new_comment = Comment(
        item_id=textbox_id,
        content=content,
        start_index=start_index,
        end_index=end_index,
        user_id=current_user.id
    )
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"message": "Marker added successfully!", "comment_id": new_comment.id})


@app.route('/textbox/<int:comment_id>/delete_marker', methods=['POST'])
@login_required
def delete_marker(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Marker deleted successfully!"})


@app.route('/item/<int:item_id>/get_markers', methods=['GET'])
@login_required
def get_markers(item_id):
    markers = Comment.query.filter_by(item_id=item_id).all()
    marker_list = [
        {
            "id": marker.id,
            "content": marker.content,
            "start_index": marker.start_index,
            "end_index": marker.end_index,
            "user_id": marker.user_id,
        }
        for marker in markers
    ]
    return jsonify(marker_list)








    





if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost')