import { useCallback, useEffect, useState } from "react";

import { ApiError, errorMessage } from "../api/client";
import { listPitches } from "../api/pitches";
import { getReservation } from "../api/reservations";
import type { Reservation } from "../api/types";
import { Alert, Loading } from "../components/Feedback";
import { ReservationCard } from "../components/ReservationCard";
import { links } from "../router";
import { loadReservationIds, saveReservationIds } from "../storage";

interface MyReservationsPageProps {
  onCountChange: () => void;
}

function byRelevance(a: Reservation, b: Reservation): number {
  const aCancelled = a.status === "CANCELLED" ? 1 : 0;
  const bCancelled = b.status === "CANCELLED" ? 1 : 0;
  return aCancelled - bCancelled || a.start.localeCompare(b.start);
}

export function MyReservationsPage({ onCountChange }: MyReservationsPageProps) {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [pitchNames, setPitchNames] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [removedCount, setRemovedCount] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const ids = loadReservationIds();
    try {
      const [pitches, results] = await Promise.all([
        listPitches(),
        Promise.allSettled(ids.map((id) => getReservation(id))),
      ]);
      setPitchNames(Object.fromEntries(pitches.map((p) => [p.id, p.name])));

      const found: Reservation[] = [];
      const missing: number[] = [];
      let firstError: unknown = null;
      results.forEach((result, index) => {
        if (result.status === "fulfilled") found.push(result.value);
        else if (result.reason instanceof ApiError && result.reason.status === 404) missing.push(ids[index]);
        else firstError ??= result.reason;
      });

      if (missing.length) {
        saveReservationIds(ids.filter((id) => !missing.includes(id)));
        onCountChange();
      }
      setRemovedCount(missing.length);
      setReservations(found);
      if (firstError) setError(errorMessage(firstError));
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setLoading(false);
    }
  }, [onCountChange]);

  useEffect(() => {
    void load();
  }, [load]);

  const replace = (updated: Reservation) =>
    setReservations((current) => current.map((r) => (r.id === updated.id ? updated : r)));

  return (
    <>
      <div className="page-header">
        <h1>My reservations</h1>
        <p className="muted">Pay pending bookings to confirm them, or cancel if your plans change.</p>
      </div>

      {loading && <Loading label="Loading your reservations…" />}

      {!loading && error && (
        <Alert kind="error" title="Some reservations couldn't be loaded">
          <p>{error}</p>
          <button type="button" className="btn btn--secondary btn--small" onClick={() => void load()}>
            Try again
          </button>
        </Alert>
      )}

      {!loading && removedCount > 0 && (
        <Alert kind="info" onDismiss={() => setRemovedCount(0)}>
          {removedCount} saved reservation{removedCount > 1 ? "s were" : " was"} not found on the server and
          removed from this list. The demo backend keeps data in memory, so a restart clears it.
        </Alert>
      )}

      {!loading && !error && reservations.length === 0 && (
        <div className="empty card">
          <p className="empty__title">No reservations yet</p>
          <p className="muted">Find a free slot and book your next match.</p>
          <a className="btn btn--primary" href={links.pitches}>
            Browse pitches
          </a>
        </div>
      )}

      {!loading && reservations.length > 0 && (
        <div className="reservation-list">
          {[...reservations].sort(byRelevance).map((reservation) => (
            <ReservationCard
              key={reservation.id}
              reservation={reservation}
              pitchName={pitchNames[reservation.pitch_id] ?? `Pitch #${reservation.pitch_id}`}
              onChange={replace}
            />
          ))}
        </div>
      )}
    </>
  );
}
