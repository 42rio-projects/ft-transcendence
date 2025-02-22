class OnlineGameWebSocket {
  UP = "w";
  DOWN = "s";
  Direction = null;
  gameRunning = false;
  pressedKeys = {};

  constructor(id) {
    this.socket = new WebSocket(
      "ws://" + window.location.host + "/ws/online-game/" + id + "/",
    );
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
    this.gameRunning = false;
    this.handleKeyUp = this.handleKeyUp.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.pressedKeys[this.UP] = false;
    this.pressedKeys[this.DOWN] = false;
  }

  onMessage(event) {
    const data = JSON.parse(event.data);
    if (this.gameRunning && !("status" in data)) {
      this.movePlayer();
      this.gameScreen.draw(data);
    } else if (data["status"] == "score") {
      this.updateScoreboard(data);
    } else if (data["status"] == "started") {
      this.setKeyListeners();
      this.gameRunning = true;
      this.gameScreen = new GameScreen();
    } else if (data["status"] == "stoped") {
      this.unsetKeyListeners();
      this.gameRunning = false;
    } else if (data["status"] == "canceled") {
      this.gameRunning = false;
      this.renderResult(data["html"]);
    } else if (data["status"] == "finished") {
      this.gameRunning = false;
      this.unsetKeyListeners();
    } else if (data["status"] == "result") {
      this.renderResult(data["html"]);
    }
  }

  onClose(event) {
    this.unsetKeyListeners();
    this.gameRunning = false;
  }

  movePlayer() {
    this.getDirections();
    let message = JSON.stringify({
      d: this.Direction,
    });
    this.socket.send(message);
  }

  getDirections() {
    if (this.pressedKeys[this.UP]) {
      this.Direction = "u";
    } else if (this.pressedKeys[this.DOWN]) {
      this.Direction = "d";
    } else {
      this.Direction = null;
    }
  }

  renderResult(html) {
    const div = document.getElementById("online-game-section");
    div.innerHTML = html;
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
