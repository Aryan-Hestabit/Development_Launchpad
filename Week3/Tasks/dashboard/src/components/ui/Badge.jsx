export default function Badge({ children, type = "default", color }) {
  const baseClasses = "items-center px-4 py-3 font-semibold rounded-full";

  const statusStyles = {
    critical: "bg-red-100 text-red-700",
    success: "bg-green-100 text-green-700",
    pending: "bg-yellow-100 text-yellow-700",
    default: "bg-gray-100 text-gray-700",
  };

  // If custom color is provided, it takes priority
  const style = color
    ? `bg-${color}-100 text-${color}-700`
    : statusStyles[type] || statusStyles.default;

  return <span className={`${baseClasses} ${style}`}>{children}</span>;
}
