fetchAllProducts().then(products => {
  const categories = [...new Set(products.map(p => p.category))];

  const container = document.getElementById("categories");

  categories.forEach(cat => {
    const card = document.createElement("div");
    card.className = "category-card";
    card.innerText = cat.toUpperCase();

    card.onclick = () => {
      window.location.href = `Catalog.html?category=${cat}`;
    };

    container.appendChild(card);
  });
});
