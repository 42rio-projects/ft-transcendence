class GameWebSocket {
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

  onMessage(event) {
    const data = JSON.parse(event.data);
    if (this.gameRunning && !("status" in data)) {
      this.movePlayer();
      this.gameScreen.draw(data);
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
    if (!this.p1Direction && !this.p2Direction) {
      return;
    }
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

  handleKeyDown(event) {
    let keyPressed = event.key;
    this.pressedKeys[keyPressed] = true;
  }

  handleKeyUp(event) {
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
}
