class GameWebSocket {
  constructor() {
    this.socket = new WebSocket(
      "ws://" + window.location.host + "/ws/local-game/",
    );
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
  }

  onMessage(event) {
    const data = JSON.parse(event.data);
    console.log(data);
  }

  onClose(event) {}

  movePlayer(direction) {
    this.socket.send(JSON.stringify({ move: direction }));
  }
}
