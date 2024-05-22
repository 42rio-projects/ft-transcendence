class GameScreen {
  screenHeight = 600;
  screenWidth = 1200;
  gameHeight = 100;
  gameWidth = 200;

  constructor() {
    this.canvas = document.getElementById("game-screen");
    this.width = this.canvas.width = this.screenWidth;
    this.height = this.canvas.height = this.screenHeight;
    this.ctx = this.canvas.getContext("2d");
    this.rectangleHeight = this.screenHeight / 5;
    this.rectangleWidth = this.screenWidth / 100;
    this.ballRadius = this.screenWidth / 200;
  }

  draw(data) {
    this.ctx.fillStyle = "rgb(0 0 0)";
    this.ctx.fillRect(0, 0, this.width, this.height);
    this.draw_players(data);
    this.draw_ball(data);
  }

  draw_players(data) {
    this.ctx.fillStyle = "rgb(25 140 225)";
    this.ctx.fillRect(
      0,
      (data["p1"] / this.gameHeight) * this.height,
      this.rectangleWidth,
      this.rectangleHeight,
    );
    this.ctx.fillStyle = "rgb(255 128 0)";
    this.ctx.fillRect(
      this.width - this.rectangleWidth,
      (data["p2"] / this.gameHeight) * this.height,
      this.rectangleWidth,
      this.rectangleHeight,
    );
  }

  draw_ball(data) {
    this.ctx.fillStyle = "rgb(255 255 255)";
    this.ctx.beginPath();
    this.ctx.arc(
      (data["bx"] / this.gameWidth) * this.width,
      (data["by"] / this.gameHeight) * this.height,
      this.ballRadius,
      0,
      Math.PI * 2,
    );
    this.ctx.fill();
  }
}
