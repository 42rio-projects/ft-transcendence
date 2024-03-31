class StatusWebSocket {
  constructor() {
    this.onlineUsers = [];
    this.socket = new WebSocket("ws://" + window.location.host + "/ws/status/");
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
  }

  onMessage(event) {
    const data = JSON.parse(event.data);
    if ("connected_user" in data) {
      this.setOnline(data["connected_user"]);
    } else if ("disconnected_user" in data) {
      this.setOffline(data["disconnected_user"]);
    } else {
      this.onlineUsers = data["online_users"];
      this.setInitialStatus();
    }
  }

  onClose(event) {}

  setInitialStatus() {
    let frienlistIsRendered = document.getElementById("Friendlist");
    if (!frienlistIsRendered) return;
    this.onlineUsers.forEach((element) => {
      try {
        document.getElementById(element).textContent = "ON";
      } catch (e) {
        console.log(e);
      }
    });
  }

  setOnline(user) {
    this.onlineUsers.push(user);
    let frienlistIsRendered = document.getElementById("Friendlist");
    if (!frienlistIsRendered) return;
    try {
      document.getElementById(user).textContent = "ON";
    } catch (e) {
      console.log(e);
    }
  }

  setOffline(user) {
    this.onlineUsers.splice(this.onlineUsers.indexOf(user));
    let frienlistIsRendered = document.getElementById("Friendlist");
    if (!frienlistIsRendered) return;
    try {
      document.getElementById(user).textContent = "OFF";
    } catch (e) {
      console.log(e);
    }
  }
}

const statusSocket = new StatusWebSocket();
