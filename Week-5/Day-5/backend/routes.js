const express = require("express");
const { productSchema } = require("./validation");

module.exports = (Product, instanceId) => {
  const router = express.Router();

  router.get("/products", async (req, res) => {
    try {
      const products = await Product.find();
      res.json({ servedBy: instanceId, products });
    } catch (err) {
      console.error('GET /api/products error', err);
      res.status(500).json({ error: 'Internal Server Error' });
    }
  });

  // Stats per category and overall
  router.get("/stats", async (req, res) => {
    try {
      const byCategory = await Product.aggregate([
        {
          $group: {
            _id: "$category",
            count: { $sum: 1 },
            totalQuantity: { $sum: { $ifNull: ["$quantity", 0] } },
            avgPrice: { $avg: { $ifNull: ["$price", 0] } },
            totalValue: { $sum: { $multiply: [{ $ifNull: ["$price", 0] }, { $ifNull: ["$quantity", 0] }] } }
          }
        },
        { $project: { category: "$_id", _id: 0, count: 1, totalQuantity: 1, avgPrice: 1, totalValue: 1 } }
      ]);

      const overall = await Product.aggregate([
        {
          $group: {
            _id: null,
            totalProducts: { $sum: 1 },
            totalQuantity: { $sum: { $ifNull: ["$quantity", 0] } },
            totalValue: { $sum: { $multiply: [{ $ifNull: ["$price", 0] }, { $ifNull: ["$quantity", 0] }] } }
          }
        },
        { $project: { _id: 0, totalProducts: 1, totalQuantity: 1, totalValue: 1 } }
      ]);

      res.json({ servedBy: instanceId, byCategory, overall: overall[0] || { totalProducts: 0, totalQuantity: 0, totalValue: 0 } });
    } catch (err) {
      console.error('GET /api/stats error', err);
      res.status(500).json({ error: 'Internal Server Error' });
    }
  });

  router.post("/products", async (req, res) => {
    try {
      const { error } = productSchema.validate(req.body);
      if (error) return res.status(400).json({ error: error.message });

      const product = new Product(req.body);
      await product.save();
      res.status(201).json({ servedBy: instanceId, product });
    } catch (err) {
      console.error('POST /api/products error', err);
      res.status(500).json({ error: 'Internal Server Error' });
    }
  });

  return router;
};
