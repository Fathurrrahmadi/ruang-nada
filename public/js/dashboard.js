// Halaman Dashboard Admin

async function startPage() {
  const user = await checkLogin("admin");
  setupAdminLayout("admin-dashboard.html", user);

  const data = await callApi("GET", "/api/dashboard");
  showSummary(data);
  showUpcoming(data.upcoming);
}

function showSummary(data) {
  // [judul, angka, nama ikon, warna]
  const cards = [
    ["Total Unit", data.units, "music_note", "text-primary"],
    ["Tersedia", data.tersedia, "check_circle", "text-tertiary"],
    ["Sedang Disewa", data.disewa, "alarm", "text-secondary"],
    ["Maintenance", data.maintenance, "build", "text-error"],
    ["Anggota Terdaftar", data.members, "group", "text-primary"],
    ["Transaksi Terlambat", data.late, "warning", "text-error"],
  ];

  let html = "";
  cards.forEach(function (card) {
    html += `
      <div class="rounded-xl bg-surface-container-low p-4">
        <div class="flex items-center justify-between">
          <span class="text-xs uppercase tracking-wider text-outline">${card[0]}</span>
          <span class="icon ${card[3]}">${card[2]}</span>
        </div>
        <div class="mt-2 font-serif text-4xl ${card[3]}">${card[1]}</div>
      </div>`;
  });
  document.getElementById("summary").innerHTML = html;
}

function showUpcoming(rentals) {
  document.getElementById("empty-message").classList.toggle("hidden", rentals.length > 0);

  let rows = "";
  rentals.forEach(function (rental) {
    const unitNames = rental.units.map(function (u) {
      return escapeHtml(u.unit_name);
    });
    rows += `
      <tr class="border-t border-outline-variant hover:bg-surface-container">
        <td class="px-4 py-3 text-sm font-semibold text-primary">${rental.code}</td>
        <td class="px-4 py-3">${escapeHtml(rental.member_name)}</td>
        <td class="px-4 py-3">${unitNames.join(", ")}</td>
        <td class="px-4 py-3 text-sm text-secondary">${formatDate(rental.due_at)}</td>
        <td class="px-4 py-3">${statusBadge(rental.status_display)}</td>
      </tr>`;
  });
  document.getElementById("upcoming-rows").innerHTML = rows;
}

startPage();
