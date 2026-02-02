const helmet = require("helmet");
const cors = require("cors");
const express = require("express");
const rateLimit = require("express-rate-limit");

module.exports = (app) => {
  // Helmet – secure HTTP headers
  app.use(helmet());

  

  // CORS – allow only known origins (example: local dev)
  app.use(
    cors({
      origin: ["http://localhost:3000"],
      methods: ["GET", "POST", "PUT", "DELETE"],
    })
  );

  // Rate limiting
  app.use(
    rateLimit({
      windowMs: 15 * 60 * 1000,
      max: 100,
      message: "Too many requests, please try again later",
    })
  );

  // Payload size limit
  app.use(express.json({ limit: "10kb" }));
};
