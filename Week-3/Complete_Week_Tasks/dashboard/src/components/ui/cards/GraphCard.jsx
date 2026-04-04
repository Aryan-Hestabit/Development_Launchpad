export default function GraphCard({
  title,
  hasData = false,
  children,
  ...props
}) {
  const base =
    "shadow-gray-600/50 transition-transform duration-200 hover:scale-105 hover:shadow-sm";

  return (
    <div
      className={`bg-gray-300 text-gray-700 rounded-lg shadow-lg ${base}`}
      {...props}
    >
      {/* Header */}
      <div className="px-4 py-3 shadow-md shadow-gray-500/50 font-semibold bg-gray-400 rounded-t-lg">
        {title}
      </div>

      {/* Content */}
      <div className="p-4 h-64">
        {hasData ? (
          <div className="h-full w-full">{children}</div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-gray-400">
            <div className="w-3/4 h-32 bg-gradient-to-r from-gray-200 to-gray-300 rounded-b-lg opacity-50" />
            <p className="mt-4 text-sm">Enter your data</p>
          </div>
        )}
      </div>
    </div>
  );
}
