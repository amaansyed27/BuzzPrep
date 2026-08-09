import { useEffect, useState } from "react";

export function useDesktopCapability() {
  const [desktop, setDesktop] = useState(() =>
    typeof window !== "undefined"
      ? window.matchMedia("(min-width: 960px) and (pointer: fine)").matches
      : true,
  );

  useEffect(() => {
    const query = window.matchMedia("(min-width: 960px) and (pointer: fine)");
    const update = () => setDesktop(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  return desktop;
}
