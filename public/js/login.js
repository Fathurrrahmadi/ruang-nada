const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");
let modeDaftar = false;

document.getElementById("mode-toggle").addEventListener("click", function (event) {
  event.preventDefault();
  modeDaftar = !modeDaftar;
  document.getElementById("name-wrap").classList.toggle("hidden", !modeDaftar);
  document.getElementById("submit-btn").textContent = modeDaftar ? "Daftar" : "Masuk";
  document.getElementById("mode-text").textContent = modeDaftar ? "Sudah punya akun?" : "Belum punya akun?";
  this.textContent = modeDaftar ? "Masuk" : "Daftar";
  clearFieldErrors(["name", "email", "password"]);
  loginError.classList.add("hidden");
});

loginForm.addEventListener("submit", async function (event) {
  event.preventDefault();
  clearFieldErrors(["name", "email", "password"]);
  loginError.classList.add("hidden");

  const data = {
    email: document.getElementById("email").value,
    password: document.getElementById("password").value,
  };
  if (modeDaftar) {
    data.name = document.getElementById("name").value;
  }

  try {
    const alamat = modeDaftar ? "/api/register" : "/api/login";
    const result = await callApi("POST", alamat, data);
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