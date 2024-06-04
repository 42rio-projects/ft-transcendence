let retries = 0;
const maxRetries = 5;

class StatusWebSocket {
  constructor() {
    this.socket = new WebSocket("wss://" + window.location.host + "/ws/status/");
    this.bind();
  }

  bind() {
    this.socket.onopen = this.onOpen.bind(this);
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
  }

  onOpen() {
    this.loggedIn = true;
  }

  onMessage(event) {
    const data = JSON.parse(event.data);

    if (data.type === "user.status") {
      this.setUserStatus(data);
    } else if (data.type === "no.login") {
      this.loggedIn = false;
    }
  }

  onClose() {
    if (this.loggedIn && retries < maxRetries) {
      retries++;

      setTimeout(() => {
        this.socket = new WebSocket(
          "ws://" + window.location.host + "/ws/status/",
        );
        this.bind();
      }, retries * 3000); // 3s
    }
  }

  connect() {
    this.socket = new WebSocket("wss://" + window.location.host + "/ws/status/");
    this.bind();
  }

  close() {
    this.loggedIn = false;
    this.socket.close();
  }

  setUserStatus(data) {
    const element = document.getElementById(`${data.user_pk}-status`);
    if (element) {
      element.innerHTML = data.user_status;
    }
    const circle = document.getElementById(`${data.user_pk}-status-icon`);
    if (circle) {
      data.user_status === "Online"
        ? (circle.className = "online-icon")
        : (circle.className = "offline-icon");
    }
  }
}

const statusSocket = new StatusWebSocket();
