const signUpBtn = document.getElementById("signUpBtn");
const loginBtn = document.getElementById("loginBtn");
const container = document.querySelector(".container");
const loginForm = document.getElementById("loginForm");
const signupForm = document.getElementById("signupForm");

signUpBtn.onclick = () => {
  container.classList.add("signup");
  loginForm.classList.remove("active");
  signupForm.classList.add("active");
};

loginBtn.onclick = () => {
  container.classList.remove("signup");
  signupForm.classList.remove("active");
  loginForm.classList.add("active");
};

