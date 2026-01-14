const faqItems = document.querySelectorAll(".faq-item");
const toggleBtn = document.getElementById("toggleBtn");
const navMenu = document.getElementById("navMenu");

toggleBtn.addEventListener("click", () => {
  navMenu.classList.toggle("open");
});

faqItems.forEach(item => {
  const question = item.querySelector(".faq-question");

  question.addEventListener("click", () => {
    faqItems.forEach(i => {
      if (i !== item) {
        i.classList.remove("active");
      }
    });

    item.classList.toggle("active");
  });
});
