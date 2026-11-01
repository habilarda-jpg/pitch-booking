const RESERVATIONS_KEY = "pitchBooking.reservationIds";
const EMAIL_KEY = "pitchBooking.email";

function read(key: string): string | null {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string): void {
  try {
    window.localStorage.setItem(key, value);
  } catch {
    return;
  }
}

export function loadReservationIds(): number[] {
  try {
    const parsed: unknown = JSON.parse(read(RESERVATIONS_KEY) ?? "[]");
    return Array.isArray(parsed) ? parsed.filter((id): id is number => Number.isInteger(id)) : [];
  } catch {
    return [];
  }
}

export function saveReservationIds(ids: number[]): void {
  write(RESERVATIONS_KEY, JSON.stringify([...new Set(ids)]));
}

export function rememberReservation(id: number): void {
  saveReservationIds([id, ...loadReservationIds()]);
}

export function loadEmail(): string {
  return read(EMAIL_KEY) ?? "";
}

export function saveEmail(email: string): void {
  write(EMAIL_KEY, email);
}
