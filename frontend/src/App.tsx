import { useCallback, useState, type MouseEvent } from "react";

import { NavBar } from "./components/NavBar";
import { MyReservationsPage } from "./pages/MyReservationsPage";
import { PitchDetailPage } from "./pages/PitchDetailPage";
import { PitchListPage } from "./pages/PitchListPage";
import { links, useRoute, type Route } from "./router";
import { loadReservationIds } from "./storage";

function skipToContent(event: MouseEvent<HTMLAnchorElement>) {
  event.preventDefault();
  document.getElementById("main")?.focus();
}

export function App() {
  const route = useRoute();
  const [reservationCount, setReservationCount] = useState(() => loadReservationIds().length);
  const refreshCount = useCallback(() => setReservationCount(loadReservationIds().length), []);

  return (
    <>
      <a className="skip-link" href="#main" onClick={skipToContent}>
        Skip to content
      </a>
      <NavBar route={route} reservationCount={reservationCount} />
      <main id="main" className="container" tabIndex={-1}>
        <Page route={route} onReservationsChanged={refreshCount} />
      </main>
      <footer className="footer">
        <div className="container">Pitch Booking · Sprint A demo · payments are simulated</div>
      </footer>
    </>
  );
}

function Page({ route, onReservationsChanged }: { route: Route; onReservationsChanged: () => void }) {
  switch (route.name) {
    case "pitches":
      return <PitchListPage />;
    case "pitch":
      return <PitchDetailPage key={route.pitchId} pitchId={route.pitchId} onReservationCreated={onReservationsChanged} />;
    case "reservations":
      return <MyReservationsPage onCountChange={onReservationsChanged} />;
    case "notFound":
      return (
        <div className="empty card">
          <p className="empty__title">Page not found</p>
          <a className="btn btn--primary" href={links.pitches}>
            Back to pitches
          </a>
        </div>
      );
  }
}
