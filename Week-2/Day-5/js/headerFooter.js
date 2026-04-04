document.getElementById("header").innerHTML = `
<header class="navbar">
  <div class="logo">Cart.Co</div>
  <nav>
    <a href="Home.html">Home</a>
    <a href="Categories.html">Categories</a>
    <a href="Catalog.html?sale=true">Sale</a>
    <input id="searchBox" placeholder="Search products">
  </nav>
</header>
`;

document.getElementById("footer").innerHTML = `
<footer>
  <p>© 2014 Cart.co Pvt Ltd</p>
</footer>
`;

document.getElementById("searchBox")?.addEventListener("keypress", e => {
  if (e.key === "Enter") {
    window.location.href = `Catalog.html?search=${e.target.value}`;
  }
});
