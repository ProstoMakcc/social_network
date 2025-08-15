const socket = new WebSocket(`ws://${window.location.host}/ws/posts/`);
let accessed_comments = null;

const handlers = {
  get_comments: handleComments,
};

function log(type, payload) {
  console.log(`[${type}]`, payload);
}

socket.onopen = () => log("OPEN", null);
socket.onmessage = (event) => {
  log("MESSAGE", event.data);
  const data = JSON.parse(event.data);

  if (handlers[data.action]) handlers[data.action](data.message);
  else console.warn("Невідоме сповіщення від сервера:", data.action);
};
socket.onerror = (event) => log("ERROR", event);
socket.onclose = (event) => log("CLOSE", event.code);

function handleComments(message) {
  const postpk = message.postpk;

  divId = "comments-div-" + postpk;
  const commentsDiv = document.getElementById(divId);

  const hr = document.createElement("hr");
  commentsDiv.appendChild(hr);

  for (let i = 0; i < Object.keys(message.comments).length; i++) {
    comment = message.comments[i];
    const commentAuthorDiv = document.createElement("div");
    commentAuthorDiv.classList.add("message-author");

    const commentAuthorAvatarImg = document.createElement("img");
    commentAuthorAvatarImg.classList.add("chat-profile-image", "zero-offset");
    commentAuthorAvatarImg.src = `${comment.author_avatar}`;

    const commentAuthorProfileA = document.createElement("a");
    commentAuthorProfileA.classList.add("zero-offset");
    commentAuthorProfileA.href = `/auth/profile/${comment.author_pk}`

    const commentAuthorUsernameP = document.createElement("p");
    commentAuthorUsernameP.textContent = `${comment.author_username}`;

    const commentContentP = document.createElement("p");
    commentContentP.textContent = `${comment.content}`;

    commentAuthorProfileA.appendChild(commentAuthorAvatarImg);
    commentAuthorDiv.appendChild(commentAuthorProfileA);
    commentAuthorDiv.appendChild(commentAuthorUsernameP);

    commentsDiv.appendChild(commentAuthorDiv);
    commentsDiv.appendChild(commentContentP);

    if (comment.media) {
      const commentMediaImg = document.createElement("img");
      commentMediaImg.src = `${comment.media}`;
      commentsDiv.appendChild(commentMediaImg);
    }

    const br = document.createElement("br");
    commentsDiv.append(br);
  }
  const hr2 = document.createElement("hr");

  const createCommentStrong = document.createElement("strong");
  createCommentStrong.textContent = "Create own comment:";

  const createCommentTextInput = document.createElement("input");
  createCommentTextInput.type = "text";
  createCommentTextInput.placeholder = "Почни писати...";
  createCommentTextInput.id = "text-input";

  const createCommentFileInput = document.createElement("input");
  createCommentFileInput.type = "file";
  createCommentFileInput.id = "file-input";

  const createCommentSubmitButton = document.createElement("button");
  createCommentSubmitButton.textContent = "Підтвердити";
  createCommentSubmitButton.type = "submit";
  createCommentSubmitButton.classList.add("button");
  createCommentSubmitButton.addEventListener("click", () => {
    createComment(postpk);
  });

  commentsDiv.appendChild(hr2);
  commentsDiv.appendChild(createCommentStrong);
  commentsDiv.appendChild(createCommentTextInput);
  commentsDiv.appendChild(createCommentFileInput);
  commentsDiv.appendChild(createCommentSubmitButton);

  accessed_comments = postpk;
}

function handleNewComment(message) {}

function loadComments(postpk) {
  if (accessed_comments == null) {
    socket.send(
      JSON.stringify({
        action: "get_comments",
        message: {
          postpk: postpk,
        },
      })
    );
  } else {
    if (accessed_comments == postpk) {
      divId = "comments-div-" + postpk;
      document.getElementById(divId).innerHTML = "";
      accessed_comments = null;
    } else {
      divId = "comments-div-" + accessed_comments;
      document.getElementById(divId).innerHTML = "";
      accessed_comments = null;
      loadComments(postpk);
    }
  }
}

function createComment(postpk) {
  const file = document.getElementById("file-input").files[0];
  const content = document.getElementById("text-input").value;

  if (!file) {
    socket.send(
      JSON.stringify({
        action: "create_comment",
        message: {
          postpk: postpk,
          content: content,
          media: null,
          filename: null
        },
      })
    );
    return;
  }

  const reader = new FileReader();  

  reader.onload = function (e) {
    const base64String = e.target.result.split(",")[1];

    socket.send(
      JSON.stringify({
        action: "create_comment",
        message: {
          postpk: postpk,
          content: content,
          media: base64String,
          filename: file.name
        },
      })
    );
  };

  reader.readAsDataURL(file);
}
