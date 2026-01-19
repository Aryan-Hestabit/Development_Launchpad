const API_URL = "https://dummyjson.com/products?limit=0";

async function fetchAllProducts() {
  const res = await fetch(API_URL);
  const data = await res.json();
  return data.products;
}

async function fetchProductById(id) {
  const res = await fetch(`https://dummyjson.com/products/${id}`);
  return res.json();
}
