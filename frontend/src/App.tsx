import { useState, useEffect, useCallback } from "react";
import DrawingCanvas from "./components/DrawingCanvas";
import { fetchReference, fetchScore, fetchCharacters } from "./api";
import type { Point } from "./types";
import "./App.css";

function getScoreColor(score: number): string {
  if (score >= 80) return "#4ade80";
  if (score >= 60) return "#facc15";
  if (score >= 40) return "#fb923c";
  return "#f87171";
}

export default function App() {
  const [characters, setCharacters] = useState<string[]>(["5"]);
  const [selectedChar, setSelectedChar] = useState("5");
  const [referencePoints, setReferencePoints] = useState<Point[]>([]);
  const [scoreText, setScoreText] = useState("Start drawing");
  const [scoreColor, setScoreColor] = useState("#ffffff");
  const [feedback, setFeedback] = useState("");
  const [showOverlay, setShowOverlay] = useState(false);
  const [resetCounter, setResetCounter] = useState(0);
  const [isFinished, setIsFinished] = useState(false);

  useEffect(() => {
    fetchCharacters().then(setCharacters).catch(console.error);
    loadReference("5");
  }, []);

  const loadReference = async (char: string) => {
    try {
      const data = await fetchReference(char);
      setReferencePoints(data.edge_points);
      console.log(`Loaded ${data.num_points} reference points for '${char}'`);
    } catch (err) {
      console.error("Failed to load reference:", err);
    }
  };

  const handleReset = useCallback(() => {
    setResetCounter((c) => c + 1);
    setScoreText("Start drawing");
    setScoreColor("#ffffff");
    setFeedback("");
    setShowOverlay(false);
    setIsFinished(false);
  }, []);

  const handleCharChange = async (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const char = e.target.value;
    setSelectedChar(char);
    handleReset();
    await loadReference(char);
  };

  const handleDrawUpdate = useCallback((_points: Point[]) => {
    // Could add real-time UI updates here
  }, []);

  const handleLiveScore = useCallback(
    async (points: Point[]) => {
      try {
        const result = await fetchScore(selectedChar, points);
        setScoreText(`Score: ${result.score}%`);
      } catch (err) {
        console.error(err);
      }
    },
    [selectedChar]
  );

  const handleDrawEnd = useCallback(
    async (points: Point[]) => {
      if (points.length < 10) {
        setScoreText("Draw more!");
        return;
      }

      try {
        const result = await fetchScore(selectedChar, points);
        setScoreText(`Final: ${result.score}%`);
        setScoreColor(getScoreColor(result.score));
        setFeedback(result.feedback + " — Click canvas to try again");
        setIsFinished(true);
      } catch (err) {
        console.error(err);
      }
    },
    [selectedChar]
  );

  return (
    <div className="container">
      <h1 className="title">Perfect Five</h1>
      <p className="subtitle">
        Draw the character '{selectedChar}' as perfectly as you can!
      </p>

      <div className="controls">
        <label htmlFor="charSelect">Character:</label>
        <select
          id="charSelect"
          value={selectedChar}
          onChange={handleCharChange}
        >
          {characters.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      <div
        className="canvas-wrapper"
        onClick={isFinished ? handleReset : undefined}
      >
        <DrawingCanvas
          onDrawUpdate={handleDrawUpdate}
          onDrawEnd={handleDrawEnd}
          onLiveScore={handleLiveScore}
          referencePoints={referencePoints}
          showOverlay={showOverlay}
          resetTrigger={resetCounter}
        />
      </div>

      <p className="score" style={{ color: scoreColor }}>
        {scoreText}
      </p>
      <p className="hint">{feedback}</p>

      <div className="options">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={showOverlay}
            onChange={(e) => setShowOverlay(e.target.checked)}
          />
          Show perfect shape
        </label>
        <button className="reset-btn" onClick={handleReset}>
          Reset
        </button>
      </div>
    </div>
  );
}
