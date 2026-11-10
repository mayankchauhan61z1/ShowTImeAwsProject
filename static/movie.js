
const seatMatrix = document.getElementById("seatMatrix");
const pricePerSeat = parseFloat(seatMatrix.dataset.price) || 0;

const showtimeSelect = document.getElementById("showtimeSelect");
const theaterSelect = document.getElementById("theaterSelect");
const confirmButton = document.getElementById("confirmBooking");

// Generate 4 rows x 6 columns = 24 seats
for (let row = 1; row <= 4; row++) {

    for (let col = 1; col <= 6; col++) {

        const seat = document.createElement("div");

        seat.classList.add("seat");

        seat.dataset.row = row;
        seat.dataset.col = col;

        seat.innerText = `${row},${col}`;

        seat.addEventListener("click", () => {

            if (seat.classList.contains("booked")) {
                return;
            }

            seat.classList.toggle("selected");

            updateBill();
        });

        seatMatrix.appendChild(seat);
    }
}


// Update booking summary
function updateBill() {

    const selectedSeats = [
        ...document.querySelectorAll(".seat.selected")
    ];

    const seatNames = selectedSeats.map(seat =>
        `${seat.dataset.row},${seat.dataset.col}`
    );

    document.getElementById("selectedSeats").innerText =
        seatNames.length ? seatNames.join(" | ") : "None";

    document.getElementById("seatCount").innerText =
        seatNames.length;

    const total = seatNames.length * pricePerSeat;

    document.getElementById("totalAmount").innerText =
        total.toFixed(2);
}


// Load booked seats from Flask
async function loadBookedSeats() {

    const showtime = showtimeSelect.value;

    if (!showtime) {
        return;
    }

    try {

        const url =
            `/booked_seats/${encodeURIComponent(movieId)}/${encodeURIComponent(showtime)}`;

        const response = await fetch(url, {
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error("Unable to load booked seats");
        }

        const data = await response.json();

        const bookedSeats = data.booked_seats || [];

        bookedSeats.forEach(seatName => {

            const [row, col] = seatName.split(",");

            const seat = document.querySelector(
                `.seat[data-row="${row}"][data-col="${col}"]`
            );

            if (seat) {

                seat.classList.remove("selected");

                seat.classList.add("booked");
            }
        });

        updateBill();

    } catch (error) {

        console.error("Booked seats error:", error);

    }
}


// Book selected tickets
async function bookTicket() {

    const selectedSeats = [
        ...document.querySelectorAll(".seat.selected")
    ].map(seat =>
        `${seat.dataset.row},${seat.dataset.col}`
    );

    if (selectedSeats.length === 0) {

        alert("Please select at least one seat!");

        return;
    }

    const theater = theaterSelect.value;
    const showtime = showtimeSelect.value;

    const totalSeats = selectedSeats.length;

    const totalAmount = totalSeats * pricePerSeat;

    confirmButton.disabled = true;
    confirmButton.innerText = "Processing...";

    try {

        const response = await fetch("/book", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                movie_id: movieId,

                seats: totalSeats,

                seat_numbers: selectedSeats,

                theater: theater,

                showtime: showtime

            })

        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error(data.message || "Booking failed");

        }

        if (data.message) {

            alert(data.message);

        } else {

            alert("Booking request completed.");

        }

        await loadBookedSeats();

    } catch (error) {

        console.error("Booking error:", error);

        alert(error.message || "Something went wrong. Please try again.");

    } finally {

        confirmButton.disabled = false;

        confirmButton.innerHTML =
            'Confirm Booking <i class="fa-solid fa-arrow-right"></i>';

    }
}


// Refresh seats when showtime changes
showtimeSelect.addEventListener("change", () => {

    document.querySelectorAll(".seat").forEach(seat => {

        seat.classList.remove("selected", "booked");

    });

    updateBill();

    loadBookedSeats();

});


// Initial page load
updateBill();

loadBookedSeats();
