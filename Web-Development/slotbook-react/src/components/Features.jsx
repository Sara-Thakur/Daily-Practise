import { useState } from "react";
import { features } from "../data.js";
import Reveal from "./Reveal.jsx";

// Flips on hover (mouse), on tap (touch) or on focus (keyboard).
function FlipCard({ feature }) {
  const [flipped, setFlipped] = useState(false);

  const tap = () => {
    // on a mouse device hover already does the job, so only react to taps
    if (window.matchMedia("(hover: none)").matches) setFlipped(!flipped);
  };

  return (
    <div className={`flip ${flipped ? "flipped" : ""}`} tabIndex={0} onClick={tap}>
      <div className="flip-inner">
        <div className="face front">
          <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d={feature.icon} />
          </svg>
          <h3>{feature.title}</h3>
          <small>Hover or tap to learn more</small>
        </div>
        <div className="face back">
          <p>{feature.text}</p>
          <a href="#contact">Request a demo</a>
        </div>
      </div>
    </div>
  );
}

export default function Features() {
  return (
    <section id="features" className="section">
      <div className="wrap">
        <Reveal><h2>Everything you need to fill your calendar</h2></Reveal>
        <div className="cards">
          {features.map((f, i) => (
            <Reveal key={f.title} delay={i * 120}>
              <FlipCard feature={f} />
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
