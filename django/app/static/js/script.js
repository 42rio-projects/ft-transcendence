let localGameSocket;
let onlineGameSocket;
let messageSocket;
let localTournamentSocket;
let onlineTournamentSocket;

// Fetches with X-Transcendence header
// inserts response HTML into target element
// returns response URL for history navigation
async function fetchData(
  url,
  { method, body } = { method: "GET", body: null },
) {
  const response = await fetch(url, {
    headers: {
      "X-Transcendence": true,
    },
    method,
    body,
  });

  const target_id = response.headers.get("X-Target-Id");
  const html = await response.text();

  document.getElementById(target_id).innerHTML = html;

  handleSockets(response.url);

  return response;
}

function handleFormSubmit(event) {
  event.preventDefault();

  const form = event.target;

  fetchData(form.action, {
    method: form.method,
    body: new FormData(form),
  })
    .then((response) => {
      // If the form returns a different URL, update the history
      if (response.url !== form.action) {
        history.pushState({ url: response.url }, null, response.url);
      }
    })
    .catch((error) => console.error(error));
}

// Navigation with history (forward and back buttons)
function handleNavigation(event) {
  const url = event.state ? event.state.url : window.location.href;

  fetchData(url).catch((error) => console.error(error));
}

window.addEventListener("popstate", handleNavigation);

// Navigation with links (anchor tags)
function handleLinkClick(event) {
  event.preventDefault();

  const url = event.target.href;

  fetchData(url)
    .then((response) => {
      history.pushState({ url: response.url }, null, response.url);
    })
    .catch((error) => console.error(error));
}

document.addEventListener("click", (event) => {
  if (event.target.tagName === "A") {
    handleLinkClick(event);
  }
});

async function handleLogin(event) {
  event.preventDefault();

  const form = event.target;

<<<<<<< HEAD:django/app/static/js/script.js
  constructor() {
    this.socket = new WebSocket(
      "wss://" + window.location.host + "/ws/local-game/",
    );
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
    this.handleKeyUp = this.handleKeyUp.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.pressedKeys[this.P1_UP] = false;
    this.pressedKeys[this.P2_UP] = false;
    this.pressedKeys[this.P1_DOWN] = false;
    this.pressedKeys[this.P2_DOWN] = false;
=======
  const response = await fetchData(form.action, {
    method: form.method,
    body: new FormData(form),
  });

  if (response.status === 200) {
    const params = new URLSearchParams(window.location.search);
    const next = params.get("next") || "/";

    history.pushState({ url: next }, null, next);

    statusSocket.connect();
>>>>>>> develop:django/static/js/script.js
  }
}

async function handleLogout(event) {
  event.preventDefault();

  const response = await fetch("/logout/")

  if (response.status === 200) {
    statusSocket.close();
    await fetchData("/");
    history.pushState({ url: "/" }, null, "/");
  }
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

  console.log("Url: " + url);

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
