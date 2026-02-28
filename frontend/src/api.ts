import type { Point, ScoreResponse, ReferenceResponse } from "./types";

const API_BASE = "http://127.0.0.1:8000";

export async function fetchReference(
  character: string
): Promise<ReferenceResponse> {
  const res = await fetch(`${API_BASE}/reference/${character}`);
  if (!res.ok) throw new Error("Failed to fetch reference");
  return res.json();
}

export async function fetchScore(
  character: string,
  userPoints: Point[]
): Promise<ScoreResponse> {
  const res = await fetch(`${API_BASE}/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      character,
      user_points: userPoints,
    }),
  });
  if (!res.ok) throw new Error("Failed to fetch score");
  return res.json();
}

export async function fetchCharacters(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/characters`);
  if (!res.ok) throw new Error("Failed to fetch characters");
  const data = await res.json();
  return data.characters;
}
