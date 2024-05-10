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
    let status = data?.status;
    if (status == "new_invite") {
      this.addInvitedPlayer(data?.["html"]);
    }
  }

  onClose(event) {}

  getStatus() {
    this.socket.send(JSON.stringify({ action: "get_status" }));
  }

  async invitePlayer(event) {
    event.preventDefault();

    const form = event.target;
    const data = new FormData(form);
    const url = data.get("url");
    form.reset();
    let response = await fetch(url, { method: form.method, body: data });
    const json = await response.json();
    let status;
    try {
      status = json["status"];
    } catch {
      console.error("Invalid Json response when inviting player");
      return;
    }
    if (status == "success") {
      console.log(json?.message);
    } else if (status == "error") {
      console.error(json?.message);
    }
  }

  addInvitedPlayer(html) {
    document.getElementById("invited-players").innerHTML += html;
  }
}
