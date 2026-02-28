export interface Point {
  x: number;
  y: number;
}

export interface ScoreRequest {
  character: string;
  user_points: Point[];
}

export interface ScoreResponse {
  score: number;
  character: string;
  num_user_points: number;
  feedback: string;
}

export interface ReferenceResponse {
  character: string;
  edge_points: Point[];
  num_points: number;
}
