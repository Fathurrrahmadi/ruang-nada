// Halaman Login

const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");

loginForm.addEventListener("submit", async function (event) {
  event.preventDefault();
  clearFieldErrors(["email", "password"]);
  loginError.classList.add("hidden");

  const data = {
    email: document.getElementById("email").value,
    password: document.getElementById("password").value,
  };

  try {
    const result = await callApi("POST", "/api/login", data);
    // admin dan anggota punya halaman utama yang berbeda
    window.location.href = result.home;
  } catch (error) {
    // kalau error milik satu input, tampilkan di bawah input itu. Kalau tidak, di kotak merah di atas
    if (!error.field || !showFieldError(error.field, error.message)) {
      loginError.textContent = error.message;
      loginError.classList.remove("hidden");
    }
  }
});
