import { links, type Route } from "../router";

interface NavBarProps {
  route: Route;
  reservationCount: number;
}

export function NavBar({ route, reservationCount }: NavBarProps) {
  const onPitches = route.name === "pitches" || route.name === "pitch";
  const onReservations = route.name === "reservations";

  return (
    <header className="topbar">
      <div className="topbar__inner">
        <a className="brand" href={links.pitches}>
          <span className="brand__mark" aria-hidden="true">
            ⚽
          </span>
          <span>
            Pitch<strong>Booking</strong>
          </span>
        </a>
        <nav aria-label="Main">
          <ul className="nav">
            <li>
              <a className="nav__link" href={links.pitches} aria-current={onPitches ? "page" : undefined}>
                Pitches
              </a>
            </li>
            <li>
              <a
                className="nav__link"
                href={links.reservations}
                aria-current={onReservations ? "page" : undefined}
              >
                My reservations
                {reservationCount > 0 && (
                  <span className="nav__count" aria-label={`${reservationCount} saved`}>
                    {reservationCount}
                  </span>
                )}
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}
