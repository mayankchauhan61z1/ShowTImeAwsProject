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
//Login & Signup functionality
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

// Search functionality start
const searchInput = document.getElementById("searchInput");
// const searchLogo = document.getElementById("searchlogo");

// Trigger search on magnifying glass click
// searchLogo.addEventListener("click", () => {
//   let query = searchInput.value.trim();
//   if (query) {
//     window.location.href = "/search?query=" + encodeURIComponent(query);
//   }
// });

// Trigger search on Enter key
searchInput.addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    let query = searchInput.value.trim();
    if (query) {
      window.location.href = "/search?query=" + encodeURIComponent(query);
    }
  }
});
// Search functionality end

// Live search dropdown functionality
const searchDropdown = document.createElement("div");
searchDropdown.id = "searchDropdown";
searchDropdown.className = "dropdown";
document.body.appendChild(searchDropdown);

searchInput.addEventListener("input", async () => {
  let query = searchInput.value.trim();

  if (query.length > 0) {
    try {
      let response = await fetch(`/search_suggestions?query=${encodeURIComponent(query)}`);
      let results = await response.json();

      // Position dropdown below input
      const rect = searchInput.getBoundingClientRect();
      searchDropdown.style.position = "absolute";
      searchDropdown.style.left = rect.left + "px";
      searchDropdown.style.top = rect.bottom + "px";
      searchDropdown.style.width = rect.width + "px";

      // Clear old results
      searchDropdown.innerHTML = "";

      if (results.length > 0) {
        results.forEach(movie => {
          let item = document.createElement("div");
          item.className = "dropdown-item";
          item.textContent = `${movie.title} (${movie.genre})`;
          item.onclick = () => {
            // Redirect directly to booking page
            window.location.href = `/movie/${movie.movie_id}`;
          };
          searchDropdown.appendChild(item);
        });
        searchDropdown.style.display = "block";
      } else {
        searchDropdown.style.display = "none";
      }
    } catch (err) {
      console.error("Error fetching search suggestions:", err);
    }
  } else {
    searchDropdown.style.display = "none";
  }
});

// Hide dropdown when clicking outside
document.addEventListener("click", (event) => {
  if (!searchInput.contains(event.target) && !searchDropdown.contains(event.target)) {
    searchDropdown.style.display = "none";
  }
});
