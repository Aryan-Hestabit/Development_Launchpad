let allProducts = [];
let filteredProducts = [];

/* -----------------------------
   READ URL PARAMETERS
--------------------------------*/
const params = new URLSearchParams(window.location.search);
const searchQuery = params.get("search")?.toLowerCase() || "";
const saleOnly = params.get("sale") === "true";
const categoryFilter = params.get("category");
const ratingFilter = params.get("rating") === "high";


/* -----------------------------
   INITIAL LOAD
--------------------------------*/
fetchAllProducts().then(products => {
  allProducts = products;
  applyFiltersAndRender();
});

/* -----------------------------
   SORT HANDLER
--------------------------------*/
document.getElementById("sort").addEventListener("change", () => {
  applyFiltersAndRender();
});

/* -----------------------------
   MAIN FILTER PIPELINE
--------------------------------*/
function applyFiltersAndRender() {
  filteredProducts = [...allProducts];

  /* 📂 CATEGORY FILTER */
  if (categoryFilter) {
    filteredProducts = filteredProducts.filter(
      p => p.category === categoryFilter
    );
  }


  /* 🔍 SEARCH FILTER */
  if (searchQuery) {
    filteredProducts = filteredProducts.filter(p =>
      p.title.toLowerCase().includes(searchQuery) ||
      p.brand?.toLowerCase().includes(searchQuery)
    );
  }

  if (ratingFilter){
    filteredProducts = filteredProducts.filter(p => p.rating > 4);
  }

  /* 🔥 SALE FILTER */
  if (saleOnly) {
    filteredProducts = filteredProducts.filter(
      p => p.discountPercentage > 5.0
    );
  }

  /* 🔃 SORTING */
  applySorting();

  /* 🎨 RENDER */
  renderCatalog(filteredProducts);
}

/* -----------------------------
   SORTING LOGIC
--------------------------------*/
function applySorting() {
  const sortValue = document.getElementById("sort").value;

  switch (sortValue) {
    case "plh":
      filteredProducts.sort((a, b) => a.price - b.price);
      break;

    case "phl":
      filteredProducts.sort((a, b) => b.price - a.price);
      break;

    case "ra":
      filteredProducts.sort((a, b) => a.rating - b.rating);
      break;

    case "rd":
      filteredProducts.sort((a, b) => b.rating - a.rating);
      break;

    case "stock-high":
      filteredProducts.sort((a, b) => b.stock - a.stock);
      break;

    case "stock-low":
      filteredProducts.sort((a, b) => a.stock - b.stock);
      break;

    default:
      break;
  }
}

/* -----------------------------
   RENDER CATALOG
--------------------------------*/
function renderCatalog(products) {
  const catalog = document.getElementById("catalog");
  catalog.innerHTML = "";

  if (products.length === 0) {
    catalog.innerHTML = "<p>No products found.</p>";
    return;
  }

  products.forEach(p => {
    const discountedPrice = (
      p.price - (p.price * p.discountPercentage) / 100
    ).toFixed(2);

    const card = document.createElement("article");
    card.className = "product-card";

    card.innerHTML = `
      ${p.discountPercentage > 0 ? `<span class="badge sale">SALE</span>` : ""}
      ${p.stock === 0 ? `<span class="badge out">OUT OF STOCK</span>` : ""}
      ${p.rating > 4 ? `<span class="badge rating high">Highly Rated</span>` : ""}
      ${p.rating < 3 ? `<span class="badge rating low">Low Rated</span>` : ""}

      <img src="${p.thumbnail}" alt="${p.title}">

      <h4>${p.brand}</h4>
      <h3>${p.title}</h3>
      

      <p class="price">
        ${p.discountPercentage > 0 
          ? `<div class="discount"><p class="discountpercentage">${p.discountPercentage}% off</p></div>
          <span class="old">₹${p.price}</span> ₹${discountedPrice}`
          : `₹${p.price}`
        }
      </p>
    `;

    card.addEventListener("click", () => {
      window.location.href = `Product.html?id=${p.id}`;
    });

    catalog.appendChild(card);
  });
}
