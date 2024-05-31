const maxRetries = 5;

class StatusWebSocket {
  constructor() {
    this.socket = new WebSocket("ws://" + window.location.host + "/ws/status/");
    this.bind();
  }

  bind() {
    this.socket.onopen = this.onOpen.bind(this);
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
  }

  onOpen() {
    this.loggedIn = true;
    console.log("Status WebSocket connected");
  }

  onMessage(event) {
    const data = JSON.parse(event.data);

    console.log(data);

    if (data.type === "user.status") {
      this.setUserStatus(data);
    }
  }

  onClose() {
    let retries = 0;

    while (this.loggedIn && retries < maxRetries) {
      retries++;
      console.log(`Trying to reconnect... Attempt ${retries}`);

      setTimeout(() => {
        this.socket = new WebSocket(
          "ws://" + window.location.host + "/ws/status/"
        );
        this.bind();
      }, retries * 3000); // 3s
    }
  }

  connect() {
    this.socket = new WebSocket("ws://" + window.location.host + "/ws/status/");
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
        data.user_status === "Online" ? circle.className = "online-icon" : circle.className = "offline-icon";
      }
  }
}

const statusSocket = new StatusWebSocket();
