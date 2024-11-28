// 項目とボードの関連データを保持する
const items = {};
let currentItemId = null;



// 項目を選択してボードに表示
function selectItem(itemId) {
    currentItemId = itemId;

    // 項目の内容をボードに表示
    const selectedItem = items[itemId];

    // ボードのタイトルを更新
    document.getElementById('boardTitleInput').textContent = selectedItem.title;

    // ボードの内容を更新
    const boardContent = document.getElementById('boardContent');
    boardContent.value = selectedItem.content;  // 内容を表示
}



// データをサーバーに保存
function saveData() {
    const groupId = document.getElementById('saveButton').dataset.groupId;

    fetch(`/group/${groupId}/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(items)
    }).then(response => {
        if (response.ok) {
            alert("データが保存されました！");
        } else {
            alert("データの保存に失敗しました。");
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    // ページロード時にすべての「いいね」ボタンを取得
    const likeButtons = document.querySelectorAll('.like-button');

    likeButtons.forEach(button => {
        button.addEventListener('click', function () {
            // ボタンのデータ属性からテキストボックスIDを取得
            const textboxId = button.dataset.textboxId;
            const likeCountSpan = button.querySelector('.like-count');

            // サーバーにPOSTリクエストを送信
            fetch(`/textbox/${textboxId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}' // 必要に応じてCSRFトークンを追加
                }
            })
            .then(response => response.json())
            .then(data => {
                // サーバーから返ってきた最新のlike_countを表示
                likeCountSpan.textContent = data.like_count;
            })
            .catch(error => {
                console.error('エラー:', error);
                alert('いいねの更新に失敗しました。');
            });
        });
    });
});








