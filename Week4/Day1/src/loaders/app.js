const express = require("express");
const logger = require("../utils/logger");
const config = require("../config");
const connectDB = require("./db");

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

  // Load routes (placeholder)
  app.get("/health", (_, res) => res.send("OK"));
  logger.info("Routes mounted: 1 endpoint");

  // Start server
  app.listen(config.port, () => {
    logger.info(`Server started on port ${config.port}`);
  });
};
