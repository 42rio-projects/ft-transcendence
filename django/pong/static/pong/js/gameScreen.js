class GameScreen {
  screenHeight = 600;
  screenWidth = 1200;

  constructor() {
    this.canvas = document.getElementById("game-screen");
    this.width = this.canvas.width = this.screenWidth;
    this.height = this.canvas.height = this.screenHeight;
    this.ctx = this.canvas.getContext("2d");
    this.rectangleHeight = this.screenHeight / 5;
    this.rectangleWidth = this.screenWidth / 100;
  }

  draw(data) {
    this.ctx.fillStyle = "rgb(0 0 0)";
    this.ctx.fillRect(0, 0, this.width, this.height);
    this.ctx.fillStyle = "rgb(25 140 225)";
    this.ctx.fillRect(
      0,
      (data["p1"] / 100) * this.height,
      this.rectangleWidth,
      this.rectangleHeight,
    );
    this.ctx.fillStyle = "rgb(255 128 0)";
    this.ctx.fillRect(
      this.width - this.rectangleWidth,
      (data["p2"] / 100) * this.height,
      this.rectangleWidth,
      this.rectangleHeight,
    );
  }
}
