const service = require("../services/user.service");
const emailQueue = require("../jobs/email.job");
const logger = require("../utils/logger");

exports.create = async (req, res, next) => {
  try {
    const user = await service.create(req.body);
    await emailQueue.add("welcome-email", {
      email: user.email,
    });

    logger.info("User created & email job queued", {
      requestId: req.requestId,
    });
    res.status(201).json({ success: true, data: user });
  } catch (err) {
    next(err);
  }
};

exports.getById = async (req, res, next) => {
  try {
    const user = await service.getById(req.params.id);
    await emailQueue.add("welcome-email", {
      email: user.email,
    });

    logger.info("User created & email job queued", {
      requestId: req.requestId,
    });
    res.json({ success: true, data: user });
  } catch (err) {
    next(err);
  }
};
