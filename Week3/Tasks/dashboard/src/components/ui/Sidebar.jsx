import Link from "next/link";

export default function Sidebar({ isOpen }) {
  if (!isOpen) return null;

  return (
    <aside className="w-64 min-h-screen bg-gray-900 text-gray-300">
      <nav className="p-4 space-y-10">
        <div>
          <p className="text-xs text-gray-500 mb-2">CORE</p>
          <Link className="block px-3 py-2 rounded hover:bg-gray-800 text-white" href="/">
            Home
          </Link>
        </div>

        <div>
          <p className="text-xs text-gray-500 mb-2">INTERFACE</p>
          <Link className="block px-3 py-2 rounded hover:bg-gray-800" href="/dashboard">
            Dashboard
          </Link>
          <Link className="block px-3 py-2 rounded hover:bg-gray-800" href="/about">
            About
          </Link>
        </div>

        <div>
          <p className="text-xs text-gray-500 mb-2">PROFILE</p>
          <Link className="block px-3 py-2 rounded hover:bg-gray-800" href="/dashboard/profile" >
            Your Profile
          </Link>
          <Link className="block px-3 py-2 rounded hover:bg-gray-800" href="/login">
            Login
          </Link>
        </div>
      </nav>
    </aside>
  );
}
