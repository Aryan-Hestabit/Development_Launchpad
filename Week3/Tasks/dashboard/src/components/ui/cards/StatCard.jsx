export default function StatCard({
  title,
  color = "gray",
  onViewDetails,
  ...props
}) {
  const base =
    "outset-shadow-lg transition-transform duration-200 hover:scale-105 hover:shadow-sm rounded-lg";

  const colorMap = {
    gray: "bg-gray-200 text-gray-600 border border-gray-600 shadow-gray-600/60",
    blue: "bg-blue-200 text-blue-600 border border-blue-600 shadow-blue-500/60",
    yellow:
      "bg-yellow-200 text-yellow-600 border border-yellow-600 shadow-yellow-500/60",
    green:
      "bg-green-200 text-green-600 border border-green-600 shadow-green-500/60",
    red: "bg-red-200 text-red-600 border border-red-600 shadow-red-500/60",
  };

  const bgColor = colorMap[color] || colorMap.gray;

  return (
    <div className={`${bgColor} ${base}`} {...props}>
      <div className="p-4 text-lg font-semibold">{title}</div>

      <div
        onClick={onViewDetails}
        className="flex items-center justify-between px-4 py-3 bg-black/10 hover:bg-black/20 cursor-pointer text-sm"
      >
        <span>View Details</span>
        <span>➜</span>
      </div>
    </div>
  );
}
