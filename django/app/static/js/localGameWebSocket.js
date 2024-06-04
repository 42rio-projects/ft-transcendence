class LocalGameWebSocket {
  P1_UP = "w";
  P1_DOWN = "s";
  P2_UP = "ArrowUp";
  P2_DOWN = "ArrowDown";
  p1Direction = null;
  p2Direction = null;
  gameRunning = false;
  pressedKeys = {};

  constructor(tournament = null) {
    this.tournament = tournament;
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
  }

  onMessage(event) {
    const data = JSON.parse(event.data);
    if (this.gameRunning && !("status" in data)) {
      this.movePlayer();
      this.gameScreen.draw(data);
    } else if (data["status"] == "score") {
      this.updateScoreboard(data);
    } else if (data["status"] == "finished") {
      this.stop();
    } else if (data["status"] == "result") {
      this.renderResult(data["html"]);
    }
  }

  onClose(event) {
    this.stop();
  }

  start() {
    document.getElementById("local-game-start").remove();
    this.setKeyListeners();
    this.gameRunning = true;
    this.gameScreen = new GameScreen();
    this.socket.send(JSON.stringify({ start: true }));
  }

  stop() {
    this.unsetKeyListeners();
    this.gameRunning = false;
    this.socket.send(JSON.stringify({ stop: true }));
    let tournament, player1, player2;
    if (this.tournament) {
      tournament = true;
    } else {
      tournament = false;
    }
    try {
      player1 = document.getElementById("p1-alias").textContent;
      player2 = document.getElementById("p2-alias").textContent;
    } catch {
      return;
    }
    this.getResult(player1, player2, tournament);
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

  getResult(player1 = "Player1", player2 = "Player2", tournament) {
    this.socket.send(
      JSON.stringify({
        render: true,
        player1: player1,
        player2: player2,
        tournament: tournament,
      }),
    );
  }

  renderResult(html) {
    const div = document.getElementById("local-game-section");
    div.innerHTML = html;
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
