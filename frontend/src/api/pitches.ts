import { request } from "./client";
import type { Pitch, Slot } from "./types";

export function listPitches(): Promise<Pitch[]> {
  return request<Pitch[]>("/pitches");
}

export async function getPitch(pitchId: number): Promise<Pitch | undefined> {
  const pitches = await listPitches();
  return pitches.find((pitch) => pitch.id === pitchId);
}

export function listSlots(pitchId: number, day: string): Promise<Slot[]> {
  return request<Slot[]>(`/pitches/${pitchId}/slots?day=${encodeURIComponent(day)}`);
}
