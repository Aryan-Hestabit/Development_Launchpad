"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export default function Home() {
  const [products, setProducts] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch("/api/products")
      .then((res) => res.json())
      .then((data) => setProducts(data.products || data));

    fetch("/api/stats")
      .then((res) => res.json())
      .then((data) => setStats(data));
  }, []);

  return (
    <div className="p-7">
      <h1 className="text-3xl font-bold mb-5">Products</h1>
      <div className="flex gap-5 items-start">
        <aside className="flex-none w-80">
          <div className="card">
            <h2 className="mt-0 text-xl font-semibold">Dashboard</h2>
            {stats ? (
              <div>
 
                <p className="my-1.5">
                  Total products: {stats.overall?.totalProducts || 0}
                </p>
                <p className="my-1.5">
                  Total quantity: {stats.overall?.totalQuantity || 0}
                </p>
                <p className="my-1.5">
                  Inventory value: ₹
                  {Math.round((stats.overall?.totalValue || 0) * 100) / 100}
                </p>

                <h3 className="mt-3">By Category</h3>
                <div>
                  {stats.byCategory.length ? (
                    stats.byCategory.map((c) => (
                      <div
                        key={c.category}
                        className="p-2 rounded-md bg-gray-50 mb-2"
                      >
                        <strong>{c.category}</strong>
                        <div className="text-sm">
                          {c.count} products · qty {c.totalQuantity} · avg ₹
                          {Math.round((c.avgPrice || 0) * 100) / 100}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div>No categories</div>
                  )}
                </div>
              </div>
            ) : (
              <p>Loading stats...</p>
            )}
          </div>
        </aside>

        <main className="flex-1">
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {products.map((p) => (
              <div key={p._id} className="card">
                <h3 className="mb-1 text-lg font-semibold">{p.name}</h3>
                <div className="text-sm text-gray-500 mb-2">
                  {p.category} · qty {p.quantity}
                </div>
                <div className="mb-2">₹{p.price}</div>
                <div className="text-sm text-gray-700 dark:text-gray-300">
                  {p.description}
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
