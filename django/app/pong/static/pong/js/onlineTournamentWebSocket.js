class OnlineTournamentWebSocket {
  constructor(id) {
    this.socket = new WebSocket(
      "wss://" + window.location.host + "/ws/online-tournament/" + id + "/",
    );
    this.socket.onmessage = this.onMessage.bind(this);
    this.socket.onclose = this.onClose.bind(this);
  }

  onMessage(event) {
    const data = JSON.parse(event.data);
    let status = data?.status;
    if (status == "new_invite") {
      this.addInvitedPlayer(data?.["html"]);
    } else if (status == "delete_invite") {
      this.delInvitedPlayer(data?.["id"]);
    } else if (status == "new_player") {
      this.addPlayer(data?.["html"]);
    } else if (status == "new_round") {
      this.addRound(data?.["html"]);
    } else if (status == "started" || status == "cancelled") {
      this.display(data?.["html"]);
    } else if (status == "error") {
      console.error(data?.message);
    }
  }

  onClose(event) {}

  getStatus() {
    this.socket.send(JSON.stringify({ action: "get_status" }));
  }

  async form(event) {
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
      console.error("Invalid Json response");
      return;
    }
    if (status == "success") {
      console.log(json?.message);
    } else if (status == "error") {
      console.error(json?.message);
    }
  }

  start() {
    this.socket.send(JSON.stringify({ action: "start" }));
  }

  advance() {
    this.socket.send(JSON.stringify({ action: "next_round" }));
  }

  display(html) {
    document.getElementById("tournament-display").innerHTML = html;
  }

  addPlayer(html) {
    document.getElementById("tournament-players").innerHTML += html;
  }

  addRound(html) {
    document.getElementById("tournament-rounds").innerHTML += html;
  }

  addInvitedPlayer(html) {
    document.getElementById("invited-players").innerHTML += html;
  }

  delInvitedPlayer(id) {
    document.getElementById(`invite-${id}`).remove();
  }
}
