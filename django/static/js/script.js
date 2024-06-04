let localGameSocket;
let onlineGameSocket;
let messageSocket;
let localTournamentSocket;
let onlineTournamentSocket;

async function fetchData(url, options = {}) {
  options.headers = options.headers || {};
  options.headers["X-Transcendence"] = true;

  const response = await fetch(url, options);
  if (!response.ok && !response.redirected) {
    toast(`Error: ${response.status} ${response.statusText}`);
    return response;
  }

  const target_id = response.headers.get("X-Target-Id");
  const target = document.getElementById(target_id);
  if (target) {
    target.innerHTML = await response.text();
  }

  handleSockets(response.url);

  return response;
}

async function navigate(url) {
  const response = await fetchData(url);
  if (response.ok && response.url != window.location.href) {
    history.pushState({ url: response.url }, null, response.url);
  }
}

// Navigation with history (forward and back buttons)
window.addEventListener("popstate", async (event) => {
  event.preventDefault();
  await navigate(event.state ? event.state.url : window.location.href);
});

// Navigation with links (anchor tags)
document.addEventListener("click", async (event) => {
  if (event.target.tagName === "A") {
    event.preventDefault();
    await navigate(event.target.href);
  }
});

async function handleFormSubmit(event) {
  event.preventDefault();

  const form = event.target;
  const response = await fetchData(form.action, {
    method: form.method,
    body: new FormData(form),
  });

  if (response.ok && response.url != form.action) {
    history.pushState({ url: response.url }, null, response.url);
  }

  return response;
}

async function handleLogin(event) {
  const response = await handleFormSubmit(event);
  if (response.status === 200) {
    statusSocket.connect();
  }
}

async function handleLogout(url) {
  const response = await fetchData(url);
  if (response.status === 200) {
    history.pushState({ url: response.url }, null, response.url);
    statusSocket.close();
  }
}

async function toast(message) {
  const toast = document.getElementById("toast");

  const toastMessage = document.createElement("div");
  toastMessage.innerHTML = message;

  toast.appendChild(toastMessage);

  setTimeout(() => {
    toastMessage.remove();
  }, 5000);
}

function handleSockets(url) {
  if (messageSocket && messageSocket.socket.readyState === WebSocket.OPEN) {
    messageSocket.socket.close();
  } else if (
    localGameSocket &&
    localGameSocket.socket.readyState === WebSocket.OPEN
  ) {
    localGameSocket.socket.close();
  } else if (
    onlineGameSocket &&
    onlineGameSocket.socket.readyState === WebSocket.OPEN
  ) {
    onlineGameSocket.socket.close();
  } else if (
    localTournamentSocket &&
    localTournamentSocket.socket.readyState === WebSocket.OPEN
  ) {
    localTournamentSocket.socket.close();
  } else if (
    onlineTournamentSocket &&
    onlineTournamentSocket.socket.readyState === WebSocket.OPEN
  ) {
    onlineTournamentSocket.socket.close();
  }

  if (url == "/friends/") {
    statusSocket.setInitialStatus();
  } else if (url.includes("/chat/room")) {
    const regex = /\/chat\/room\/(?<id>\d+)\//;
    const match = url.match(regex);
    messageSocket = new MessageWebSocket(match.groups.id);
  } else if (url.includes("/local-game/")) {
    localGameSocket = new LocalGameWebSocket();
  } else if (url.includes("/online-game/")) {
    const regex = /\/online-game\/(?<id>\d+)\//;
    const match = url.match(regex);
    onlineGameSocket = new OnlineGameWebSocket(match.groups.id);
  } else if (url.includes("/local-tournament/")) {
    localTournamentSocket = new LocalTournamentWebSocket();
  } else if (url.includes("/online-tournament/")) {
    const regex = /\/online-tournament\/(?<id>\d+)\//;
    const match = url.match(regex);
    if (!match) return;
    onlineTournamentSocket = new OnlineTournamentWebSocket(match.groups.id);
  }
}

handleSockets(window.location.href);
