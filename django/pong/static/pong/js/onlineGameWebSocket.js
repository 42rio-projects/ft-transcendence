class OnlineGameWebSocket {
  constructor(id) {
    this.socket = new WebSocket(
      "ws://" + window.location.host + "/ws/online-game/" + id + "/",
    );
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
    this.gameRunning = false;
    //this.handleKeyUp = this.handleKeyUp.bind(this);
    //this.handleKeyDown = this.handleKeyDown.bind(this);
    //this.pressedKeys[this.P1_UP] = false;
    //this.pressedKeys[this.P2_UP] = false;
    //this.pressedKeys[this.P1_DOWN] = false;
    //this.pressedKeys[this.P2_DOWN] = false;
  }

  gameAction(action) {
    let message;
    if (action == "start") {
      message = JSON.stringify({
        start: true,
      });
    } else {
      message = JSON.stringify({
        stop: true,
      });
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
    } else if (data["status"] == "started") {
      //this.setKeyListeners();
      this.gameRunning = true;
      this.gameScreen = new GameScreen();
    } else if (data["status"] == "stoped") {
      //this.unsetKeyListeners();
      this.gameRunning = false;
    } else if (data["status"] == "canceled") {
      console.log("Game canceled");
      this.gameRunning = false;
    }
  }

  onClose(event) {
    //this.unsetKeyListeners();
    //this.gameRunning = false;
  }

  movePlayer() {
    return;
    //this.getDirections();
    //let message = JSON.stringify({
    //  l: this.p1Direction,
    //  r: this.p2Direction,
    //});
    //this.socket.send(message);
  }

  //getDirections() {
  //  if (this.pressedKeys[this.P1_UP]) {
  //    this.p1Direction = "u";
  //  } else if (this.pressedKeys[this.P1_DOWN]) {
  //    this.p1Direction = "d";
  //  } else {
  //    this.p1Direction = null;
  //  }
  //  if (this.pressedKeys[this.P2_UP]) {
  //    this.p2Direction = "u";
  //  } else if (this.pressedKeys[this.P2_DOWN]) {
  //    this.p2Direction = "d";
  //  } else {
  //    this.p2Direction = null;
  //  }
  //}

  //handleKeyDown(event) {
  //  event.preventDefault();
  //  let keyPressed = event.key;
  //  this.pressedKeys[keyPressed] = true;
  //}

  //handleKeyUp(event) {
  //  event.preventDefault();
  //  let keyPressed = event.key;
  //  this.pressedKeys[keyPressed] = false;
  //}

  //setKeyListeners() {
  //  document.addEventListener("keydown", this.handleKeyDown);
  //  document.addEventListener("keyup", this.handleKeyUp);
  //}

  //unsetKeyListeners() {
  //  document.removeEventListener("keydown", this.handleKeyDown);
  //  document.removeEventListener("keyup", this.handleKeyUp);
  //}

  updateScoreboard(data) {
    document.getElementById("p1-score").innerHTML = data["p1"];
    document.getElementById("p2-score").innerHTML = data["p2"];
  }
}
