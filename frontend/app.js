const API_BASE = "http://127.0.0.1:8000";

// DOM elements
const canvas = document.getElementById("drawCanvas");
const ctx = canvas.getContext("2d");
const scoreLabel = document.getElementById("scoreLabel");
const hintLabel = document.getElementById("hintLabel");
const subtitle = document.getElementById("subtitle");
const charSelect = document.getElementById("charSelect");
const overlayToggle = document.getElementById("overlayToggle");
const resetBtn = document.getElementById("resetBtn");

// State
let userPoints = [];
let referencePoints = [];
let isDrawing = false;
let drawingComplete = false;
let lastX = null;
let lastY = null;
let drawCounter = 0;

// --- API calls ---

async function fetchReference(character) {
    try {
        const res = await fetch(`${API_BASE}/reference/${character}`);
        if (!res.ok) throw new Error("Failed to fetch reference");
        const data = await res.json();
        referencePoints = data.edge_points.map(p => [p.x, p.y]);
        console.log(`Loaded ${referencePoints.length} reference points for '${character}'`);
    } catch (err) {
        console.error("Error fetching reference:", err);
    }
}

async function fetchScore(character, points) {
    try {
        const res = await fetch(`${API_BASE}/score`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                character: character,
                user_points: points.map(p => ({ x: p[0], y: p[1] }))
            })
        });
        if (!res.ok) throw new Error("Failed to fetch score");
        return await res.json();
    } catch (err) {
        console.error("Error fetching score:", err);
        return null;
    }
}

// --- Drawing ---

function resetCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    userPoints = [];
    drawCounter = 0;
    lastX = null;
    lastY = null;
    drawingComplete = false;
    overlayToggle.checked = false;
    scoreLabel.textContent = "Start drawing";
    scoreLabel.style.color = "#ffffff";
    hintLabel.textContent = "";
}

function getCanvasPos(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    if (e.touches) {
        return {
            x: (e.touches[0].clientX - rect.left) * scaleX,
            y: (e.touches[0].clientY - rect.top) * scaleY
        };
    }
    return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    };
}

function startDrawing(e) {
    e.preventDefault();
    if (drawingComplete) {
        resetCanvas();
    }
    isDrawing = true;
    const pos = getCanvasPos(e);
    lastX = pos.x;
    lastY = pos.y;
}

async function draw(e) {
    e.preventDefault();
    if (!isDrawing || drawingComplete) return;

    const pos = getCanvasPos(e);

    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(pos.x, pos.y);
    ctx.strokeStyle = "#e94560";
    ctx.lineWidth = 6;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.stroke();

    lastX = pos.x;
    lastY = pos.y;
    userPoints.push([pos.x, pos.y]);

    drawCounter++;
    if (drawCounter % 15 === 0 && userPoints.length >= 10) {
        const result = await fetchScore(charSelect.value, userPoints);
        if (result) {
            scoreLabel.textContent = `Score: ${result.score}%`;
        }
    }
}

async function stopDrawing(e) {
    e.preventDefault();
    if (!isDrawing || drawingComplete) return;

    isDrawing = false;
    drawingComplete = true;
    lastX = null;
    lastY = null;

    if (userPoints.length < 10) {
        scoreLabel.textContent = "Draw more!";
        drawingComplete = false;
        return;
    }

    const result = await fetchScore(charSelect.value, userPoints);
    if (result) {
        scoreLabel.textContent = `Final: ${result.score}%`;
        hintLabel.textContent = result.feedback + " — Click to try again";

        if (result.score >= 80) scoreLabel.style.color = "#4ade80";
        else if (result.score >= 60) scoreLabel.style.color = "#facc15";
        else if (result.score >= 40) scoreLabel.style.color = "#fb923c";
        else scoreLabel.style.color = "#f87171";
    }

    if (overlayToggle.checked) {
        drawOverlay();
    }
}

// --- Overlay ---

function drawOverlay() {
    if (!userPoints.length || !referencePoints.length) return;

    // Get bounding boxes
    const userBounds = getBounds(userPoints);
    const refBounds = getBounds(referencePoints);

    const userW = userBounds.maxX - userBounds.minX;
    const userH = userBounds.maxY - userBounds.minY;
    const refW = refBounds.maxX - refBounds.minX;
    const refH = refBounds.maxY - refBounds.minY;

    if (refW === 0 || refH === 0) return;

    ctx.fillStyle = "#4ade80";
    for (let i = 0; i < referencePoints.length; i += 8) {
        const [rx, ry] = referencePoints[i];
        const scaledX = userBounds.minX + ((rx - refBounds.minX) / refW) * userW;
        const scaledY = userBounds.minY + ((ry - refBounds.minY) / refH) * userH;

        ctx.beginPath();
        ctx.arc(scaledX, scaledY, 2, 0, Math.PI * 2);
        ctx.fill();
    }
}

function getBounds(points) {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const [x, y] of points) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
    }
    return { minX, minY, maxX, maxY };
}

// --- Event listeners ---

// Mouse events
canvas.addEventListener("mousedown", startDrawing);
canvas.addEventListener("mousemove", draw);
canvas.addEventListener("mouseup", stopDrawing);
canvas.addEventListener("mouseleave", stopDrawing);

// Touch events (mobile support)
canvas.addEventListener("touchstart", startDrawing);
canvas.addEventListener("touchmove", draw);
canvas.addEventListener("touchend", stopDrawing);

// Character change
charSelect.addEventListener("change", async (e) => {
    const char = e.target.value;
    subtitle.textContent = `Draw the character '${char}' as perfectly as you can!`;
    resetCanvas();
    await fetchReference(char);
});

// Overlay toggle
overlayToggle.addEventListener("change", () => {
    if (drawingComplete && overlayToggle.checked) {
        drawOverlay();
    }
    // Note: unchecking doesn't erase overlay since canvas is flat.
    // A full reset would be needed, or we'd need to redraw user strokes.
});

// Reset button
resetBtn.addEventListener("click", resetCanvas);

// --- Init ---
(async () => {
    await fetchReference("5");
})();
