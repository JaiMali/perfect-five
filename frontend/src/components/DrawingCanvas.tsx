import { useRef, useEffect, useCallback } from "react";
import type { Point } from "../types";

interface Segment {
  from: Point;
  to: Point;
}

interface DrawingCanvasProps {
  onDrawUpdate: (points: Point[]) => void;
  onDrawEnd: (points: Point[]) => void;
  onLiveScore: (points: Point[]) => void;
  referencePoints: Point[];
  showOverlay: boolean;
  resetTrigger: number;
}

export default function DrawingCanvas({
  onDrawUpdate,
  onDrawEnd,
  onLiveScore,
  referencePoints,
  showOverlay,
  resetTrigger,
}: DrawingCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isDrawing = useRef(false);
  const lastPos = useRef<Point | null>(null);
  const pointsRef = useRef<Point[]>([]);
  const segmentsRef = useRef<Segment[]>([]);
  const drawCountRef = useRef(0);
  const drawingComplete = useRef(false);

  const getCanvasPos = useCallback(
    (e: React.MouseEvent | React.TouchEvent): Point => {
      const canvas = canvasRef.current!;
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;

      if ("touches" in e) {
        return {
          x: (e.touches[0].clientX - rect.left) * scaleX,
          y: (e.touches[0].clientY - rect.top) * scaleY,
        };
      }
      return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY,
      };
    },
    []
  );

  // Reset when trigger changes
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    pointsRef.current = [];
    segmentsRef.current = [];
    drawCountRef.current = 0;
    isDrawing.current = false;
    lastPos.current = null;
    drawingComplete.current = false;
  }, [resetTrigger]);

  // Handle overlay drawing
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;

    // Always redraw user strokes first
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = "#e94560";
    ctx.lineWidth = 6;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    for (const seg of segmentsRef.current) {
      ctx.beginPath();
      ctx.moveTo(seg.from.x, seg.from.y);
      ctx.lineTo(seg.to.x, seg.to.y);
      ctx.stroke();
    }

    // Draw overlay if enabled
    if (
      showOverlay &&
      pointsRef.current.length > 0 &&
      referencePoints.length > 0
    ) {
      const userBounds = getBounds(pointsRef.current);
      const refBounds = getBounds(referencePoints);

      const userW = userBounds.maxX - userBounds.minX;
      const userH = userBounds.maxY - userBounds.minY;
      const refW = refBounds.maxX - refBounds.minX;
      const refH = refBounds.maxY - refBounds.minY;

      if (refW > 0 && refH > 0) {
        ctx.fillStyle = "#4ade80";
        for (let i = 0; i < referencePoints.length; i += 8) {
          const rp = referencePoints[i];
          const scaledX =
            userBounds.minX + ((rp.x - refBounds.minX) / refW) * userW;
          const scaledY =
            userBounds.minY + ((rp.y - refBounds.minY) / refH) * userH;
          ctx.beginPath();
          ctx.arc(scaledX, scaledY, 2, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }
  }, [showOverlay, referencePoints]);

  const handleStart = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    if (drawingComplete.current) return;
    isDrawing.current = true;
    lastPos.current = getCanvasPos(e);
  };

  const handleMove = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    if (!isDrawing.current || drawingComplete.current) return;

    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const pos = getCanvasPos(e);

    if (lastPos.current) {
      ctx.beginPath();
      ctx.moveTo(lastPos.current.x, lastPos.current.y);
      ctx.lineTo(pos.x, pos.y);
      ctx.strokeStyle = "#e94560";
      ctx.lineWidth = 6;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.stroke();

      segmentsRef.current.push({ from: lastPos.current, to: pos });
    }

    lastPos.current = pos;
    pointsRef.current.push(pos);
    onDrawUpdate(pointsRef.current);

    drawCountRef.current++;
    if (
      drawCountRef.current % 15 === 0 &&
      pointsRef.current.length >= 10
    ) {
      onLiveScore([...pointsRef.current]);
    }
  };

  const handleEnd = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    if (!isDrawing.current || drawingComplete.current) return;
    isDrawing.current = false;
    lastPos.current = null;
    drawingComplete.current = true;

    if (pointsRef.current.length >= 10) {
      onDrawEnd([...pointsRef.current]);
    }
  };

  return (
    <canvas
      ref={canvasRef}
      width={500}
      height={500}
      style={{
        backgroundColor: "#16213e",
        borderRadius: "12px",
        cursor: "crosshair",
        display: "block",
        maxWidth: "100%",
        touchAction: "none",
      }}
      onMouseDown={handleStart}
      onMouseMove={handleMove}
      onMouseUp={handleEnd}
      onMouseLeave={handleEnd}
      onTouchStart={handleStart}
      onTouchMove={handleMove}
      onTouchEnd={handleEnd}
    />
  );
}

function getBounds(points: Point[]) {
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const p of points) {
    if (p.x < minX) minX = p.x;
    if (p.x > maxX) maxX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.y > maxY) maxY = p.y;
  }
  return { minX, minY, maxX, maxY };
}
