# 🛒 Day 5 – E-Commerce Product Listing Website

## 📌 Project Overview

This project is a **multi-page E-Commerce Product Listing Website** built using **HTML, CSS, and Vanilla JavaScript**.  
The application fetches product data from an external API and dynamically renders products, categories, and product details across different pages.

---
## 🔗 API Used

**DummyJSON Products API**  
```bash
https://dummyjson.com/products
```

1. Checked API using DevTool "Network" Tab:

![API Response]("Images/APIResponse.png")

2. Found that the API has Total of 194 Products, but due to "limit = 30" , Response only shows 30 products

3. Set Parameters:
```bash
https://dummyjson.com/products?limit=0
```

The API provides product data in JSON format including:
- Product name
- Brand
- Category
- Price
- Discount
- Rating
- Stock
- Images
- Description

---

## 🧱 Pages Implemented

### 1️⃣ Home Page (`Home.html`)
### 2️⃣ Categories Page (`Categories.html`)
### 3️⃣ Product Catalog Page (`Catalog.html`)
### 4️⃣ Individual Product Page (`Product.html`)

Each page shares a **common Header and Footer**, injected dynamically using JavaScript.

---

## 🏠 Home Page

### Features
- Fixed header with navigation and search bar
- Feature cards for:
  - Sale
  - Top Rated
  - New Arrivals
- Contact Us section
- Fixed footer

### Screenshot
![Home Page]("Images/Home.png")

---

## 📂 Categories Page

### Features
- Displays all unique product categories dynamically
- Categories are derived directly from API data
- Clicking a category redirects to the Catalog page filtered by that category

### Screenshot
![Categories Page]("Images/Categories.png")

---

## 📦 Product Catalog Page

### Features
- Displays products as **semantic `<article>` cards**
- Product card includes:
  - Thumbnail image
  - Product name
  - Discounted price (with original price slashed)
  - Sale badge (if applicable)
  - Rating badge:
    - “Highly Rated” (rating > 4)
    - “Low Rated” (rating < 3)
  - Out of Stock overlay
- Sorting options:
  - Price (Low → High, High → Low)
  - Rating (Ascending, Descending)
  - Stock (High → Low, Low → High)
- Filters supported via URL:
  - Search
  - Sale
  - Category
- Clicking a product opens its detailed product page

### Screenshot
![Catalog Page]("Images/Catalog.png")

---

## 🛍️ Product Page

### Features
- Displays detailed information of a single product
- Includes:
  - Product name and brand
  - Product image
  - Discounted price and discount percentage
  - Detailed description
- Similar products section:
  - Products from the same category
  - Clickable cards redirect to respective product pages
- Header and footer remain fixed while content scrolls

### Screenshot
![Product Page]("Images/Product1.png")
![Product Page]("Images/Product2.png")

---

## 🔄 Navigation & Linking Flow

- **Navbar**
  - Home → `Home.html`
  - Categories → `Categories.html`
  - Sale → `Catalog.html?sale=true`
  - Search → `Catalog.html?search=keyword`

- **Categories Page**
  - Clicking a category → `Catalog.html?category=category_name`

- **Catalog Page**
  - Clicking a product → `Product.html?id=product_id`

- **Home Feature Cards**
  - Sale → Catalog filtered by sale products
  - Top Rated → Catalog filtered by high rating

---

## 🧠 Working Logic Summary

- Data is fetched once from the API and reused where required
- URL query parameters control:
  - Search
  - Category filtering
  - Sale filtering
  - Sorting
- Header and footer are injected dynamically using JavaScript
- Layout uses fixed header and footer with scrollable main content
- Semantic HTML elements (`<article>`, `<main>`, `<section>`) are used for better structure

