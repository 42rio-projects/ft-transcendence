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
    console.log(data);
  }

  onClose(event) {}

  testMessage() {
    let message = JSON.stringify({
      test: "Hello World",
    });
    this.socket.send(message);
  }
}
