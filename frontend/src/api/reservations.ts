import { request } from "./client";
import type { NewReservation, Reservation } from "./types";

export function createReservation(data: NewReservation): Promise<Reservation> {
  return request<Reservation>("/reservations", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getReservation(reservationId: number): Promise<Reservation> {
  return request<Reservation>(`/reservations/${reservationId}`);
}

export function payReservation(reservationId: number, cardNumber: string): Promise<Reservation> {
  return request<Reservation>(`/reservations/${reservationId}/pay`, {
    method: "POST",
    body: JSON.stringify({ card_number: cardNumber }),
  });
}

export function cancelReservation(reservationId: number): Promise<Reservation> {
  return request<Reservation>(`/reservations/${reservationId}/cancel`, { method: "POST" });
}
