const loginBox = document.getElementById("loginBox");
const signupBox = document.getElementById("signupBox");
const errorMsg = document.getElementById("errorMsg");

// Show Signup form
// function showSignup() {
//   loginBox.style.display = "none";
//   signupBox.style.display = "block";
//   errorMsg.textContent = "";
// }

// // Show Login form
// function showLogin() {
//   signupBox.style.display = "none";
//   loginBox.style.display = "block";
//   errorMsg.textContent = "";
// }

// document.getElementById("adminSignupForm").addEventListener("submit", function (e) {
//   const password = document.getElementById("signupPass").value;
//   if (password.length < 6) {
//     e.preventDefault();
//     errorMsg.textContent = "Password must be at least 6 characters long.";
//   }
// });

document.getElementById("adminLoginForm").addEventListener("submit", function (e) {
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPass").value;
  if (!email || !password) {
    e.preventDefault();
    errorMsg.textContent = "Email and password are required.";
  }
});

// Admin Signup (demo – stored in localStorage)
// document.getElementById("adminSignupForm").addEventListener("submit", function (e) {
//   e.preventDefault();

//   const username = document.getElementById("signupUser").value;
//   const email = document.getElementById("signupEmail").value;
//   const password = document.getElementById("signupPass").value;

//   localStorage.setItem("adminUser", username);
//   localStorage.setItem("adminEmail", email);
//   localStorage.setItem("adminPass", password);

//   alert("Admin registered successfully!");
//   showLogin();
// });

// // Admin Login
// document.getElementById("adminLoginForm").addEventListener("submit", function (e) {
//   e.preventDefault();

//   const username = document.getElementById("loginUser").value;
//   const password = document.getElementById("loginPass").value;

//   const savedUser = localStorage.getItem("adminUser");
//   const savedPass = localStorage.getItem("adminPass");

//   if (username === savedUser && password === savedPass) {
//     window.location.href = "/adminDashbord";
//   } else {
//     errorMsg.textContent = "Invalid admin username or password!";
//   }
// });
