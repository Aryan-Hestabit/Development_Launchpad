const logger = require("../utils/logger");

module.exports = async function connectDB() {
  return new Promise((resolve) => {
    setTimeout(() => {
      logger.info("Database connected");
      resolve();
    }, 500);
  });
};
