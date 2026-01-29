const express = require("express");
const logger = require("../utils/logger");
const config = require("../config");
const connectDB = require("./db");
const User = require("../models/User");
const Product = require("../models/Product");

module.exports = async function startApp() {
  const app = express();

  // Load middlewares
  app.use(express.json());
  logger.info("Middlewares loaded");

  // Load DB
  await connectDB();

  app.get("/", (_, res) => {
    res.send("Server is running");
  });

  app.get("/test-db", async (_, res) => {
    const user = await User.create({
      firstName: "Test",
      lastName: "User",
      email: "test@example.com",
      password: "password123",
    });
    const product = await Product.create({
      name: "Laptop",
      status: "active",
      description: "User interface",
      price: 20000,
      ratingCount: 100,
      ratingSum: 40,
    });
    res.json({user,product});
  });

  // Load routes (placeholder)
  app.get("/health", (_, res) => res.send("OK"));
  logger.info("Routes mounted: 1 endpoint");

  // Start server
  app.listen(config.port, () => {
    logger.info(`Server started on port ${config.port}`);
  });
};
