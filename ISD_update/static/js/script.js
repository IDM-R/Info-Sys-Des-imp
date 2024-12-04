document.addEventListener('DOMContentLoaded', () => {
    // メッセージボックスの制御
    const openButton = document.getElementById('openButton');
    const closeButton = document.getElementById('closeButton');
    const messageBox = document.getElementById('messageBox');
    const sendMessageButton = document.getElementById('sendMessage');
    const messagesContainer = document.getElementById('messages');
    const messageInput = document.getElementById('messageInput');

    // 項目とボードの関連データを保持する
    const items = {};
    let currentItemId = null;

   

    

    // ページロード時にすべての「いいね」ボタンを取得
    const likeButtons = document.querySelectorAll('.like-button');
    likeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const textboxId = button.dataset.textboxId;
            const likeCountSpan = button.querySelector('.like-count');
            fetch(`/textbox/${textboxId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}'
                }
            })
            .then(response => response.json())
            .then(data => {
                likeCountSpan.textContent = data.like_count;
            })
            .catch(error => {
                console.error('エラー:', error);
                alert('いいねの更新に失敗しました。');
            });
        });
    });
});

    




document.addEventListener('DOMContentLoaded', () => {
    const textboxes = document.querySelectorAll('.textbox-wrapper');

    textboxes.forEach((wrapper) => {
        const textarea = wrapper.querySelector('.editable-textarea');
        const displayDiv = wrapper.querySelector('.display-div');

        // 初期化：textareaの内容をdivに反映
        displayDiv.textContent = textarea.value;

        // 選択範囲にマーカーを追加
        displayDiv.addEventListener('mouseup', () => {
            const selection = window.getSelection();
            const selectedText = selection.toString().trim();

            if (selectedText) {
                const range = selection.getRangeAt(0);
                const startContainer = range.startContainer;
                const endContainer = range.endContainer;

                if (displayDiv.contains(startContainer) && displayDiv.contains(endContainer)) {
                    const span = document.createElement('span');
                    span.className = 'highlight';
                    span.textContent = selectedText;

                    span.addEventListener('click', () => {
                        // クリックでマーカーを削除
                        span.replaceWith(document.createTextNode(span.textContent));
                    });

                    range.deleteContents();
                    range.insertNode(span);

                    // 選択を解除
                    selection.removeAllRanges();

                    // サーバーに選択範囲を保存
                    const textboxId = wrapper.dataset.textboxId;
                    fetch(`/textbox/${textboxId}/add_marker`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            content: selectedText,
                            start_index: range.startOffset,
                            end_index: range.endOffset,
                        }),
                    }).then((response) => response.json());
                }
            }
        });

        // textareaとdivの同期（必要に応じて）
        textarea.addEventListener('input', () => {
            displayDiv.textContent = textarea.value;
        });
    });
});




//document.addEventListener('DOMContentLoaded', () => {
//    const gridBox = document.querySelector('.grid-box');
//    let draggedElement = null;

    // ドラッグ開始
//    gridBox.addEventListener('dragstart', (event) => {
//        if (event.target.classList.contains('textbox-wrapper')) {
//            draggedElement = event.target;
//            setTimeout(() => {
//                draggedElement.style.display = 'none'; // ドラッグ中は非表示
//            }, 0);
//        }
//    });

    // ドラッグ終了
//    gridBox.addEventListener('dragend', () => {
//        if (draggedElement) {
//            draggedElement.style.display = ''; // 再表示
//            draggedElement = null;

            // 新しい順序を保存
//            saveOrder();
//        }
//    });

    // ドラッグオーバー
//    gridBox.addEventListener('dragover', (event) => {
//        event.preventDefault();
//        const closestElement = [...gridBox.children].find((child) => {
//            return child !== draggedElement && child.getBoundingClientRect().top > event.clientY;
//        });

//        if (closestElement) {
//            gridBox.insertBefore(draggedElement, closestElement);
//        } else {
//            gridBox.appendChild(draggedElement);
//        }
//    });

    // サーバーに順序を保存
//    function saveOrder() {
//        const orderData = [...gridBox.children].map((child, index) => ({
//            id: child.dataset.textboxId,
//            order: index
//        }));

//        fetch('/textbox/update_order', {
//            method: 'POST',
//            headers: {
//                'Content-Type': 'application/json',
//            },
//            body: JSON.stringify(orderData),
//        }).then((response) => response.json())
//          .then((data) => console.log(data.message))
//          .catch((error) => console.error('順序の保存に失敗しました:', error));
//    }
//});



