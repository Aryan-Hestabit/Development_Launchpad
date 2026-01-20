export default function Badge({ label, color = "blue" }) {
  const colors = {
    blue: "bg-blue-100 text-blue-700",
    green: "bg-green-100 text-green-700",
    yellow: "bg-yellow-100 text-yellow-700",
    red: "bg-red-100 text-red-700",
  };

  return (
    <span
      className={`text-s px-2 py-1 rounded ${colors[color]}`}
    >
      {label}
    </span>
  );
}
