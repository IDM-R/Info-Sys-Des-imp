document.getElementById('addItemBtn').addEventListener('click', () => {
    const newItem = document.createElement('div');

    newItem.className = 'box';
    newItem.textContent = `Item ${document.querySelectorAll('.box').length + 1}`;
    //新しいところ開始
    const itemId = `item-${document.querySelectorAll('.box').length + 1}`;
    newItem.dataset.id = itemId;
    //ここまで

    //新しいところ開始
    const itemContainer = document.getElementById('itemContainer');
    const boardContent = document.getElementById('boardContent');
    //ここまで
    
    // コンテナに追加
    document.getElementById('itemContainer').appendChild(newItem);

    newItem.addEventListener('click', () => {
        const newName = prompt('Enter a new name for this item:', newItem.textContent);
        if (newName !== null && newName.trim() !== '') {
            newItem.textContent = newName.trim();
        }
    });

    //項目クリック時に対応する内容表示
    newItem.addEventListener('click', () => {
        fetch('/get_item_content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ item_id: newItem.dataset.id })
        })
        .then(response => response.json())
        .then(data => {
            boardContent.textContent = data.content;  // サーバーから取得した内容を表示
        })
        .catch(error => console.error('Error:', error));
    });

    
});

document.getElementsById('insert-title-button').addEventListener('click',function(){
    const newTitle = prompt("タイトルを入力");
    if (newTitle) {
        document.getElementById("page-title").textContent = newTitle;
    }
})