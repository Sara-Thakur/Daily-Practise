// All the page content lives here so the components stay short.

export const navLinks = [
  { href: "#features", label: "Features" },
  { href: "#how", label: "How it works" },
  { href: "#pricing", label: "Pricing" },
  { href: "#contact", label: "Contact" },
];

export const features = [
  {
    title: "Your own booking page",
    text: "Share one link on Instagram, WhatsApp or your shop window. Clients pick a service and a time that is actually free.",
    icon: "M3 6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM8 2v4M16 2v4M3 10h18",
  },
  {
    title: "Automatic reminders",
    text: "Clients get a message the day before. Fewer forgotten appointments, fewer empty chairs.",
    icon: "M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0",
  },
  {
    title: "Team schedules",
    text: "Add staff, set their working hours and days off. Slotbook never double-books anyone.",
    icon: "M16 20v-1.5a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4V20M9.5 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7M21 20v-1.5a4 4 0 0 0-3-3.9M15.5 4.2a3.5 3.5 0 0 1 0 6.6",
  },
];

export const steps = [
  { title: "Add your services", text: "List what you offer, how long each takes and the price." },
  { title: "Set your hours", text: "Choose the days and times you work. Block off holidays in a click." },
  { title: "Share your link", text: "Clients book on their phone and you see it in your calendar right away." },
];

export const plans = [
  { name: "Solo", price: 499, perks: ["1 staff calendar", "Up to 100 bookings a month", "Email reminders"] },
  { name: "Studio", price: 1299, featured: true, perks: ["Up to 5 staff calendars", "Unlimited bookings", "SMS and email reminders"] },
  { name: "Chain", price: 3499, perks: ["Multiple locations", "Unlimited staff", "Priority support"] },
];

export const businessTypes = ["Salon or spa", "Clinic", "Tutor or coach", "Other"];
