export type ReservationStatus = "PENDING" | "CONFIRMED" | "CANCELLED";

export interface Pitch {
  id: number;
  name: string;
  owner_id: number;
  hourly_price: string;
}

export interface Slot {
  start: string;
  end: string;
  price: string;
  available: boolean;
}

export interface Reservation {
  id: number;
  pitch_id: number;
  customer_email: string;
  start: string;
  end: string;
  hours: number;
  price: string;
  status: ReservationStatus;
  payment_reference: string | null;
}

export interface NewReservation {
  pitch_id: number;
  customer_email: string;
  start: string;
  hours: number;
}
