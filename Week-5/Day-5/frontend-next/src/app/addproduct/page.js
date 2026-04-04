"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function AddProduct() {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [quantity, setQuantity] = useState(1);
  const router = useRouter();

  async function handleSubmit(e) {
    e.preventDefault();

    const res = await fetch("/api/products", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        price: Number(price),
        description,
        category,
        quantity: Number(quantity),
      }),
    });

    if (res.ok) {
      router.push("/");
    } else {
      alert("Failed to add product");
    }
  }

  return (
    <div className="flex justify-center p-7">
      <div className="card w-[640px]">
        <h1 className="mt-0 text-2xl font-bold">Add Product</h1>

        <form onSubmit={handleSubmit} className="border-md grid gap-3">
          <label>
            <div className="text-sm mb-1.5">Product Name</div>
            <input
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full"
            />
          </label>

          <div className="flex gap-3">
            <label className="flex-1">
              <div className="text-sm mb-1.5">Price</div>
              <input
                required
                type="number"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                className="w-full"
              />
            </label>

            <label className="flex-1">
              <div className="text-sm mb-1.5">Quantity</div>
              <input
                required
                type="number"
                min={0}
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                className="w-full"
              />
            </label>
          </div>

          <label>
            <div className="text-sm mb-1.5">Category</div>
            <input
                required
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full"
            />
          </label>

          <label>
            <div className="text-sm mb-1.5">Description</div>
            <textarea
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full"
            />
          </label>

          <div className="flex justify-end mt-1.5">
            <button
              type="submit"
              className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
            >
              Add Product
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
