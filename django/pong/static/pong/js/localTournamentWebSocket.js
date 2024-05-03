class LocalTournamentWebSocket {
  constructor() {
    this.socket = new WebSocket(
      "ws://" + window.location.host + "/ws/local-tournament/",
    );
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
  }

  onMessage(event) {
    const data = JSON.parse(event.data);
    const status = data["status"];
    if (status == "new_player") {
      this.addPlayer(data["html"]);
    } else if (status == "removed_player") {
      this.removePlayer(data["alias"]);
    } else if (status == "warning") {
      console.log(data["content"]);
    }
  }

  onClose(event) {}

  playerAction(event) {
    try {
      event.preventDefault();

      const form = event.target;
      const data = new FormData(form);
      const message = { action: data.get("action"), alias: data.get("alias") };
      form.reset();
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

  testMessage() {
    let message = JSON.stringify({
      test: "Hello World",
    });
    this.socket.send(message);
  }
}
