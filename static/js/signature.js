// ── Signature Canvas (penalty confirm modal) ──────
let signCanvas, signCtx, isDrawing = false, lastX = 0, lastY = 0;

function initCanvas() {
  signCanvas = document.getElementById('signatureCanvas');
  if (!signCanvas) return;
  signCtx = signCanvas.getContext('2d');
  signCtx.fillStyle = '#f8f9fa';
  signCtx.fillRect(0, 0, signCanvas.width, signCanvas.height);
  signCtx.strokeStyle = '#1a2b3c';
  signCtx.lineWidth = 2.5;
  signCtx.lineCap = 'round';
  signCtx.lineJoin = 'round';

  signCanvas.addEventListener('mousedown', startDraw);
  signCanvas.addEventListener('mousemove', draw);
  signCanvas.addEventListener('mouseup', stopDraw);
  signCanvas.addEventListener('mouseleave', stopDraw);

  signCanvas.addEventListener('touchstart', (e) => { e.preventDefault(); startDraw(e.touches[0]); }, { passive: false });
  signCanvas.addEventListener('touchmove',  (e) => { e.preventDefault(); draw(e.touches[0]); }, { passive: false });
  signCanvas.addEventListener('touchend',   stopDraw);
}

function getPos(e) {
  const rect = signCanvas.getBoundingClientRect();
  const scaleX = signCanvas.width  / rect.width;
  const scaleY = signCanvas.height / rect.height;
  return {
    x: (e.clientX - rect.left) * scaleX,
    y: (e.clientY - rect.top)  * scaleY,
  };
}

function startDraw(e) {
  isDrawing = true;
  const pos = getPos(e);
  lastX = pos.x; lastY = pos.y;
}

function draw(e) {
  if (!isDrawing) return;
  const pos = getPos(e);
  signCtx.beginPath();
  signCtx.moveTo(lastX, lastY);
  signCtx.lineTo(pos.x, pos.y);
  signCtx.stroke();
  lastX = pos.x; lastY = pos.y;
}

function stopDraw() { isDrawing = false; }

function clearCanvas() {
  if (!signCanvas) return;
  signCtx.clearRect(0, 0, signCanvas.width, signCanvas.height);
  signCtx.fillStyle = '#f8f9fa';
  signCtx.fillRect(0, 0, signCanvas.width, signCanvas.height);
}

// ── Profile Signature Canvas ─────────────────────
let profCanvas, profCtx, profDrawing = false, profLastX = 0, profLastY = 0;

function initProfileCanvas() {
  profCanvas = document.getElementById('profileSignCanvas');
  if (!profCanvas) return;
  profCtx = profCanvas.getContext('2d');
  profCtx.fillStyle = '#f8f9fa';
  profCtx.fillRect(0, 0, profCanvas.width, profCanvas.height);
  profCtx.strokeStyle = '#1a2b3c';
  profCtx.lineWidth = 2.5;
  profCtx.lineCap = 'round';
  profCtx.lineJoin = 'round';

  profCanvas.addEventListener('mousedown', profStart);
  profCanvas.addEventListener('mousemove', profDraw);
  profCanvas.addEventListener('mouseup',   profStop);
  profCanvas.addEventListener('mouseleave', profStop);
  profCanvas.addEventListener('touchstart', (e) => { e.preventDefault(); profStart(e.touches[0]); }, { passive: false });
  profCanvas.addEventListener('touchmove',  (e) => { e.preventDefault(); profDraw(e.touches[0]); },  { passive: false });
  profCanvas.addEventListener('touchend',   profStop);
}

function profGetPos(e) {
  const rect = profCanvas.getBoundingClientRect();
  return {
    x: (e.clientX - rect.left) * (profCanvas.width / rect.width),
    y: (e.clientY - rect.top)  * (profCanvas.height / rect.height),
  };
}

function profStart(e) { profDrawing = true; const p = profGetPos(e); profLastX = p.x; profLastY = p.y; }
function profDraw(e) {
  if (!profDrawing) return;
  const p = profGetPos(e);
  profCtx.beginPath(); profCtx.moveTo(profLastX, profLastY); profCtx.lineTo(p.x, p.y); profCtx.stroke();
  profLastX = p.x; profLastY = p.y;
}
function profStop() { profDrawing = false; }