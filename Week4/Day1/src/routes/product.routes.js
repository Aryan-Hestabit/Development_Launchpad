const express = require("express");
const controller = require("../controllers/product.controller");

const router = express.Router();

router.post("/", controller.create);
router.get("/", controller.getAll);
router.get("/:id", controller.getById);
router.delete("/:id", controller.delete);

module.exports = router;
