import { useEffect, useRef, useState } from "react";

const day = [
  { time: "9:00", label: "Haircut - Meera K.", type: "blue" },
  { time: "10:00", label: "Colour - Aman S.", type: "blue" },
  { time: "11:00", open: 0 },
  { time: "12:00", label: "Lunch break", type: "sun" },
  { time: "1:00", label: "Beard trim - Dev P.", type: "blue" },
  { time: "2:00", open: 1 },
];
const newBookings = ["Facial - Riya T.", "Haircut - Kabir J."];

// Open slots book themselves until the visitor clicks one, then they're in control.
function Calendar() {
  const [taken, setTaken] = useState([false, false]);
  const [touched, setTouched] = useState(false);
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (touched || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const id = setInterval(() => setStep((s) => (s + 1) % 4), 2200);
    return () => clearInterval(id);
  }, [touched]);

  useEffect(() => {
    if (!touched) setTaken([step > 0, step > 1]);
  }, [step, touched]);

  const toggle = (i) => {
    setTouched(true);
    setTaken((t) => t.map((v, j) => (j === i ? !v : v)));
  };

  const booked = 3 + taken.filter(Boolean).length;

  return (
    <div>
      <div className="cal">
        <div className="cal-top"><b>Thursday, 14 Nov</b><span>{booked} booked</span></div>
        {day.map((slot) => {
          const isOpen = slot.open !== undefined;
          const isTaken = isOpen && taken[slot.open];
          return (
            <div className="row" key={slot.time}>
              <time>{slot.time}</time>
              {isOpen ? (
                <button
                  key={String(isTaken)}
                  className={`slot ${isTaken ? "s-blue pop" : "s-free"}`}
                  aria-pressed={isTaken}
                  onClick={() => toggle(slot.open)}
                >
                  {isTaken ? newBookings[slot.open] : "Open - click to book"}
                </button>
              ) : (
                <div className={`slot s-${slot.type}`}>{slot.label}</div>
              )}
            </div>
          );
        })}
      </div>
      <p className="cal-hint">Try it: click an open slot.</p>
    </div>
  );
}

export default function Hero() {
  const title = useRef(null);

  // the picture inside the headline follows the mouse
  const follow = (e) => {
    const box = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - box.left) / box.width) * 100;
    const y = ((e.clientY - box.top) / box.height) * 100;
    title.current.style.setProperty("--mx", `${x}%`);
    title.current.style.setProperty("--my", `${y}%`);
  };

  return (
    <section className="hero" onMouseMove={follow}>
      <div className="wrap hero-grid">
        <div className="hero-copy">
          <h1 ref={title}>Let your clients book themselves.</h1>
          <p className="lead">
            Slotbook gives salons, clinics and tutors a booking page that works around the clock.
            No more back-and-forth messages to find a free time.
          </p>
          <div className="hero-actions">
            <a href="#contact" className="btn">Request a demo</a>
            <a href="#how" className="btn btn-ghost">See how it works</a>
          </div>
        </div>
        <Calendar />
      </div>
    </section>
  );
}
