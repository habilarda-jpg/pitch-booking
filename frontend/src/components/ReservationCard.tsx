import { useState, type FormEvent } from "react";

import { errorMessage } from "../api/client";
import { cancelReservation, payReservation } from "../api/reservations";
import type { Reservation } from "../api/types";
import { formatDate, formatPrice, formatTime } from "../format";
import { Alert, Spinner } from "./Feedback";
import { StatusBadge } from "./StatusBadge";

const TEST_CARD = "4242 4242 4242 4242";

interface ReservationCardProps {
  reservation: Reservation;
  pitchName: string;
  onChange: (reservation: Reservation) => void;
}

type Message = { kind: "success" | "error"; text: string };

export function ReservationCard({ reservation, pitchName, onChange }: ReservationCardProps) {
  const [cardNumber, setCardNumber] = useState("");
  const [busy, setBusy] = useState<"pay" | "cancel" | null>(null);
  const [confirmingCancel, setConfirmingCancel] = useState(false);
  const [message, setMessage] = useState<Message | null>(null);

  const id = reservation.id;
  const canPay = reservation.status === "PENDING";
  const canCancel = reservation.status !== "CANCELLED";

  const pay = async (event: FormEvent) => {
    event.preventDefault();
    setBusy("pay");
    setMessage(null);
    try {
      onChange(await payReservation(id, cardNumber.replace(/\s+/g, "")));
      setCardNumber("");
      setMessage({ kind: "success", text: "Payment received. Your reservation is confirmed. See you on the pitch!" });
    } catch (e) {
      setMessage({ kind: "error", text: errorMessage(e) });
    } finally {
      setBusy(null);
    }
  };

  const cancel = async () => {
    setBusy("cancel");
    setMessage(null);
    try {
      onChange(await cancelReservation(id));
      setMessage({ kind: "success", text: "Reservation cancelled. The slot is free for others again." });
    } catch (e) {
      setMessage({ kind: "error", text: errorMessage(e) });
    } finally {
      setBusy(null);
      setConfirmingCancel(false);
    }
  };

  return (
    <article className={`card reservation reservation--${reservation.status.toLowerCase()}`} aria-labelledby={`res-${id}-title`}>
      <header className="reservation__header">
        <div>
          <h2 className="reservation__title" id={`res-${id}-title`}>
            {pitchName}
          </h2>
          <p className="muted">Reservation #{id}</p>
        </div>
        <StatusBadge status={reservation.status} />
      </header>

      <dl className="summary summary--row">
        <div>
          <dt>Date</dt>
          <dd>{formatDate(reservation.start)}</dd>
        </div>
        <div>
          <dt>Time</dt>
          <dd>
            {formatTime(reservation.start)}–{formatTime(reservation.end)}
          </dd>
        </div>
        <div>
          <dt>Duration</dt>
          <dd>
            {reservation.hours} hour{reservation.hours > 1 ? "s" : ""}
          </dd>
        </div>
        <div>
          <dt>Price</dt>
          <dd>{formatPrice(reservation.price)}</dd>
        </div>
        {reservation.payment_reference && (
          <div>
            <dt>Payment ref.</dt>
            <dd className="mono">{reservation.payment_reference}</dd>
          </div>
        )}
      </dl>

      {message && (
        <Alert kind={message.kind} onDismiss={() => setMessage(null)}>
          {message.text}
        </Alert>
      )}

      {canPay && (
        <form className="pay-form" onSubmit={pay}>
          <div className="field">
            <label htmlFor={`card-${id}`}>Card number</label>
            <input
              id={`card-${id}`}
              inputMode="numeric"
              autoComplete="cc-number"
              placeholder={TEST_CARD}
              required
              value={cardNumber}
              onChange={(e) => setCardNumber(e.target.value)}
              aria-describedby={`card-${id}-hint`}
            />
            <p className="hint" id={`card-${id}-hint`}>
              Mock payment. Test card <span className="mono">{TEST_CARD}</span> is approved;{" "}
              <span className="mono">4000 0000 0000 0002</span> is declined.{" "}
              <button type="button" className="link-btn" onClick={() => setCardNumber(TEST_CARD)}>
                Use test card
              </button>
            </p>
          </div>
          <button type="submit" className="btn btn--primary" disabled={busy !== null}>
            {busy === "pay" ? (
              <>
                <Spinner /> Paying…
              </>
            ) : (
              `Pay ${formatPrice(reservation.price)}`
            )}
          </button>
        </form>
      )}

      {canCancel && !confirmingCancel && (
        <div className="reservation__actions">
          <button
            type="button"
            className="btn btn--danger-ghost"
            onClick={() => setConfirmingCancel(true)}
            disabled={busy !== null}
          >
            Cancel reservation
          </button>
        </div>
      )}

      {canCancel && confirmingCancel && (
        <div className="confirm" role="group" aria-labelledby={`confirm-${id}`}>
          <p id={`confirm-${id}`}>
            <strong>Cancel this reservation?</strong> The slot will be released for other players.
          </p>
          <div className="confirm__buttons">
            <button type="button" className="btn btn--danger" onClick={() => void cancel()} disabled={busy !== null}>
              {busy === "cancel" ? (
                <>
                  <Spinner /> Cancelling…
                </>
              ) : (
                "Yes, cancel it"
              )}
            </button>
            <button
              type="button"
              className="btn btn--secondary"
              onClick={() => setConfirmingCancel(false)}
              disabled={busy !== null}
              autoFocus
            >
              Keep reservation
            </button>
          </div>
        </div>
      )}
    </article>
  );
}
