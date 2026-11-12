import { steps } from "../data.js";
import Reveal from "./Reveal.jsx";

export default function HowItWorks() {
  return (
    <section id="how" className="section alt">
      <div className="wrap">
        <Reveal>
          <h2>How it works</h2>
          <p className="sub">Slotbook replaces the notebook and the phone calls. Most owners are set up in an afternoon.</p>
        </Reveal>
        <ol className="steps">
          {steps.map((s, i) => (
            <Reveal key={s.title} as="li" delay={i * 150}>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </Reveal>
          ))}
        </ol>
      </div>
    </section>
  );
}
