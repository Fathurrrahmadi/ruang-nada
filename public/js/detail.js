// Halaman Detail Unit + pengajuan sewa

// id unit diambil dari alamat halaman, contoh: detail-unit.html?id=3
const unitId = new URLSearchParams(window.location.search).get("id");

const formAlert = document.getElementById("form-alert");

function showAlert(message) {
  formAlert.textContent = message;
  formAlert.classList.remove("hidden");
}

async function startPage() {
  const user = await checkLogin("anggota");
  setupMemberLayout("katalog.html", user);

  if (!user.is_member) {
    showAlert("Kamu belum terdaftar sebagai anggota. Hubungi Admin untuk menyelesaikan pendaftaran.");
  }

  // isi tanggal bawaan: hari ini, dan jatuh tempo 5 hari lagi
  document.getElementById("rented_at").value = dateInputValue(0);
  document.getElementById("due_at").value = dateInputValue(5);

  try {
    const unit = await callApi("GET", "/api/catalog/" + encodeURIComponent(unitId));
    showUnit(unit);
  } catch (error) {
    document.getElementById("unit-info").innerHTML = `<p class="text-error">${escapeHtml(error.message)}</p>`;
  }
}

function showUnit(unit) {
  let categoryTags = "";
  unit.categories.forEach(function (category) {
    categoryTags += `<span class="rounded bg-surface-container-highest px-2 py-0.5 text-xs text-primary-fixed">${escapeHtml(category.name)}</span> `;
  });

  document.getElementById("unit-info").innerHTML = `
    <div class="flex items-center justify-between">
      <span class="text-sm text-primary">${escapeHtml(unit.unit_code)}</span>
      ${statusBadge(unit.status)}
    </div>
    <h1 class="font-serif text-3xl">${escapeHtml(unit.unit_name)}</h1>
    <p class="text-on-surface-variant">${escapeHtml(unit.description || "")}</p>
    <div class="flex flex-wrap gap-1">${categoryTags}</div>
    <div>
      <div class="font-serif text-3xl text-secondary">${formatRupiah(unit.daily_rate)}</div>
      <div class="text-xs text-outline">per hari</div>
    </div>`;

  // unit yang disewa / maintenance tidak bisa diajukan
  if (unit.status !== "tersedia") {
    if (unit.status === "disewa") {
      showAlert("Unit sedang disewa dan tidak bisa dipilih.");
    } else {
      showAlert("Unit sedang maintenance dan tidak bisa dipilih.");
    }
    document.getElementById("submit-button").disabled = true;
  }
}

// kalau tanggal sewa diganti, jatuh tempo ikut disesuaikan jadi 5 hari setelahnya
document.getElementById("rented_at").addEventListener("change", function () {
  const date = new Date(this.value);
  if (!isNaN(date)) {
    date.setDate(date.getDate() + 5);
    document.getElementById("due_at").value = date.toISOString().slice(0, 10);
  }
});

document.getElementById("rental-form").addEventListener("submit", async function (event) {
  event.preventDefault();
  clearFieldErrors(["rented_at", "due_at"]);
  formAlert.classList.add("hidden");

  const data = {
    unit_id: Number(unitId),
    rented_at: document.getElementById("rented_at").value,
    due_at: document.getElementById("due_at").value,
  };

  try {
    const result = await callApi("POST", "/api/rentals", data);
    showToast("Penyewaan berhasil (" + result.code + "). Jatuh tempo " + formatDate(result.due_at) + ".", true);
    setTimeout(function () {
      window.location.href = "anggota-sewa.html";
    }, 1500);
  } catch (error) {
    // error tanggal tampil di bawah inputnya, error lain (batas 2 unit, bukan anggota, dll) di kotak merah
    if (error.field === "rented_at" || error.field === "due_at") {
      showFieldError(error.field, error.message);
    } else {
      showAlert(error.message);
    }
  }
});

startPage();
