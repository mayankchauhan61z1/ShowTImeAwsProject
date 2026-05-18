// hero section slide functionality start
const slides = document.getElementById("slides");
const prevBtn = document.getElementById("prev");
const nextBtn = document.getElementById("next");
let index = 0;

if (slides && prevBtn && nextBtn) {
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
}
// hero section slide functionality end

// Login & Signup functionality (CRITICAL SAFE CHECK)
const userLoginBtn = document.getElementById("userLoginBtn");
const adminLoginBtn = document.getElementById("adminLoginBtn");

if (userLoginBtn) {
  userLoginBtn.onclick = () => { window.location.href = "/login"; };
}
if (adminLoginBtn) {
  adminLoginBtn.onclick = () => { window.location.href = "/AdminLogin"; };
}

function goToMovie(movieId) {
  window.location.href = `/movie?movie_id=${movieId}`;
}

// Search functionality start
const searchInput = document.getElementById("searchInput");

if (searchInput) {
  // Trigger search on Enter key
  searchInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      let query = searchInput.value.trim();
      if (query) {
        window.location.href = "/search?query=" + encodeURIComponent(query);
      }
    }
  });

  // Target the searchDropdown that is built into your HTML templates
  const searchDropdown = document.getElementById("searchDropdown");

  if (searchDropdown) {
    // CLEAN FIX: Apply layout isolation styles via JS to stop it from breaking the Navbar look
    searchDropdown.style.position = "absolute";
    searchDropdown.style.backgroundColor = "#222";
    searchDropdown.style.border = "1px solid #444";
    searchDropdown.style.zIndex = "1000";
    searchDropdown.style.display = "none";

    searchInput.addEventListener("input", async () => {
      let query = searchInput.value.trim();

      if (query.length > 0) {
        try {
          let response = await fetch(`/search_suggestions?query=${encodeURIComponent(query)}`);
          let results = await response.json();

          // Reposition dropdown cleanly beneath input layout bounds
          const rect = searchInput.getBoundingClientRect();
          searchDropdown.style.left = rect.left + window.scrollX + "px";
          searchDropdown.style.top = rect.bottom + window.scrollY + "px";
          searchDropdown.style.width = rect.width + "px";

          // Clear old results
          searchDropdown.innerHTML = "";

          if (results.length > 0) {
            results.forEach(movie => {
              let item = document.createElement("div");
              item.className = "dropdown-item";
              item.textContent = `${movie.title} (${movie.genre})`;
              item.style.padding = "10px";
              item.style.color = "#fff";
              item.style.cursor = "pointer";
              
              item.onclick = () => {
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
  }
}
