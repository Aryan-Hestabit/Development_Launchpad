module.exports = {
  apps: [
    {
      name: "backend-api",
      script: "src/index.js",

      // Run one instance per CPU core
      instances: "max",
      exec_mode: "cluster",

      // Restart on crash
      autorestart: true,

      // Environment variables
      env: {
        NODE_ENV: "prod",
      },
    },
  ],
};
