class LocalTournamentWebSocket {
  constructor() {
    this.socket = new WebSocket(
      "ws://" + window.location.host + "/ws/local-tournament/",
    );
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
    this.gameSocket = null;
  }

  onMessage(event) {
    const data = JSON.parse(event.data);
    const status = data["status"];
    if (status == "new_player") {
      this.addPlayer(data["html"]);
    } else if (status == "removed_player") {
      this.removePlayer(data["alias"]);
    } else if (status == "started") {
      this.removeFormationMenu();
    } else if (status == "next_game") {
      this.renderGame(data["html"]);
    } else if (status == "start_game") {
      this.startGame();
    } else if (status == "warning") {
      console.log(data["content"]);
    }
  }

  onClose(event) {
    if (this.gameSocket) {
      this.gameSocket.socket.close();
    }
  }

  playerAction(event) {
    try {
      event.preventDefault();

      const form = event.target;
      const data = new FormData(form);
      const message = {
        user_action: data.get("user_action"),
        alias: data.get("alias"),
      };
      form.reset();
      this.socket.send(JSON.stringify(message));
    } catch (error) {
      console.log(error);
    }
  }

  tournamentAction(event) {
    try {
      event.preventDefault();

      const form = event.target;
      const data = new FormData(form);
      const message = { user_action: data.get("user_action") };
      this.socket.send(JSON.stringify(message));
    } catch (error) {
      console.log(error);
    }
  }

  addPlayer(html) {
    const player_list = document.getElementById("tournament-players");
    player_list.innerHTML += html;
  }

  removePlayer(alias) {
    let player = document.getElementById(`tournament_player_${alias}`);
    player.remove();
  }

  removeFormationMenu() {
    let menu = document.getElementById("formation-menu");
    menu.remove();
  }

  renderGame(html) {
    if (!this.gameSocket) {
      this.gameSocket = new LocalGameWebSocket(this);
    }
    const game = document.getElementById("game-section");
    game.innerHTML = html;
  }

  startGame() {
    if (this.gameSocket) {
      this.gameSocket.start();
    }
  }

  nextGame(winner) {
    const message = { user_action: "next_game", winner: winner };
    this.socket.send(JSON.stringify(message));
  }
}
