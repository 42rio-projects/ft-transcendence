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
    document.getElementById("chat-messages").innerHTML += html;
  }

  async sendMessage(event) {
    event.preventDefault();

    const form = event.target;
    const data = new FormData(form);
    const url = data.get("url");
    form.reset();
    let response = await fetch(url, { method: form.method, body: data });
    if (!response.ok) {
      console.error("failed to send message");
    } else {
      const json = await response.json();
      const json_string = JSON.stringify(json);
      this.socket.send(json_string);
    }
  }

  onClose(event) {}
}
