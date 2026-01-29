const service = require("../services/product.service");

exports.create = async (req, res, next) => {
  try {
    const product = await service.create(req.body);
    res.status(201).json({ success: true, data: product });
  } catch (err) {
    next(err);
  }
};

exports.getAll = async (req, res, next) => {
  try {
    const products = await service.getAll(req.query);
    res.json({ success: true, data: products });
  } catch (err) {
    next(err);
  }
};

exports.getById = async (req, res, next) => {
  try {
    const product = await service.getById(
      req.params.id,
      req.query.includeDeleted === "true"
    );
    res.json({ success: true, data: product });
  } catch (err) {
    next(err);
  }
};

exports.delete = async (req, res, next) => {
  try {
    const product = await service.delete(req.params.id);
    res.json({ success: true, data: product });
  } catch (err) {
    next(err);
  }
};
