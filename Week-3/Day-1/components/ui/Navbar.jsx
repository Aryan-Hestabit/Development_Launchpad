"use client";

import Input from "@/components/ui/Input";
import Link from "next/link";
import { useState } from "react";

export default function Navbar({ toggleSidebar }) {
  const [open, setOpen] = useState(false);

  return (
    <header className="h-14 bg-gray-800 text-white flex items-center justify-between px-4 py-8">
      
      {/* LEFT: Hamburger + Brand */}
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="text-lg focus:outline-none lg:text-2xl md:text-xl"
        >
          ☰
        </button>

        <span className="font-semibold sm:text-xl md:text-2xl lg:text-3xl sm:block">
          StoreFlow
        </span>
      </div>

      {/* RIGHT: Search + Avatar */}
      <div className="flex items-center gap-4">
        
        {/* Search */}
        <Input type="search"></Input>

        {/* Avatar */}
        <div className="relative">
          <button
            onClick={() => setOpen(!open)}
            className="w-11 h-11 rounded-full bg-gray-600 flex items-center justify-center"
          >
            👤
          </button>

          {open && (
            <div className="absolute right-0 mt-2 w-40 bg-white text-gray-800 rounded shadow">
              <Link className="block px-4 py-2 hover:bg-gray-100" href="/dashboard/profile">
                Profile
              </Link>
              <Link className="block px-4 py-2 hover:bg-gray-100" href="/dashboard/users">
                Users
              </Link>
              <a className="block px-4 py-2 hover:bg-gray-100">
                Settings
              </a>
              <hr />
              <Link className="block px-4 py-2 hover:bg-gray-100 text-red-600" href="/login">
                Logout
              </Link>
            </div>
          )}
        </div>

      </div>
    </header>
  );
}
