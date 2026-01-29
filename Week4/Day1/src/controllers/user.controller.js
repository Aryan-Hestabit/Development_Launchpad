const service = require("../services/user.service");

exports.create = async (req, res, next) => {
  try {
    const user = await service.create(req.body);
    res.status(201).json({ success: true, data: user });
  } catch (err) {
    next(err);
  }
};

exports.getById = async (req, res, next) => {
  try {
    const user = await service.getById(req.params.id);
    res.json({ success: true, data: user });
  } catch (err) {
    next(err);
  }
};
