export default function DataTableCard({
  title = "DataTable Card",
  hasData = false,
  columns = [],
  data = [],
  ...props
}) {
  return (
    <div
      className="bg-white rounded-lg shadow-lg transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-md"
      {...props}
    >
      {/* Title */}
      <div className="px-4 py-3 border-b bg-gray-400 text-gray-700 rounded-t-lg font-semibold">
        {title}
      </div>

      {/* Body */}
      <div className="p-4">
        {!hasData && (
          <div className="text-gray-700 text-center py-10">
            <div className="border border-dashed rounded p-6">
              No data available
            </div>
          </div>
        )}

        {hasData && (
          <table className="w-full text-sm border table-auto">
            <thead className="bg-gray-300 text-gray-600">
              <tr>
                {columns.map((col) => (
                  <th key={col} className="px-3 py-2 border text-left">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody className="text-gray-700">
              {data.map((row, i) => (
                <tr key={i} className="hover:bg-gray-200">
                  {columns.map((col) => (
                    <td key={col} className="px-3 py-2 border">
                      {row[col]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
