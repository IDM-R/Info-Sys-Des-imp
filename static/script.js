function addOpinion() {
    const opinionText = document.getElementById('new-opinion').value;
    fetch('/add_opinion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `opinion=${opinionText}`
    }).then(response => response.json())
      .then(data => {
          if (data.success) location.reload();  // 更新
      });
}

function addFeedback(index) {
    const feedbackInput = document.querySelectorAll('.feedback-input')[index];
    const feedbackText = feedbackInput.value;
    fetch('/add_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `opinion_index=${index}&feedback=${feedbackText}`
    }).then(response => response.json())
      .then(data => {
          if (data.success) location.reload();  // 更新
      });
}

function addFeedback(opinionIndex) {
    const opinionBox = document.getElementsByClassName("opinion-box")[opinionIndex];
    const feedbackInput = opinionBox.querySelector(".feedback-input");
    const feedbackText = feedbackInput.value.trim();

    if (feedbackText !== "") {
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // 新しいフィードバック要素を作成
        const newFeedback = document.createElement("textarea");
        newFeedback.className = "feedback";
        newFeedback.readOnly = true;
        newFeedback.value = `${feedbackText} [${timestamp}]`;

        // フィードバックセクションに追加
        opinionBox.querySelector(".feedback-section").appendChild(newFeedback);

        // 入力エリアをクリア
        feedbackInput.value = "";
    }
}

