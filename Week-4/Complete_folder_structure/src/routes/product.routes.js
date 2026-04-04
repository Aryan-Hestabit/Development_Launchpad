const express = require("express");
const controller = require("../controllers/product.controller");
const validate = require("../middlewares/validate");
const productSchema = require("../validators/product.schema");

const router = express.Router();

router.post("/", validate(productSchema), controller.create);
router.get("/", controller.getAll);
router.get("/:id", controller.getById);
router.delete("/:id", controller.delete);

module.exports = router;
