// hero section slide functionality start
const slides = document.getElementById("slides");
const prevBtn = document.getElementById("prev");
const nextBtn = document.getElementById("next");

let index = 0;
const total = slides.children.length;

function updateSlide() {
  slides.style.transform = `translateX(-${index * 100}%)`;
}

nextBtn.addEventListener("click", () => {
  index = (index + 1) % total;
  updateSlide();
});

prevBtn.addEventListener("click", () => {
  index = (index - 1 + total) % total;
  updateSlide();
});
// hero section slide functionality end
//Login & Signup functionality start
const userLoginBtn = document.getElementById("userLoginBtn");
const adminLoginBtn = document.getElementById("adminLoginBtn");

userLoginBtn.onclick = () => {
  window.location.href = "/login";
};
adminLoginBtn.onclick = () => {
  window.location.href = "/AdminLogin";
};

function goToMovie(movieId) {
  window.location.href = `/movie?movie_id=${movieId}`;
};