const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const overlay = document.getElementById('gameOverOverlay');

const player = {
  x: 60,
  y: canvas.height / 2,
  width: 16,
  height: 90,
  speed: 7,
};

const robot = {
  x: canvas.width - 76,
  y: canvas.height / 2,
  width: 16,
  height: 90,
  speed: 5.2,
  cooldown: 0,
};

const ball = {
  x: canvas.width / 2,
  y: canvas.height / 2,
  radius: 10,
  vx: 4.4,
  vy: 2.3,
};

const keys = {
  up: false,
  down: false,
  left: false,
  right: false,
  space: false,
};

let score = 0;
let gameOver = false;
let lastTime = 0;

function resetBall(direction = -1) {
  ball.x = canvas.width / 2;
  ball.y = canvas.height / 2;
  ball.vx = direction * (4.4 + Math.random() * 0.7);
  ball.vy = (Math.random() - 0.5) * 3.8;
}

function showGameOver() {
  gameOver = true;
  overlay.classList.remove('hidden');
}

function attemptPlayerHit() {
  if (gameOver) return;

  const nearPaddle =
    ball.x - ball.radius <= player.x + player.width + 4 &&
    ball.x + ball.radius >= player.x - 4 &&
    ball.y >= player.y - ball.radius &&
    ball.y <= player.y + player.height + ball.radius;

  if (nearPaddle) {
    score += 1;
    scoreEl.textContent = score;
    ball.vx = Math.abs(ball.vx) * 1.06 + 0.5;
    ball.vy = (Math.random() - 0.5) * 3.6;
    ball.x = player.x + player.width + ball.radius + 2;
  } else {
    showGameOver();
  }
}

function updateRobot(delta) {
  if (gameOver) return;

  if (robot.cooldown > 0) {
    robot.cooldown -= delta;
  }

  if (ball.vx > 0 && ball.x > canvas.width * 0.62 && robot.cooldown <= 0) {
    const targetY = ball.y - robot.height / 2;
    robot.y += Math.sign(targetY - robot.y) * Math.min(robot.speed * 1.4, Math.abs(targetY - robot.y));
    robot.cooldown = 0.9 + Math.random() * 0.6;

    ball.vx = -Math.abs(ball.vx) * 1.04 - 0.4;
    ball.vy = (Math.random() - 0.5) * 4.2;
    ball.x = robot.x - ball.radius - 2;
  } else {
    const targetY = ball.y - robot.height / 2;
    robot.y += Math.sign(targetY - robot.y) * Math.min(robot.speed * delta * 60, Math.abs(targetY - robot.y));
  }

  robot.y = Math.max(0, Math.min(canvas.height - robot.height, robot.y));
}

function updatePlayer() {
  if (keys.left) {
    player.x -= player.speed;
  }
  if (keys.right) {
    player.x += player.speed;
  }
  if (keys.up) {
    player.y -= player.speed;
  }
  if (keys.down) {
    player.y += player.speed;
  }
  player.x = Math.max(0, Math.min(canvas.width / 2 - player.width, player.x));
  player.y = Math.max(0, Math.min(canvas.height - player.height, player.y));
}

function updateBall(delta) {
  if (gameOver) return;

  ball.x += ball.vx * delta * 60;
  ball.y += ball.vy * delta * 60;

  if (ball.y - ball.radius <= 0 || ball.y + ball.radius >= canvas.height) {
    ball.vy *= -1;
    ball.y = Math.max(ball.radius, Math.min(canvas.height - ball.radius, ball.y));
  }

  if (ball.x - ball.radius <= 0) {
    showGameOver();
    return;
  }

  if (ball.x + ball.radius >= canvas.width) {
    showGameOver();
    return;
  }

  const playerHit =
    ball.vx < 0 &&
    ball.x - ball.radius <= player.x + player.width &&
    ball.x + ball.radius >= player.x &&
    ball.y >= player.y &&
    ball.y <= player.y + player.height;

  if (playerHit) {
    if (keys.space) {
      attemptPlayerHit();
    } else {
      showGameOver();
    }
    return;
  }

  const robotHit =
    ball.vx > 0 &&
    ball.x + ball.radius >= robot.x &&
    ball.x - ball.radius <= robot.x + robot.width &&
    ball.y >= robot.y &&
    ball.y <= robot.y + robot.height;

  if (robotHit) {
    ball.vx = -Math.abs(ball.vx) * 1.02;
    ball.vy = (Math.random() - 0.5) * 4.2;
    ball.x = robot.x - ball.radius - 2;
  }
}

function drawCourt() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#0a4a0f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = 'rgba(255,255,255,0.45)';
  ctx.lineWidth = 2;
  ctx.strokeRect(20, 20, canvas.width - 40, canvas.height - 40);

  ctx.setLineDash([8, 8]);
  ctx.beginPath();
  ctx.moveTo(canvas.width / 2, 20);
  ctx.lineTo(canvas.width / 2, canvas.height - 20);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = 'rgba(255,255,255,0.12)';
  ctx.fillRect(0, 0, canvas.width, 20);
  ctx.fillRect(0, canvas.height - 20, canvas.width, 20);
}

function drawPaddles() {
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(player.x, player.y, player.width, player.height);
  ctx.fillRect(robot.x, robot.y, robot.width, robot.height);
}

function drawBall() {
  ctx.beginPath();
  ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
  ctx.fillStyle = '#f7f7f7';
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = '#ababab';
  ctx.stroke();
}

function draw() {
  drawCourt();
  drawPaddles();
  drawBall();
}

function loop(timestamp) {
  if (!lastTime) lastTime = timestamp;
  const delta = (timestamp - lastTime) / 1000;
  lastTime = timestamp;

  if (!gameOver) {
    updatePlayer();
    updateRobot(delta);
    updateBall(delta);
  }

  draw();
  requestAnimationFrame(loop);
}

window.addEventListener('keydown', (event) => {
  if (event.key === 'ArrowUp' || event.key === 'Up') {
    keys.up = true;
  }
  if (event.key === 'ArrowDown' || event.key === 'Down') {
    keys.down = true;
  }
  if (event.key === 'ArrowLeft' || event.key === 'Left') {
    keys.left = true;
  }
  if (event.key === 'ArrowRight' || event.key === 'Right') {
    keys.right = true;
  }
  if (event.key === ' ' || event.key === 'Spacebar') {
    event.preventDefault();
    keys.space = true;
  }
});

window.addEventListener('keyup', (event) => {
  if (event.key === 'ArrowUp' || event.key === 'Up') {
    keys.up = false;
  }
  if (event.key === 'ArrowDown' || event.key === 'Down') {
    keys.down = false;
  }
  if (event.key === 'ArrowLeft' || event.key === 'Left') {
    keys.left = false;
  }
  if (event.key === 'ArrowRight' || event.key === 'Right') {
    keys.right = false;
  }
  if (event.key === ' ' || event.key === 'Spacebar') {
    keys.space = false;
  }
});

window.addEventListener('keydown', (event) => {
  if (event.key === ' ' || event.key === 'Spacebar') {
    if (!gameOver) {
      attemptPlayerHit();
    }
  }
});

resetBall(-1);
scoreEl.textContent = score;
requestAnimationFrame(loop);
