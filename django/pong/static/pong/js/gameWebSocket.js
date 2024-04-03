class GameWebSocket {
  P1_UP = "w";
  P1_DOWN = "s";
  P2_UP = "ArrowUp";
  P2_DOWN = "ArrowDown";
  keyDownListener = null;
  keyUpListener = null;
  p1Direction = null;
  p2Direction = null;
  gameRunning = false;

  constructor() {
    this.socket = new WebSocket(
      "ws://" + window.location.host + "/ws/local-game/",
    );
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
    this.handleKeyUp = this.handleKeyUp.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
  }

  onMessage(event) {
    const data = JSON.parse(event.data);
    if (this.gameRunning && !("status" in data)) {
      this.movePlayer();
      console.log(data);
    } else if (data["status"] == "invalid") {
      console.error(data["message"]);
    }
  }

  onClose(event) {
    this.unsetKeyListeners();
    this.gameRunning = false;
  }

  movePlayer() {
    if (!this.p1Direction && !this.p2Direction) {
      return;
    }
    let message = JSON.stringify({
      l: this.p1Direction,
      r: this.p2Direction,
    });
    this.socket.send(message);
  }

  gameAction(action) {
    let message;
    if (action == "start") {
      message = JSON.stringify({
        start: true,
      });
      this.setKeyListeners();
      this.gameRunning = true;
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

    if (!this.p1Direction) {
      if (keyPressed === this.P1_UP) {
        this.p1Direction = "u";
        return;
      } else if (keyPressed === this.P1_DOWN) {
        this.p1Direction = "d";
        return;
      }
    }
    if (!this.p2Direction) {
      if (keyPressed === this.P2_UP) {
        this.p2Direction = "u";
        return;
      } else if (keyPressed === this.P2_DOWN) {
        this.p2Direction = "d";
        return;
      }
    }
  }

  handleKeyUp(event) {
    let keyPressed = event.key;

    if (keyPressed === this.P1_DOWN || keyPressed === this.P1_UP) {
      this.p1Direction = null;
    } else if (keyPressed === this.P2_DOWN || keyPressed === this.P2_UP) {
      this.p2Direction = null;
    }
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
