const galleryView = document.getElementById('galleryView');
const editorView = document.getElementById('editorView');
const addBtn = document.getElementById('addBtn');
const saveBtn = document.getElementById('saveBtn');
const backBtn = document.getElementById('backBtn');
const clearBtn = document.getElementById('clearBtn');
const emojiBtn = document.getElementById('emojiBtn');
const emojiPicker = document.getElementById('emojiPicker');
const gallery = document.getElementById('gallery');
const canvas = document.getElementById('trainCanvas');
const ctx = canvas.getContext('2d');

const state = {
  tool: 'paintbrush',
  color: '#111111',
  drawing: false,
  emojiMode: false,
  entries: [],
};

function loadEntries() {
  try {
    const raw = localStorage.getItem('trainGalleryEntries');
    state.entries = raw ? JSON.parse(raw) : [];
  } catch (error) {
    state.entries = [];
  }
}

function saveEntries() {
  localStorage.setItem('trainGalleryEntries', JSON.stringify(state.entries));
}

function renderGallery() {
  if (!state.entries.length) {
    gallery.innerHTML = '<p class="empty">No trains saved yet. Create one!</p>';
    return;
  }

  gallery.innerHTML = '';
  state.entries.forEach((entry) => {
    const card = document.createElement('article');
    card.className = 'gallery-card';
    card.innerHTML = `
      <img src="${entry.image}" alt="Decorated train" />
      <p>${entry.label}</p>
    `;
    gallery.appendChild(card);
  });
}

function drawBaseTrain() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.save();
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = '#222222';
  ctx.lineWidth = 4;
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';

  const trainY = 360;
  const bodyHeight = 100;
  const bodyWidth = 300;

  ctx.fillStyle = '#f4f4f5';
  ctx.strokeRect(150, trainY - 50, bodyWidth, bodyHeight);
  ctx.fillRect(150, trainY - 50, bodyWidth, bodyHeight);

  ctx.fillStyle = '#e4e4e7';
  ctx.fillRect(250, trainY - 90, 140, 40);
  ctx.strokeRect(250, trainY - 90, 140, 40);

  ctx.fillStyle = '#d4d4d8';
  ctx.beginPath();
  ctx.arc(220, trainY + 50, 34, 0, Math.PI * 2);
  ctx.arc(420, trainY + 50, 34, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = '#111111';
  ctx.beginPath();
  ctx.arc(220, trainY + 50, 16, 0, Math.PI * 2);
  ctx.arc(420, trainY + 50, 16, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#52525b';
  ctx.fillRect(470, trainY - 20, 90, 50);
  ctx.strokeRect(470, trainY - 20, 90, 50);

  ctx.restore();
}

function setTool(toolName) {
  state.tool = toolName;
  state.emojiMode = toolName === 'emoji';
  document.querySelectorAll('.tool-btn').forEach((btn) => btn.classList.toggle('active', btn.dataset.tool === toolName));
  emojiPicker.classList.toggle('show', state.emojiMode);
}

function setColor(color) {
  state.color = color;
  document.querySelectorAll('.color-swatch').forEach((swatch) => {
    swatch.classList.toggle('active', swatch.dataset.color === color);
  });
}

function getPoint(event) {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  return {
    x: (event.clientX - rect.left) * scaleX,
    y: (event.clientY - rect.top) * scaleY,
  };
}

function beginStroke(event) {
  if (state.emojiMode) {
    const point = getPoint(event);
    addEmoji(point);
    return;
  }

  state.drawing = true;
  const point = getPoint(event);
  ctx.beginPath();
  ctx.moveTo(point.x, point.y);
  ctx.strokeStyle = state.color;
  ctx.lineWidth = state.tool === 'marker' ? 16 : state.tool === 'colored-pencil' ? 7 : 8;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.globalAlpha = state.tool === 'colored-pencil' ? 0.65 : 1;
  ctx.lineTo(point.x, point.y);
  ctx.stroke();
  ctx.globalAlpha = 1;
}

function continueStroke(event) {
  if (!state.drawing || state.emojiMode) return;
  const point = getPoint(event);
  ctx.lineTo(point.x, point.y);
  ctx.stroke();
}

function endStroke() {
  state.drawing = false;
  ctx.beginPath();
}

function addEmoji(point) {
  const emoji = document.querySelector('.emoji-picker button.active')?.dataset.emoji || '⭐';
  ctx.font = '48px sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(emoji, point.x, point.y);
}

function clearCanvas() {
  drawBaseTrain();
}

function switchToEditor() {
  galleryView.classList.remove('active');
  editorView.classList.add('active');
  drawBaseTrain();
}

function switchToGallery() {
  editorView.classList.remove('active');
  galleryView.classList.add('active');
  renderGallery();
}

function saveCurrentTrain() {
  const image = canvas.toDataURL('image/png');
  state.entries.unshift({
    id: Date.now(),
    image,
    label: `Train ${state.entries.length + 1}`,
  });
  saveEntries();
  renderGallery();
  switchToGallery();
}

addBtn.addEventListener('click', switchToEditor);
backBtn.addEventListener('click', switchToGallery);
saveBtn.addEventListener('click', saveCurrentTrain);
clearBtn.addEventListener('click', clearCanvas);

canvas.addEventListener('pointerdown', beginStroke);
canvas.addEventListener('pointermove', continueStroke);
canvas.addEventListener('pointerup', endStroke);
canvas.addEventListener('pointerleave', endStroke);

emojiBtn.addEventListener('click', () => {
  setTool('emoji');
});

document.querySelectorAll('.tool-btn[data-tool]').forEach((btn) => {
  btn.addEventListener('click', () => setTool(btn.dataset.tool));
});

document.querySelectorAll('.color-swatch').forEach((swatch) => {
  swatch.addEventListener('click', () => setColor(swatch.dataset.color));
});

document.querySelectorAll('.emoji-picker button').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.emoji-picker button').forEach((btn) => btn.classList.remove('active'));
    button.classList.add('active');
  });
});

loadEntries();
renderGallery();
drawBaseTrain();
setTool('paintbrush');
setColor('#111111');
