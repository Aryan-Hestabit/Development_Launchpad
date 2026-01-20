export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 text-gray-200 p-4">
      <nav className="space-y-6">

        <div>
          <h2 className="text-xs uppercase text-gray-400 mb-2">Core</h2>
          <a className="block px-3 py-2 rounded bg-gray-800">
            Dashboard
          </a>
        </div>

        <div>
          <h2 className="text-xs uppercase text-gray-400 mb-2">Interface</h2>
          <a className="block px-3 py-2 rounded hover:bg-gray-800">
            Layouts
          </a>
          <a className="block px-3 py-2 rounded hover:bg-gray-800">
            Pages
          </a>
        </div>

        <div>
          <h2 className="text-xs uppercase text-gray-400 mb-2">Addons</h2>
          <a className="block px-3 py-2 rounded hover:bg-gray-800">
            Charts
          </a>
          <a className="block px-3 py-2 rounded hover:bg-gray-800">
            Tables
          </a>
        </div>

      </nav>
    </aside>
  );
}
