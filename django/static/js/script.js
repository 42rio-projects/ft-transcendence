let localGameSocket;
let onlineGameSocket;
let messageSocket;
let localTournamentSocket;

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

  return response.url;
}

function handleFormSubmit(event) {
  event.preventDefault();

  const form = event.target;

  fetchData(form.action, {
    method: form.method,
    body: new FormData(form),
  })
    .then((response_url) => {
      // If the form returns a different URL, update the history
      console.log(response_url);
      if (response_url !== form.action) {
        history.pushState({ url: response_url }, null, response_url);
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
    .then((response_url) => {
      history.pushState({ url: response_url }, null, response_url);
    })
    .catch((error) => console.error(error));
}

document.addEventListener("click", (event) => {
  if (event.target.tagName === "A") {
    handleLinkClick(event);
  }
});

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
  }

  console.log("Url: " + url);

  if (url == "/friends/") {
    statusSocket.setInitialStatus();
  } else if (url.includes("/chat/room")) {
    const regex = /\/chat\/room\/(?<id>\d+)\//;
    const match = url.match(regex);
    messageSocket = new MessageWebSocket(match.groups.id);
  } else if (url.includes("/local-game/")) {
    console.log("Creating localGameSocket");
    localGameSocket = new LocalGameWebSocket();
  } else if (url.includes("/online-game/")) {
    const regex = /\/online-game\/(?<id>\d+)\//;
    const match = url.match(regex);
    onlineGameSocket = new OnlineGameWebSocket(match.groups.id);
  } else if (url.includes("/local-tournament/")) {
    console.log("Creating localGameSocket");
    localTournamentSocket = new LocalTournamentWebSocket();
  }
}

handleSockets(window.location.href);
