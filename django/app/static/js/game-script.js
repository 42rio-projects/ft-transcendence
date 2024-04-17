var width = 800;
var height = 400;
var pi = Math.PI;
var UpArrow = 38;
var DownArrow = 40;
var canvas, ctx, keystate, player, ai, ball;

player = {
  x: null,
  y: null,
  height: 100,
  width: 20,
  playerScore: 0,
  
  update: function() {
    if (keystate[UpArrow] && this.y > 0) this.y -= 7;
    if (keystate[DownArrow] && (this.y + this.height) < height) this.y += 7;
  },
  
  draw: function() {
    ctx.fillRect(this.x, this.y, this.width, this.height);
  }
};

ai = {
  x: null,
  y: null,
  height: 100,
  width: 20,
  aiScore: 0,
  
  update: function() {
    let ballPos = (ball.y + (ball.side/2) - (this.height / 2));
    if (ballPos > this.y) {
      this.y += 1.5;
    } else if (ballPos < this.y) {
      this.y -= 1.5;
    }
  },
  
  draw: function() {
    ctx.fillRect(this.x, this.y, this.width, this.height);
  }
};

ball = {
  x: null,
  y: null,
  vel: null,
  speed: 2,    // mude a velocidade da bola aqui querido.
  side: 20,
  
  update: function() {
    this.x += this.vel.x;
    this.y += this.vel.y;
    
    if (0 > this.y || this.y + this.side > height) {
      this.vel.y *= -1;
    }
    
    var shouldBounce = function(ax, ay, aw, ah, bx, by, bw, bh) {
      return ax < bx+bw && ay < by+bh && bx < ax+aw && by < ay+ah;
    };
    
    var padel = this.vel.x < 0 ? player : ai;
    if (shouldBounce(padel.x, padel.y, padel.width, padel.height, this.x, this.y, this.side, this.side)) {
      let whereHit = (this.y + this.side - padel.y) / (padel.height + this.side);
      let phi = .25 * pi * (2 * whereHit - 1);
      this.vel.x = (padel === player ? 1 : -1) * this.speed * Math.cos(phi);
      this.vel.y = this.speed * Math.sin(phi);
    }
    if (this.x < 0) {
      ai.aiScore++;
      ballReset();
    }
    if (this.x > canvas.width) {
      player.playerScore++;
      ballReset();
    }
  },
  
  draw: function() {
    ctx.fillRect(this.x, this.y, this.side, this.side);
  }
};

function trackGameTime() {
  var startTime = new Date().getTime(); // Tempo inicial

  // Atualiza a cada segundo
  setInterval(function() {
      var currentTime = new Date().getTime();
      var elapsedTimeInSeconds = Math.floor((currentTime - startTime) / 1000);

      // Calcula minutos e segundos
      var minutes = Math.floor(elapsedTimeInSeconds / 60);
      var seconds = elapsedTimeInSeconds % 60;

      // Atualiza o elemento com o tempo decorrido
      document.getElementById('timer').textContent = formatTime(minutes, seconds);
  }, 1000);
}

function formatTime(minutes, seconds) {
  return pad(minutes) + ':' + pad(seconds);
}

function pad(number) {
  return (number < 10 ? '0' : '') + number;
}

function main() {
  canvas = document.getElementById('canvas');
  canvas.width = width;
  canvas.height = height;
  ctx = canvas.getContext('2d');
  trackGameTime();
  
  keystate = {};
  document.addEventListener('keydown', (evt) => {
    keystate[evt.keyCode] = true;
  });
  document.addEventListener('keyup', (evt) => {
    delete keystate[evt.keyCode];
  });
  
  init();
  
  var loop = function() {
    update();
    draw();
    
    window.requestAnimationFrame(loop, canvas);
  };
  
  window.requestAnimationFrame(loop, canvas);
}

function init() {
  timer = 0;

  player.playerScore = 0;
  player.x = player.width;
  player.y = (height - player.height) / 2;
  
  ai.aiScore = 0;
  ai.x = width - (player.width + ai.width);
  ai.y = (height - ai.height) / 2;
  
  ball.x = (width - ball.side) / 2;
  ball.y = (height - ball.side) / 2;
  ball.vel = {
    x: ball.speed,
    y: 0
  };
}

function update() {
  player.update();
  ai.update();
  ball.update();
}

function draw() {
  ctx.fillRect(0, 0, width, height);
  ctx.save();
  ctx.fillStyle = '#ffffff';
  
  player.draw();
  ai.draw();
  ball.draw();
  
  let w = 4;
  let x = (width - w) * 0.5;
  let y = 0;
  let step = height/20;
  while (y < height) {
    ctx.fillRect(x, y+step*0.2, w, step*0.6);
    y += step;
  }
  
  document.getElementById("player1-score").innerText = player.playerScore;
  document.getElementById("player2-score").innerText = ai.aiScore;

  ctx.restore();
}

function ballReset() {
  ball.vel.x = -ball.vel.x;
  ball.x = canvas.width / 2;
  ball.y = canvas.height / 2;
}

main();
