// const movies = {
//   mov1: {
//     title: "Frieren: Beyond Journey’s End",
//     desc: "Second season of Frieren. The adventure is over, but life goes on.",
//     img: "Images/Frieren.jpg"
//   },
//   mov2: {
//     title: "Hell's Paradise Season 2",
//     desc: "Gabimaru returns in a brutal fight for survival.",
//     img: "Images/HellParadise.jpg"
//   },
//   mov3: {
//     title: "Jujutsu Kaisen: Culling Game",
//     desc: "Deadly battles begin after the Shibuya incident.",
//     img: "Images/JujutsuKaisen.jpg"
//   }
// };
// const params = new URLSearchParams(window.location.search);
// const movieId = params.get("id");

// const movie = movies[movieId];

// const params = new URLSearchParams(window.location.search);
// const movieId = params.get("movie_id");

 // Generate 4x6 seat matrix
// Get seat matrix container and price
// Get seat matrix container and price
// Get seat matrix container and price
const seatMatrix = document.getElementById('seatMatrix');
const pricePerSeat = parseFloat(seatMatrix.dataset.price) || 0;

console.log("DEBUG pricePerSeat =", pricePerSeat); // check in console

// Build seat matrix (4 rows × 6 columns)
for (let i = 1; i <= 4; i++) {
  for (let j = 1; j <= 6; j++) {
    const seat = document.createElement('div');
    seat.classList.add('seat');
    seat.dataset.row = i;
    seat.dataset.col = j;
    seat.innerText = `${i},${j}`;

    // Toggle seat selection (only if not booked)
    seat.addEventListener('click', () => {
      if (!seat.classList.contains('booked')) {
        seat.classList.toggle('selected');
        updateBill();
      }
    });

    seatMatrix.appendChild(seat);
  }
}

// ✅ Load booked seats immediately on page load
loadBookedSeats();

// Update booking summary
function updateBill() {
  const selectedSeats = [...document.querySelectorAll('.seat.selected')];
  const names = selectedSeats.map(s => `${s.dataset.row},${s.dataset.col}`);

  document.getElementById('selectedSeats').innerText =
    names.length ? names.join(' | ') : "None";

  document.getElementById('seatCount').innerText = names.length;

  const total = names.length * pricePerSeat;
  document.getElementById('totalAmount').innerText = total;
}

function bookTicket() {
  const selectedSeats = [...document.querySelectorAll('.seat.selected')]
    .map(seat => `${seat.dataset.row},${seat.dataset.col}`);

  if (selectedSeats.length === 0) {
    alert("No seats selected!");
    return;
  }

  const theater = document.querySelector('.select-row select').value;
  const showtime = document.querySelectorAll('.select-row select')[1].value;
  const seats = selectedSeats.length;
  const total = seats * pricePerSeat;

  fetch("/book", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      movie_id: movieId,          // ✅ comes from Flask
      seats: seats,
      seat_numbers: selectedSeats,
      theater: theater,
      showtime: showtime
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data) {
      alert(data.message);
      // ✅ Refresh booked seats after booking
      loadBookedSeats();
    }
  })
  .catch(err => console.error("Booking error:", err));
}

function loadBookedSeats() {
  const showtime = document.querySelectorAll('.select-row select')[1].value;

  fetch(`/booked_seats/${movieId}/${showtime}`)
    .then(res => res.json())
    .then(data => {
      const bookedSeats = data.booked_seats;
      bookedSeats.forEach(seatName => {
        const [row, col] = seatName.split(',');
        const seat = document.querySelector(`.seat[data-row="${row}"][data-col="${col}"]`);
        if (seat) {
          seat.classList.add('booked');
        }
      });
    });
}

// ✅ Refresh seats when showtime changes
document.querySelectorAll('.select-row select')[1].addEventListener('change', () => {
  document.querySelectorAll('.seat').forEach(seat => {
    seat.classList.remove('selected', 'booked');
  });
  loadBookedSeats();
});