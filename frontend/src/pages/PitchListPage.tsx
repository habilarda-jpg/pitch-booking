import { useCallback, useEffect, useState } from "react";

import { errorMessage } from "../api/client";
import { listPitches } from "../api/pitches";
import type { Pitch } from "../api/types";
import { Alert, Loading } from "../components/Feedback";
import { formatPrice } from "../format";
import { links } from "../router";

export function PitchListPage() {
  const [pitches, setPitches] = useState<Pitch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setPitches(await listPitches());
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <>
      <section className="hero">
        <h1>Book a pitch in seconds</h1>
        <p>
          Pick a pitch, choose a free hour and pay securely. Your slot is held for you as soon as you
          reserve it.
        </p>
        <ul className="pricing-notes" aria-label="How prices work">
          <li>
            <strong>Weekdays 09–18</strong> base price
          </li>
          <li>
            <strong>Weekdays 18–24</strong> peak ×1.3
          </li>
          <li>
            <strong>Weekends</strong> ×1.5
          </li>
        </ul>
      </section>

      <h2 className="section-title">Pitches</h2>

      {loading && <Loading label="Loading pitches…" />}

      {error && (
        <Alert kind="error" title="We couldn't load the pitches">
          <p>{error}</p>
          <button type="button" className="btn btn--secondary btn--small" onClick={() => void load()}>
            Try again
          </button>
        </Alert>
      )}

      {!loading && !error && pitches.length === 0 && (
        <div className="empty card">
          <p>No pitches have been added yet.</p>
        </div>
      )}

      {!loading && !error && pitches.length > 0 && (
        <ul className="pitch-grid">
          {pitches.map((pitch) => (
            <li key={pitch.id} className="card pitch-card">
              <div className="pitch-card__art" aria-hidden="true" />
              <div className="pitch-card__body">
                <h3 className="pitch-card__name">{pitch.name}</h3>
                <p className="pitch-card__price">
                  <span className="pitch-card__amount">{formatPrice(pitch.hourly_price)}</span>
                  <span className="muted"> / hour base price</span>
                </p>
                <a className="btn btn--primary btn--block" href={links.pitch(pitch.id)}>
                  See available slots
                </a>
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
