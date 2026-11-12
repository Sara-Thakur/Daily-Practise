import { useState } from "react";
import { businessTypes } from "../data.js";
import Reveal from "./Reveal.jsx";

const empty = { name: "", email: "", biz: "" };

function validate({ name, email, biz }) {
  const errors = {};
  if (name.trim().length < 2) errors.name = "Please enter your name.";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) errors.email = "Enter a valid email, like name@example.com.";
  if (!biz) errors.biz = "Choose your type of business.";
  return errors;
}

export default function Contact() {
  const [values, setValues] = useState(empty);
  const [errors, setErrors] = useState({});
  const [sentTo, setSentTo] = useState(null);

  const change = (e) => {
    setValues({ ...values, [e.target.name]: e.target.value });
    if (errors[e.target.name]) setErrors({ ...errors, [e.target.name]: undefined });
  };

  const submit = (e) => {
    e.preventDefault();
    setSentTo(null);
    const found = validate(values);
    setErrors(found);
    if (Object.keys(found).length > 0) return;
    setSentTo({ name: values.name.trim().split(" ")[0], email: values.email.trim() });
    setValues(empty);
  };

  const field = (name) => (errors[name] ? "invalid" : "");

  return (
    <section id="contact" className="section alt">
      <div className="wrap contact-grid">
        <Reveal>
          <h2>Request a demo</h2>
          <p className="sub">Tell us a little about your business and we will reply within one working day.</p>
          <p className="details">hello@slotbook.example<br />+91 98765 43210<br />Indore, Madhya Pradesh</p>
        </Reveal>

        <Reveal delay={150}>
          <form onSubmit={submit} noValidate>
            <label htmlFor="name">Your name</label>
            <input id="name" name="name" type="text" autoComplete="name" value={values.name} onChange={change} className={field("name")} />
            <small className="err">{errors.name}</small>

            <label htmlFor="email">Email</label>
            <input id="email" name="email" type="email" autoComplete="email" value={values.email} onChange={change} className={field("email")} />
            <small className="err">{errors.email}</small>

            <label htmlFor="biz">Type of business</label>
            <select id="biz" name="biz" value={values.biz} onChange={change} className={field("biz")}>
              <option value="">Choose one</option>
              {businessTypes.map((t) => <option key={t}>{t}</option>)}
            </select>
            <small className="err">{errors.biz}</small>

            <button type="submit" className="btn">Request demo</button>

            {sentTo && (
              <p className="success" role="status">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <path className="check" d="M4 12.5l5 5L20 6.5" />
                </svg>
                <span>Thanks {sentTo.name}, your demo request is in. We will email {sentTo.email} soon.</span>
              </p>
            )}
          </form>
        </Reveal>
      </div>
    </section>
  );
}
