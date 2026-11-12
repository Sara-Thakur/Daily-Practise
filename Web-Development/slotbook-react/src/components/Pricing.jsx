import { useState } from "react";
import { plans } from "../data.js";
import Reveal from "./Reveal.jsx";
import AnimatedNumber from "./AnimatedNumber.jsx";

const YEARLY_DISCOUNT = 0.8; // 20% off

export default function Pricing() {
  const [yearly, setYearly] = useState(false);

  return (
    <section id="pricing" className="section">
      <div className="wrap">
        <Reveal>
          <h2>Simple pricing</h2>
          <p className="sub">Try any plan free for 14 days. No card needed.</p>
          <div className="billing">
            <span className={yearly ? "" : "on"}>Monthly</span>
            <button
              className="switch"
              role="switch"
              aria-checked={yearly}
              aria-label="Switch to yearly billing"
              onClick={() => setYearly(!yearly)}
            >
              <span />
            </button>
            <span className={yearly ? "on" : ""}>Yearly <em>save 20%</em></span>
          </div>
        </Reveal>
        <div className="plans">
          {plans.map((p, i) => {
            const price = yearly ? Math.round(p.price * YEARLY_DISCOUNT) : p.price;
            return (
              <Reveal key={p.name} as="article" className={`plan ${p.featured ? "featured" : ""}`} delay={i * 120}>
                <h3>{p.name}</h3>
                <p className="price">
                  &#8377;<AnimatedNumber value={price} />
                  <span>/month{yearly ? ", billed yearly" : ""}</span>
                </p>
                <ul>
                  {p.perks.map((perk) => <li key={perk}>{perk}</li>)}
                </ul>
                <a href="#contact" className={`btn ${p.featured ? "" : "btn-ghost"}`}>Choose {p.name}</a>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
