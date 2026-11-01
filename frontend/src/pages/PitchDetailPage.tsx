import { useEffect, useMemo, useState, type FormEvent } from "react";

import { ApiError, errorMessage } from "../api/client";
import { getPitch, listSlots } from "../api/pitches";
import { createReservation } from "../api/reservations";
import type { Pitch, Reservation, Slot } from "../api/types";
import { Alert, Loading, Spinner } from "../components/Feedback";
import { addDays, formatDate, formatPrice, formatTime, isPast, todayIso } from "../format";
import { links } from "../router";
import { loadEmail, rememberReservation, saveEmail } from "../storage";

const MAX_HOURS = 3;

interface PitchDetailPageProps {
  pitchId: number;
  onReservationCreated: () => void;
}

function isBookable(slot: Slot): boolean {
  return slot.available && !isPast(slot.start);
}

export function PitchDetailPage({ pitchId, onReservationCreated }: PitchDetailPageProps) {
  const today = todayIso();
  const [pitch, setPitch] = useState<Pitch | null>(null);
  const [pitchError, setPitchError] = useState<string | null>(null);

  const [day, setDay] = useState(today);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [slotsLoading, setSlotsLoading] = useState(true);
  const [slotsError, setSlotsError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const [selectedStart, setSelectedStart] = useState<string | null>(null);
  const [hours, setHours] = useState(1);
  const [email, setEmail] = useState(loadEmail);
  const [submitting, setSubmitting] = useState(false);
  const [bookingError, setBookingError] = useState<string | null>(null);
  const [created, setCreated] = useState<Reservation | null>(null);

  useEffect(() => {
    let active = true;
    setPitch(null);
    setPitchError(null);
    getPitch(pitchId)
      .then((found) => {
        if (!active) return;
        if (found) setPitch(found);
        else setPitchError("This pitch does not exist (anymore).");
      })
      .catch((e) => active && setPitchError(errorMessage(e)));
    return () => {
      active = false;
    };
  }, [pitchId]);

  useEffect(() => {
    let active = true;
    setSlotsLoading(true);
    setSlotsError(null);
    listSlots(pitchId, day)
      .then((result) => active && setSlots(result))
      .catch((e) => active && setSlotsError(errorMessage(e)))
      .finally(() => active && setSlotsLoading(false));
    return () => {
      active = false;
    };
  }, [pitchId, day, reloadKey]);

  const selectedIndex = slots.findIndex((slot) => slot.start === selectedStart);
  const selectedSlot = selectedIndex >= 0 ? slots[selectedIndex] : null;

  const maxHours = useMemo(() => {
    if (selectedIndex < 0) return 1;
    let count = 0;
    while (count < MAX_HOURS && slots[selectedIndex + count] && isBookable(slots[selectedIndex + count])) {
      count += 1;
    }
    return Math.max(count, 1);
  }, [slots, selectedIndex]);

  const bookedSlots = selectedIndex >= 0 ? slots.slice(selectedIndex, selectedIndex + hours) : [];
  const total = bookedSlots.reduce((sum, slot) => sum + Number(slot.price), 0);
  const endTime = bookedSlots.length ? bookedSlots[bookedSlots.length - 1].end : null;

  const changeDay = (next: string) => {
    if (!next) return;
    setDay(next);
    setSelectedStart(null);
    setBookingError(null);
  };

  const selectSlot = (slot: Slot) => {
    setSelectedStart(slot.start === selectedStart ? null : slot.start);
    setHours(1);
    setBookingError(null);
    setCreated(null);
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedSlot) return;
    setSubmitting(true);
    setBookingError(null);
    try {
      const reservation = await createReservation({
        pitch_id: pitchId,
        customer_email: email.trim(),
        start: selectedSlot.start,
        hours,
      });
      rememberReservation(reservation.id);
      saveEmail(email.trim());
      onReservationCreated();
      setCreated(reservation);
      setSelectedStart(null);
      setReloadKey((k) => k + 1);
    } catch (e) {
      setBookingError(errorMessage(e));
      if (e instanceof ApiError && e.status === 409) {
        setReloadKey((k) => k + 1);
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (pitchError) {
    return (
      <>
        <a className="back-link" href={links.pitches}>
          ← All pitches
        </a>
        <Alert kind="error" title="We couldn't open this pitch">
          {pitchError}
        </Alert>
      </>
    );
  }

  return (
    <>
      <a className="back-link" href={links.pitches}>
        ← All pitches
      </a>

      <div className="page-header">
        <h1>{pitch ? pitch.name : "Loading pitch…"}</h1>
        {pitch && (
          <p className="muted">
            Base price {formatPrice(pitch.hourly_price)} / hour · peak 18–24 ×1.3 · weekends ×1.5
          </p>
        )}
      </div>

      {created && (
        <Alert kind="success" title="Reservation created!" onDismiss={() => setCreated(null)}>
          <p>
            Reservation #{created.id} on {formatDate(created.start)}, {formatTime(created.start)}–
            {formatTime(created.end)} is <strong>pending</strong> until you pay.{" "}
            <a href={links.reservations}>Go to My reservations to pay</a>
          </p>
        </Alert>
      )}

      <div className="detail-layout">
        <section className="card" aria-labelledby="slots-heading">
          <div className="slots-toolbar">
            <h2 id="slots-heading">Choose a time</h2>
            <div className="date-picker">
              <button
                type="button"
                className="icon-btn"
                onClick={() => changeDay(addDays(day, -1))}
                disabled={day <= today}
                aria-label="Previous day"
              >
                ‹
              </button>
              <div className="field field--inline">
                <label htmlFor="day">Date</label>
                <input
                  id="day"
                  type="date"
                  value={day}
                  min={today}
                  onChange={(e) => changeDay(e.target.value)}
                />
              </div>
              <button
                type="button"
                className="icon-btn"
                onClick={() => changeDay(addDays(day, 1))}
                aria-label="Next day"
              >
                ›
              </button>
            </div>
          </div>

          <p className="slots-date">{formatDate(day)}</p>

          <ul className="legend" aria-label="Legend">
            <li>
              <span className="legend__swatch legend__swatch--available" aria-hidden="true" /> Available
            </li>
            <li>
              <span className="legend__swatch legend__swatch--selected" aria-hidden="true" /> Selected
            </li>
            <li>
              <span className="legend__swatch legend__swatch--booked" aria-hidden="true" /> Booked / past
            </li>
          </ul>

          {slotsLoading && <Loading label="Loading slots…" />}

          {!slotsLoading && slotsError && (
            <Alert kind="error" title="We couldn't load the slots">
              <p>{slotsError}</p>
              <button
                type="button"
                className="btn btn--secondary btn--small"
                onClick={() => setReloadKey((k) => k + 1)}
              >
                Try again
              </button>
            </Alert>
          )}

          {!slotsLoading && !slotsError && (
            <ul className="slot-grid">
              {slots.map((slot, index) => {
                const bookable = isBookable(slot);
                const inSelection =
                  selectedIndex >= 0 && index >= selectedIndex && index < selectedIndex + hours;
                const state = !bookable ? "booked" : inSelection ? "selected" : "available";
                const tag = !slot.available ? "Booked" : isPast(slot.start) ? "Past" : null;
                return (
                  <li key={slot.start}>
                    <button
                      type="button"
                      className={`slot slot--${state}`}
                      disabled={!bookable}
                      aria-pressed={bookable ? slot.start === selectedStart : undefined}
                      aria-label={`${formatTime(slot.start)} to ${formatTime(slot.end)}, ${formatPrice(slot.price)}${tag ? `, ${tag}` : ""}`}
                      onClick={() => selectSlot(slot)}
                    >
                      <span className="slot__time">{formatTime(slot.start)}</span>
                      <span className="slot__price">{tag ?? formatPrice(slot.price)}</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </section>

        <aside className="card booking-panel" aria-labelledby="booking-heading">
          <h2 id="booking-heading">Your booking</h2>

          {!selectedSlot && (
            <p className="muted">Tap a green slot to start your booking.</p>
          )}

          {selectedSlot && (
            <form onSubmit={submit} className="stack">
              <dl className="summary">
                <div>
                  <dt>Date</dt>
                  <dd>{formatDate(selectedSlot.start)}</dd>
                </div>
                <div>
                  <dt>Time</dt>
                  <dd>
                    {formatTime(selectedSlot.start)}–{endTime ? formatTime(endTime) : ""}
                  </dd>
                </div>
              </dl>

              <div className="field">
                <label htmlFor="hours">Duration</label>
                <select id="hours" value={hours} onChange={(e) => setHours(Number(e.target.value))}>
                  {Array.from({ length: maxHours }, (_, i) => i + 1).map((h) => (
                    <option key={h} value={h}>
                      {h} hour{h > 1 ? "s" : ""}
                    </option>
                  ))}
                </select>
                {maxHours < MAX_HOURS && (
                  <p className="hint">Longer bookings aren't possible here because the next hour is taken.</p>
                )}
              </div>

              <div className="field">
                <label htmlFor="email">Your e-mail</label>
                <input
                  id="email"
                  type="email"
                  required
                  autoComplete="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  aria-describedby="email-hint"
                />
                <p className="hint" id="email-hint">
                  We send your booking confirmation here.
                </p>
              </div>

              <div className="total">
                <span>Total</span>
                <strong>{formatPrice(total)}</strong>
              </div>

              {bookingError && (
                <Alert kind="error" title="Booking failed">
                  {bookingError}
                </Alert>
              )}

              <button type="submit" className="btn btn--primary btn--block" disabled={submitting}>
                {submitting ? (
                  <>
                    <Spinner /> Reserving…
                  </>
                ) : (
                  "Reserve slot"
                )}
              </button>
              <button
                type="button"
                className="btn btn--ghost btn--block"
                onClick={() => setSelectedStart(null)}
                disabled={submitting}
              >
                Clear selection
              </button>
            </form>
          )}
        </aside>
      </div>
    </>
  );
}
