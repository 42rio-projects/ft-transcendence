class MessageWebSocket {
  constructor(id) {
    this.onlineUsers = [];
    this.socket = new WebSocket(
      "ws://" + window.location.host + "/ws/chat/" + id + "/",
    );
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
  }

  async onMessage(event) {
    const data = JSON.parse(event.data);
    const message_id = data.id;
    const response = await fetch("/message/" + message_id + "/");
    const html = await response.text();
    const container = document.querySelector(".renderChat");
    container.innerHTML += html;
  }

  async sendMessage(event) {
    try {
      event.preventDefault();

      const form = event.target;
      const data = new FormData(form);
      const url = data.get("url");
      form.reset();
      let response = await fetch(url, { method: form.method, body: data });
      const jsonResponse = await response.json();
      const status = jsonResponse["status"];
      if (status == "success") {
        const jsonString = JSON.stringify(jsonResponse);
        this.socket.send(jsonString);
      } else {
        this.displayWarning(jsonResponse["msg"]);
      }
    } catch (error) {
      console.log(error);
    }
  }
  onClose(event) {}

  displayWarning(warning) {
    const warningElement = document.getElementById("chat-warning");
    if (warningElement.textContent === "") {
      warningElement.textContent = warning;
      setTimeout(() => {
        warningElement.textContent = "";
      }, 1500);
    }
  }
}

