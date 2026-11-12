import { useEffect, useRef, useState } from "react";

// Counts up or down to the new value instead of jumping.
export default function AnimatedNumber({ value }) {
  const [shown, setShown] = useState(value);
  const current = useRef(value);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      current.current = value;
      setShown(value);
      return;
    }
    const start = current.current;
    const t0 = performance.now();
    let frame;
    const tick = (now) => {
      const k = Math.min((now - t0) / 450, 1);
      const eased = 1 - Math.pow(1 - k, 3);
      current.current = Math.round(start + (value - start) * eased);
      setShown(current.current);
      if (k < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [value]);

  return shown.toLocaleString("en-IN");
}
