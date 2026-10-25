// Halaman Riwayat Peminjaman (admin)

async function startPage() {
  const user = await checkLogin("admin");
  setupAdminLayout("admin-riwayat.html", user);

  // isi pilihan anggota untuk filter
  const members = await callApi("GET", "/api/members");
  const filter = document.getElementById("filter");
  members.forEach(function (member) {
    filter.innerHTML += `<option value="${member.id}">${escapeHtml(member.name)}</option>`;
  });
  filter.addEventListener("change", loadHistory);

  await loadHistory();
}

async function loadHistory() {
  const filter = document.getElementById("filter");
  let url = "/api/history";
  if (filter.value) {
    url += "?user_id=" + filter.value;
  }
  const rentals = await callApi("GET", url);

  document.getElementById("total").textContent = rentals.length + " transaksi";
  document.getElementById("print-info").textContent =
    "Anggota: " + filter.options[filter.selectedIndex].text + " | Dicetak: " + formatDate(dateInputValue(0));
  document.getElementById("empty-message").classList.toggle("hidden", rentals.length > 0);

  let rows = "";
  rentals.forEach(function (rental) {
    const unitNames = rental.units.map(function (u) {
      return escapeHtml(u.unit_name);
    });

    // nominal denda belum ditetapkan, jadi kalau kosong cukup tampilkan keterangan
    let fine = "-";
    if (rental.fine_amount !== null) {
      fine = formatRupiah(rental.fine_amount);
    } else if (rental.days_late > 0) {
      fine = "Terlambat " + rental.days_late + " hari (nominal belum ditetapkan)";
    }

    rows += `
      <tr class="border-t border-outline-variant hover:bg-surface-container">
        <td class="px-4 py-3 text-sm font-semibold text-primary">${rental.code}</td>
        <td class="px-4 py-3">${escapeHtml(rental.member_name)}</td>
        <td class="px-4 py-3">${unitNames.join(", ")}</td>
        <td class="px-4 py-3 text-sm">${formatDate(rental.rented_at)}</td>
        <td class="px-4 py-3 text-sm">${formatDate(rental.due_at)}</td>
        <td class="px-4 py-3 text-sm">${formatDate(rental.returned_at)}</td>
        <td class="px-4 py-3">${statusBadge(rental.status_display)}</td>
        <td class="px-4 py-3 text-xs text-outline">${fine}</td>
      </tr>`;
  });
  document.getElementById("history-rows").innerHTML = rows;
}

startPage();
