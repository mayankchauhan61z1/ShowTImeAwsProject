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

// 1. Handle Flash Message disappearance
const flashBox = document.getElementById('flash-container');
if (flashBox) {
    setTimeout(() => {
        flashBox.style.transition = "opacity 0.5s";
        flashBox.style.opacity = "0";
        setTimeout(() => flashBox.remove(), 500);
    }, 3000);

    // 2. Logic to switch to Signup view if an account error exists
    const allMessages = document.querySelectorAll('.flash-message');
    allMessages.forEach(msg => {
        const text = msg.getAttribute('data-msg').toLowerCase();
        if (text.includes("exists") || text.includes("registered")) {
            // This matches your existing JS variables
            container.classList.add("signup");
            loginForm.classList.remove("active");
            signupForm.classList.add("active");
        }
    });
}
