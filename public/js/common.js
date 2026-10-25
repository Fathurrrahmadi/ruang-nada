// Fungsi yang dipakai di banyak halaman

// ---------- komunikasi dengan server ----------

// Kirim permintaan ke API. Hasilnya berupa objek dari JSON.
// Kalau server membalas error, fungsi ini melempar Error yang berisi pesannya.
async function callApi(method, url, data) {
  const options = {
    method: method,
    headers: { "Content-Type": "application/json" },
  };
  if (data !== undefined) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(url, options);

  let result = {};
  try {
    result = await response.json();
  } catch (e) {
    // balasan kosong, abaikan saja
  }

  // sesi habis atau belum login -> kembali ke halaman login
  if (response.status === 401 && !url.includes("/api/login")) {
    window.location.href = "index.html";
  }

  if (!response.ok) {
    const error = new Error(result.error || "Terjadi kesalahan.");
    error.field = result.field;
    error.code = result.code;
    throw error;
  }
  return result;
}

// Cek user yang login. Kalau perannya tidak cocok dengan halaman, diarahkan ke halaman yang benar.
async function checkLogin(requiredRole) {
  const user = await callApi("GET", "/api/me");

  if (user.role !== requiredRole) {
    if (user.role === "admin") {
      window.location.href = "admin-dashboard.html";
    } else {
      window.location.href = "katalog.html";
    }
    return new Promise(function () {}); // hentikan proses di halaman ini
  }
  return user;
}

async function logout() {
  await callApi("POST", "/api/logout");
  window.location.href = "index.html";
}

// ---------- tampilan ----------

// Notifikasi kecil di pojok kanan bawah
let toastTimer = null;
function showToast(message, isSuccess) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    document.body.appendChild(toast);
    toast.id = "toast";
  }

  const color = isSuccess
    ? "bg-tertiary-container text-on-tertiary-container"
    : "bg-error-container text-on-error-container";
  toast.className = "fixed bottom-6 right-6 z-50 max-w-sm rounded-lg px-4 py-3 text-sm shadow-xl " + color;
  toast.textContent = message;

  clearTimeout(toastTimer);
  toastTimer = setTimeout(function () {
    toast.className = "hidden";
  }, 4000);
}

// Pesan error di bawah input. Elemennya: <p id="error-NAMA">
function showFieldError(fieldName, message) {
  const element = document.getElementById("error-" + fieldName);
  if (!element) return false;
  element.textContent = message;
  element.classList.remove("hidden");
  return true;
}

function clearFieldErrors(fieldNames) {
  fieldNames.forEach(function (name) {
    const element = document.getElementById("error-" + name);
    if (element) element.classList.add("hidden");
  });
}

// Tampilkan error dari server: di bawah input yang salah, atau sebagai notifikasi kalau tidak ada inputnya
function showError(error) {
  const shown = error.field && showFieldError(error.field, error.message);
  if (!shown) {
    showToast(error.message, false);
  }
}

// Label status berwarna (tersedia, disewa, aktif, terlambat, dst)
function statusBadge(status) {
  const styles = {
    tersedia: ["Tersedia", "text-tertiary", "bg-tertiary"],
    disewa: ["Disewa", "text-secondary", "bg-secondary"],
    maintenance: ["Maintenance", "text-error", "bg-error"],
    aktif: ["Aktif", "text-tertiary", "bg-tertiary"],
    selesai: ["Selesai", "text-on-surface-variant", "bg-outline"],
    terlambat: ["Terlambat", "text-error", "bg-error"],
  };
  const style = styles[status] || [status, "text-on-surface-variant", "bg-outline"];

  return `
    <span class="inline-flex items-center gap-1.5 rounded-full bg-surface-container-high px-3 py-1 text-xs ${style[1]}">
      <span class="h-1.5 w-1.5 rounded-full ${style[2]}"></span>
      ${style[0]}
    </span>`;
}

// ---------- format data ----------

const monthNames = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];

// "2026-10-25" -> "25 Okt 2026"
function formatDate(text) {
  if (!text) return "-";
  const parts = text.slice(0, 10).split("-");
  return parts[2] + " " + monthNames[Number(parts[1]) - 1] + " " + parts[0];
}

// 1450000 -> "Rp 1.450.000"
function formatRupiah(number) {
  return "Rp " + Number(number || 0).toLocaleString("id-ID");
}

// Tanggal hari ini (ditambah beberapa hari) dalam format YYYY-MM-DD untuk input type="date"
function dateInputValue(plusDays) {
  const date = new Date();
  date.setDate(date.getDate() + (plusDays || 0));
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return date.getFullYear() + "-" + month + "-" + day;
}

// Cegah teks dari database merusak HTML (contoh: nama yang berisi tanda < >)
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text == null ? "" : String(text);
  return div.innerHTML;
}
