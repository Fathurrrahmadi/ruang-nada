// Halaman Daftar Unit (anggota)

async function startPage() {
  const user = await checkLogin("anggota");
  setupMemberLayout("katalog.html", user);

  if (!user.is_member) {
    document.getElementById("not-member").classList.remove("hidden");
  }

  await searchUnits("");
  await showActiveCount();
}

// Hitung unit yang sedang disewa anggota ini (yang belum dikembalikan)
async function showActiveCount() {
  const rentals = await callApi("GET", "/api/my/rentals");
  let total = 0;
  rentals.forEach(function (rental) {
    if (!rental.returned_at) {
      total += rental.units.length;
    }
  });
  document.getElementById("active-count").textContent = total;
}

async function searchUnits(keyword) {
  const units = await callApi("GET", "/api/catalog?q=" + encodeURIComponent(keyword));
  document.getElementById("empty-message").classList.toggle("hidden", units.length > 0);

  let html = "";
  units.forEach(function (unit) {
    let categoryTags = "";
    unit.categories.forEach(function (category) {
      categoryTags += `<span class="rounded bg-surface-container-highest px-2 py-0.5 text-xs text-primary-fixed">${escapeHtml(category.name)}</span> `;
    });

    // tombol "Ajukan Sewa" hanya untuk unit yang tersedia
    let buttonStyle = "bg-surface-container text-on-surface-variant hover:bg-surface-container-high";
    let buttonText = "Lihat Detail";
    if (unit.status === "tersedia") {
      buttonStyle = "bg-primary-container text-on-primary-container hover:opacity-90";
      buttonText = "Ajukan Sewa";
    }

    html += `
      <div class="flex flex-col overflow-hidden rounded-xl bg-surface-container-low">
        <div class="relative flex h-28 items-center justify-center bg-surface-container">
          <span class="icon h-12 w-12 text-primary">music_note</span>
          <div class="absolute right-3 top-3">${statusBadge(unit.status)}</div>
        </div>
        <div class="flex flex-1 flex-col gap-2 p-4">
          <span class="text-sm text-primary">${escapeHtml(unit.unit_code)}</span>
          <h3 class="font-serif text-xl">${escapeHtml(unit.unit_name)}</h3>
          <p class="text-sm text-outline">${escapeHtml(unit.description || "")}</p>
          <div class="flex flex-wrap gap-1">${categoryTags}</div>
          <div class="mt-auto flex items-center justify-between pt-3">
            <div>
              <div class="font-semibold text-secondary">${formatRupiah(unit.daily_rate)}</div>
              <div class="text-xs text-outline">per hari</div>
            </div>
            <a href="detail-unit.html?id=${unit.id}" class="rounded-lg px-4 py-2 text-sm font-semibold ${buttonStyle}">${buttonText}</a>
          </div>
        </div>
      </div>`;
  });
  document.getElementById("unit-grid").innerHTML = html;
}

document.getElementById("search-form").addEventListener("submit", function (event) {
  event.preventDefault();
  searchUnits(document.getElementById("search").value);
});

startPage();
