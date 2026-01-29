const express = require("express");
const connectDB = require("./db");
const config = require("../config");
const logger = require("../utils/logger");

const productRoutes = require("../routes/product.routes");
const userRoutes = require("../routes/user.routes");
const errorMiddleware = require("../middlewares/error.middleware");

module.exports = async function startApp() {
  const app = express();

  app.use(express.json());
  logger.info("Middlewares loaded");

  await connectDB();

  app.get("/", (_, res) => res.send("Server running"));
  app.get("/health", (_, res) => res.send("health OK"));

  app.use("/products", productRoutes);
  app.use("/users", userRoutes);

  logger.info("Routes mounted: /products, /users");

  app.use(errorMiddleware);

  app.listen(config.port, () => {
    logger.info(`Server started on port ${config.port}`);
  });
};
