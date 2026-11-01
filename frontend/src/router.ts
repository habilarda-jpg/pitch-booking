import { useEffect, useState } from "react";

export type Route =
  | { name: "pitches" }
  | { name: "pitch"; pitchId: number }
  | { name: "reservations" }
  | { name: "notFound" };

export const links = {
  pitches: "#/",
  pitch: (pitchId: number) => `#/pitches/${pitchId}`,
  reservations: "#/reservations",
};

export function parseHash(hash: string): Route {
  const path = hash.replace(/^#/, "") || "/";
  if (path === "/") {
    return { name: "pitches" };
  }
  if (path === "/reservations") {
    return { name: "reservations" };
  }
  const match = /^\/pitches\/(\d+)$/.exec(path);
  if (match) {
    return { name: "pitch", pitchId: Number(match[1]) };
  }
  return { name: "notFound" };
}

export function useRoute(): Route {
  const [route, setRoute] = useState<Route>(() => parseHash(window.location.hash));

  useEffect(() => {
    const onChange = () => {
      setRoute(parseHash(window.location.hash));
      window.scrollTo({ top: 0 });
      document.getElementById("main")?.focus({ preventScroll: true });
    };
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  return route;
}
