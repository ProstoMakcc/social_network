const socket = new WebSocket(`ws://${window.location.host}/ws/chat/`);

const handlers = {
  user_suggestions: handleUserSuggestions,
  new_chat: handleNewChat,
  get_messages: handleGetMessages,
  typing_status: handleTypingStatus,
  new_message: handleNewMessage,
};

let current_chat = null;
let last_message_author = null;
let timer_id = null;
let typing_status_chat = null;

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

function handleUserSuggestions(message) {
  userSuggestions = message.users;
  const userSuggestionsDropdown = document.getElementById(
    "user-suggestions-dropdown"
  );

  for (let i = 0; i < userSuggestions.length; i++) {
    const userSuggestionOption = document.createElement("option");
    userSuggestionOption.value = `${userSuggestions[i].pk}`;
    userSuggestionOption.textContent = `${userSuggestions[i].username}`;

    userSuggestionsDropdown.appendChild(userSuggestionOption);
  }
}

function handleNewChat(message) {
  chat = message["chat"];

  const chatPlateDiv = document.createElement("div");
  chatPlateDiv.classList.add("chat-plate");
  chatPlateDiv.addEventListener("click", () => selectChat(`${chat.pk}`));

  const chatNameP = document.createElement("p");
  chatNameP.textContent = `${chat.name}`;

  const chatLastMessageP = document.createElement("p");
  chatLastMessageP.id = `last-message-id-${chat.pk}`;
  chatLastMessageP.textContent = `${chat.pk}`;

  chatPlateDiv.appendChild(chatNameP);
  chatPlateDiv.appendChild(chatLastMessageP);

  const chatList = document.getElementById("chat-list");
  chatList.prepend(chatPlateDiv);
}

function handleGetMessages(message) {
  const chatWindow = document.getElementById("chat-window");
  chatWindow.innerHTML = "";
  messages = message.messages;
  lastMessageAuthor = messages[messages.length - 1].author;

  for (let i = 0; i < messages.length; i++) {
    if (lastMessageAuthor == messages[i].author) {
      const messageContentP = document.createElement("p");
      messageContentP.textContent = `${messages[i].content}`;

      chatWindow.appendChild(messageContentP);
    } else {
      const br = document.createElement("br");

      const messageAuthorDiv = document.createElement("div");
      messageAuthorDiv.classList.add("message-author", "zero-offset");

      const messageAuthorAvatarImg = document.createElement("img");
      messageAuthorAvatarImg.classList.add("chat-profile-image");
      messageAuthorAvatarImg.src = `${messages[i].author_avatar}`;

      const messageAuthorProfileA = document.createElement("a");
      messageAuthorProfileA.classList.add("zero-offset");
      messageAuthorProfileA.href = `/auth/profile/${messages[i].author_pk}`;

      const messageAuthorUsernameStrong = document.createElement("strong");
      messageAuthorUsernameStrong.textContent = `${messages[i].author}`;

      const messageContentP = document.createElement("p");
      messageContentP.textContent = `${messages[i].content}`;

      messageAuthorProfileA.appendChild(messageAuthorAvatarImg);
      messageAuthorDiv.appendChild(messageAuthorProfileA);
      messageAuthorDiv.appendChild(messageAuthorUsernameStrong);

      chatWindow.appendChild(br);
      chatWindow.appendChild(messageAuthorDiv);
      chatWindow.appendChild(messageContentP);

      lastMessageAuthor = messages[i].author;
    }
  }

  document.getElementById("chat-input").hidden = false;
  document.getElementById("currently-typing-list").hidden = false;
  document.getElementById("chat-window").scrollTop =
    document.getElementById("chat-window").scrollHeight;
}

function handleTypingStatus(message) {
  if (current_chat != message.chatpk) return;
  const currentlyTypingList = document.getElementById("currently-typing-list");
  const currentlyTypingUserP = document.createElement("p");

  currently_typing_user = message.user;

  if (message.typing_status == true)
    currentlyTypingUserP.textContent = `${currently_typing_user.username} пише...`;
  else currentlyTypingUserP.textContent = ``;

  currentlyTypingList.replaceChild(
    currentlyTypingUserP,
    currentlyTypingList.firstChild
  );
}

function handleNewMessage(message) {
  new_message = message.new_message;
  const chatLastMessage = document.getElementById(
    `last-message-id-${new_message.chat}`
  );
  const chatWindow = document.getElementById(`chat-window`);

  last_message_text = message.new_message.content;
  if (last_message_text.length > 10)
    last_message_text = last_message_text.substring(0, 10) + "...";

  const chatLastMessageP = document.createElement("p");
  chatLastMessageP.textContent = `${last_message_text}`;

  chatLastMessage.replaceChild(chatLastMessageP, chatLastMessage.firstChild);

  if (new_message.author == last_message_author) {
    const newMessageContentP = document.createElement("p");
    newMessageContentP.textContent = `${new_message.content}`;

    chatWindow.appendChild(newMessageContentP);
  } else {
    const br = document.createElement("br");

    const messageAuthorDiv = document.createElement("div");
    messageAuthorDiv.classList.add("message-author");

    const messageAuthorAvatarImg = document.createElement("img");
    messageAuthorAvatarImg.classList.add("chat-profile-image");
    messageAuthorAvatarImg.src = `${new_message.author_avatar}`;

    const messageAuthorProfileA = document.createElement("a");
    messageAuthorProfileA.classList.add("zero-offset");
    messageAuthorProfileA.href = `/auth/profile/${author_pk}`;

    const messageAuthorUsernameStrong = document.createElement("strong");
    messageAuthorUsernameStrong.textContent = `${new_message.author}`;

    const messageContentP = document.createElement("p");
    messageContentP.textContent = `${new_message.content}`;

    messageAuthorProfileA.appendChild(messageAuthorAvatarImg);
    messageAuthorDiv.appendChild(messageAuthorProfileA);
    messageAuthorDiv.appendChild(messageAuthorUsernameStrong);

    chatWindow.append(br);
    chatWindow.appendChild(messageAuthorDiv);
    chatWindow.appendChild(messageContentP);
  }
  last_message_author = new_message.author;
  document.getElementById("chat-window").scrollTop =
    document.getElementById("chat-window").scrollHeight;
}

function showSuggestions(username) {
  socket.send(
    JSON.stringify({
      action: "user_suggestions",
      message: {
        username: username,
      },
    })
  );
}

function createChat() {
  socket.send(
    JSON.stringify({
      action: "create_chat",
      message: {
        participant_pk: document.getElementById("user-suggestions-dropdown")
          .value,
      },
    })
  );
}

function selectChat(chatpk) {
  socket.send(
    JSON.stringify({
      action: "get_messages",
      message: {
        chatpk: chatpk,
      },
    })
  );
  current_chat = chatpk;
  sendTypingStatus(false, typing_status_chat);
  typing_status_chat = chatpk;
}

function newMessage() {
  socket.send(
    JSON.stringify({
      action: "new_message",
      message: {
        chatpk: current_chat,
        content: document.getElementById("text-input").value,
      },
    })
  );
  document.getElementById("text-input").value = "";
}

function sendTypingStatus(typing_status, chat = current_chat) {
  socket.send(
    JSON.stringify({
      action: "typing_status",
      message: {
        chatpk: chat,
        typing_status: typing_status,
      },
    })
  );
}

function setTimer() {
  if (timer_id != null) clearTimeout(timer_id);
  timer_id = setTimeout(() => {
    sendTypingStatus(false);
  }, 2000);
}
