const mongoose = require("mongoose");
const logger = require("../utils/logger");
const config = require("../config");

module.exports = async function connectDB() {
  try {
    await mongoose.connect(config.dbUrl);
    logger.info("Database connected");
  } catch (error) {
    logger.error("Database connection failed");
    process.exit(1);
  }
};
