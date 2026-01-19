const id = new URLSearchParams(window.location.search).get("id");

fetchProductById(id).then(p => {
  document.getElementById("product").innerHTML = `
    <h1>${p.title}</h1>
    <h3>${p.brand}</h3>
    <img src="${p.thumbnail}">
    <p id="price"><del>₹${p.price}</del> ₹${(p.price - p.price*p.discountPercentage/100).toFixed(0)}</p>
    <div class="Productinfo">
      <section class="InfoTitle">
        <h1>Product Info</h1>
      </section>
      <section class="Description">
        <h2>Description</h2>
        <p class="description">${p.description}</p>
      </section>
      <section class="Rating">
        <h2>Rating</h2>
        <p class ="rating">${p.rating}/5</p>
      </section>
      <section class="Warranty">
        <h2>Warranty</h2>
        <p class ="warranty">${p.warrantyInformation}</p>
      </section>
      <section class="Shipping">
        <h2>Shipping</h2>
        <p class ="shipping">${p.shippingInformation}</p>
      </section>
      <section class="Return">
        <h2>Rrturn Policy</h2>
        <p class ="retrun">${p.returnPolicy}</p>
      </section>
    </div>
  `;

  fetchAllProducts().then(all => {
    const similar = all.filter(x =>
      x.category === p.category && x.id !== p.id
    ).slice(0,4);

    document.getElementById("similar").innerHTML =
      similar.map(s => `
        <article onclick="location.href='Product.html?id=${s.id}'" class="similarProduct">
          <img src="${s.thumbnail}" width="100">
          <p class="similartext">${s.title}</p>
        </article>
      `).join("");
  });
});
