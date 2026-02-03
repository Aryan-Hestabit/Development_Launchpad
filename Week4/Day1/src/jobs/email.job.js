const { Queue, Worker } = require("bullmq");
const logger = require("../utils/logger");

const connection = {
  host: "127.0.0.1",
  port: 6379,
};

// Queue
const emailQueue = new Queue("email-queue", { connection });

// Worker
new Worker(
  "email-queue",
  async (job) => {
    logger.info(`[JOB:${job.id}] Sending email to ${job.data.email}`);

    // Simulate email sending
    await new Promise((resolve) => setTimeout(resolve, 2000));

    logger.info(`[JOB:${job.id}] Email sent successfully`);
  },
  {
    connection,
    attempts: 3,
    backoff: { type: "exponential", delay: 2000 },
  }
);

module.exports = emailQueue;
