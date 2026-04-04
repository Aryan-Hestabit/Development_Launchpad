const service = require("../services/product.service");
const logger = require("../utils/logger");

exports.create = async (req, res, next) => {
  try {
    logger.info("creating Product", {requestId: req.requestId});

    const product = await service.create(req.body);

    logger.info("Product created successfully",{
      requestId: req.requestId,
    })
    res.status(201).json({ success: true, data: product });
  } catch (err) {
    logger.error(err.message,{requestId: req.requestId});
    next(err);
  }
};

exports.getAll = async (req, res, next) => {
  try {
    logger.info("creating Product", {requestId: req.requestId});

    const products = await service.getAll(req.query);
    logger.info("Product created successfully",{
      requestId: req.requestId,
    })
    res.json({ success: true, data: products });
  } catch (err) {
    logger.error(err.message,{requestId: req.requestId});
    
    next(err);
  }
};

exports.getById = async (req, res, next) => {
  try {
    logger.info("creating Product", {requestId: req.requestId});

    const product = await service.getById(
      req.params.id,
      req.query.includeDeleted === "true"
    );

    logger.info("Product created successfully",{
      requestId: req.requestId,
    })
    res.json({ success: true, data: product });
  } catch (err) {
    logger.error(err.message,{requestId: req.requestId});

    next(err);
  }
};

exports.delete = async (req, res, next) => {
  try {
    logger.info("creating Product", {requestId: req.requestId});

    const product = await service.delete(req.params.id);
    logger.info("Product created successfully",{
      requestId: req.requestId,
    })
    res.json({ success: true, data: product });
  } catch (err) {
    logger.error(err.message,{requestId: req.requestId});

    next(err);
  }
};
