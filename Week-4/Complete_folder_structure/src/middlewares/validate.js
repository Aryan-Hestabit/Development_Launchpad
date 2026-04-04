const AppError = require("../utils/appError");

module.exports = (schema) => (req, res, next) => {
  const { error } = schema.validate(req.body, { abortEarly: false });

  if (error) {
    const message = error.details.map(d => d.message).join(", ");
    return next(new AppError(message, 400, "VALIDATION_ERROR"));
  }

  next();
};
