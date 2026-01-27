"use client";

import "./globals.css";
import { useState } from "react";
import Navbar from "@/components/ui/Navbar";
import Sidebar from "@/components/ui/Sidebar";

export default function RootLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <html lang="en">
      <body>
        <Navbar toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

        <div className="flex ">
          <Sidebar isOpen={sidebarOpen} />

          <main className="flex-1 bg-gray-100 min-h-screen">{children}</main>
        </div>
      </body>
    </html>
  );
}
