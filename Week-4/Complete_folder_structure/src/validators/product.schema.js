const Joi = require("joi");

module.exports = Joi.object({
  name: Joi.string().trim().min(2).required(),
  description: Joi.string().allow(""),
  price: Joi.number().min(0).required(),
  tags: Joi.array().items(Joi.string()),
});
