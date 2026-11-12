import useReveal from "../hooks/useReveal.js";

// Wraps content and fades it in when scrolled into view. `delay` staggers siblings.
export default function Reveal({ children, delay = 0, as: Tag = "div", className = "" }) {
  const [ref, shown] = useReveal();
  return (
    <Tag
      ref={ref}
      className={`reveal ${shown ? "in" : ""} ${className}`}
      style={{ "--d": `${delay}ms` }}
    >
      {children}
    </Tag>
  );
}
