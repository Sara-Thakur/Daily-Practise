# Slotbook - React version

Front-end internship assignment for Sankar Group, by Sara Thakur.
Slotbook is an invented booking tool for small businesses (salons, clinics, tutors).

## Setup
You need Node.js 18 or newer.

    npm install
    npm run dev       # opens at http://localhost:5173
    npm run build     # production build in /dist

## Technologies
- React 18 (function components and hooks)
- Vite
- Plain CSS (custom properties, grid, flexbox, keyframes)

## Structure
    src/
      main.jsx            entry point
      App.jsx             page layout, one component per section
      data.js             text, features, steps and pricing plans
      index.css           all styles and animations
      assets/             hero-pattern.svg (the image inside the headline)
      hooks/               useReveal (scroll fade-in), useScrollSpy (active nav link)
      components/         Navbar, Hero, Features (flip cards), HowItWorks, Pricing, Contact, Footer,
                          Reveal, AnimatedNumber, ScrollProgress, BackToTop

## Interactions
- Nav links and buttons scroll to their sections; the menu opens and closes on mobile
- Hero headline has a picture inside the letters that moves with the mouse
- Hero calendar books its own open slots until you click one, then you control it
- Feature cards flip on hover (tap on phones, focus on keyboard)
- Pricing has a monthly / yearly switch and the prices count up or down
- Nav link highlights the section you are on, a bar shows scroll progress, and a back-to-top button appears
- Pointer cursor on everything clickable
- Cards, steps and plans fade in as you scroll (once)
- Demo form validates name, email and business type, shows errors, then a success message (no backend)
- Animations are turned off for people who set "reduce motion"

## Deploy
Push to GitHub and import the repo in Vercel or Netlify (build command `npm run build`, output `dist`).

## Design notes
- I invented Slotbook, a booking tool for small businesses, so the page copy talks to salon owners and tutors instead of using generic SaaS text.
- I used a deep blue and white palette with a yellow accent for highlights, and paired Bricolage Grotesque headings with Source Sans 3 body text so the hierarchy is clear.
- The hero headline has an image inside the letters, done with background-clip: text. The image moves with the mouse, and the hero calendar lets visitors book a slot, which shows what the product does.
- I built the page in React with one component per section and kept all the text in a single data.js file. I used small hooks for scroll animations and for highlighting the active nav link.
- The feature cards flip on hover, and I made them flip on tap for touch screens and on focus for keyboard users. This was the trickiest part, because hover doesn’t exist on phones.
- The demo form checks the name, email and business type, shows an error under each field, and then shows a success message. The layout switches to one column below 820px, and animations switch off for visitors who have “reduce motion” turned on.
