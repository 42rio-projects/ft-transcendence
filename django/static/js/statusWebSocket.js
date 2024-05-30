class StatusWebSocket {
  constructor() {
    this.socket = new WebSocket("ws://" + window.location.host + "/ws/status/");
    this.socket.onmessage = this.onMessage.bind(this);
  }

  onMessage(event) {
    const data = JSON.parse(event.data);

    console.log(data);

    if (data.type === "user.status") {
      this.setUserStatus(data)
    }
  }

  close() {
    this.socket.close();
  }

  setUserStatus(data) {
    const element = document.getElementById(`${data.user_pk}-status`);
    if (element) {
      element.innerHTML = data.user_status;
    }
  }
}

const statusSocket = new StatusWebSocket();
