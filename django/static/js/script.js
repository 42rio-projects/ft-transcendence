// Fetches with X-Transcendence header
// inserts response HTML into target element
// returns response URL for history navigation
async function fetchData(
  url,
  { method, body } = { method: "GET", body: null }
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

let localGameSocket;
let onlineGameSocket;
let messageSocket;

class LocalGameWebSocket {
  P1_UP = "w";
  P1_DOWN = "s";
  P2_UP = "ArrowUp";
  P2_DOWN = "ArrowDown";
  p1Direction = null;
  p2Direction = null;
  gameRunning = false;
  pressedKeys = {};

  constructor() {
    this.socket = new WebSocket(
      "ws://" + window.location.host + "/ws/local-game/",
    );
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
    this.handleKeyUp = this.handleKeyUp.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.pressedKeys[this.P1_UP] = false;
    this.pressedKeys[this.P2_UP] = false;
    this.pressedKeys[this.P1_DOWN] = false;
    this.pressedKeys[this.P2_DOWN] = false;
  }

  gameAction(action) {
    let message;
    if (action == "start") {
      message = JSON.stringify({
        start: true,
      });
      this.setKeyListeners();
      this.gameRunning = true;
      this.gameScreen = new GameScreen();
    } else {
      message = JSON.stringify({
        stop: true,
      });
      this.unsetKeyListeners();
      this.gameRunning = false;
    }
    this.socket.send(message);
  }

  onMessage(event) {
    const data = JSON.parse(event.data);
    if (this.gameRunning && !("status" in data)) {
      this.movePlayer();
      this.gameScreen.draw(data);
    } else if (data["status"] == "score") {
      this.updateScoreboard(data);
    } else if (data["status"] == "invalid") {
      console.error(data["message"]);
    }
  }

  onClose(event) {
    this.unsetKeyListeners();
    this.gameRunning = false;
  }

  movePlayer() {
    this.getDirections();
    let message = JSON.stringify({
      l: this.p1Direction,
      r: this.p2Direction,
    });
    this.socket.send(message);
  }

  getDirections() {
    if (this.pressedKeys[this.P1_UP]) {
      this.p1Direction = "u";
    } else if (this.pressedKeys[this.P1_DOWN]) {
      this.p1Direction = "d";
    } else {
      this.p1Direction = null;
    }
    if (this.pressedKeys[this.P2_UP]) {
      this.p2Direction = "u";
    } else if (this.pressedKeys[this.P2_DOWN]) {
      this.p2Direction = "d";
    } else {
      this.p2Direction = null;
    }
  }

  handleKeyDown(event) {
    event.preventDefault();
    let keyPressed = event.key;
    this.pressedKeys[keyPressed] = true;
  }

  handleKeyUp(event) {
    event.preventDefault();
    let keyPressed = event.key;
    this.pressedKeys[keyPressed] = false;
  }

  setKeyListeners() {
    document.addEventListener("keydown", this.handleKeyDown);
    document.addEventListener("keyup", this.handleKeyUp);
  }

  unsetKeyListeners() {
    document.removeEventListener("keydown", this.handleKeyDown);
    document.removeEventListener("keyup", this.handleKeyUp);
  }

  updateScoreboard(data) {
    document.getElementById("p1-score").innerHTML = data["p1"];
    document.getElementById("p2-score").innerHTML = data["p2"];
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
  }

  console.log("Url: " + url)

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
  }
}

handleSockets(window.location.href);
