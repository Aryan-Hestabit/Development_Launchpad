export default function DashboardLayout({ children }) {
  return (
    <div className="bg-gray-200 h-full space-y-6 p-6">
      <h1 className="text-2xl text-black font-semibold">Dashboard</h1>
      {children}
    </div>
  );
}
