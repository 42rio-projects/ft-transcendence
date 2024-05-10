class OnlineTournamentWebSocket {
  constructor(id) {
    this.socket = new WebSocket(
      "ws://" + window.location.host + "/ws/online-tournament/" + id + "/",
    );
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
  }

  onMessage(event) {
    const data = JSON.parse(event.data);
    console.log(data);
  }

  onClose(event) {}

  getStatus() {
    this.socket.send(JSON.stringify({ action: "get_status" }));
  }
}
