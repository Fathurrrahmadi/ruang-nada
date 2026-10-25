// Halaman Unit Sedang Disewa + proses pengembalian

async function startPage() {
  const user = await checkLogin("admin");
  setupAdminLayout("admin-disewa.html", user);
  await loadRentals();
}

async function loadRentals() {
  const rentals = await callApi("GET", "/api/rentals/active");

  document.getElementById("total").textContent = rentals.length + " transaksi aktif";
  document.getElementById("empty-message").classList.toggle("hidden", rentals.length > 0);

  let rows = "";
  rentals.forEach(function (rental) {
    const isLate = rental.status_display === "terlambat";

    let unitList = "";
    rental.units.forEach(function (unit) {
      unitList += `<div>${escapeHtml(unit.unit_name)} <span class="text-xs text-outline">${escapeHtml(unit.unit_code)}</span></div>`;
    });

    let dueText = formatDate(rental.due_at);
    if (isLate) {
      dueText += `<div class="text-xs">Lewat ${rental.days_late} hari</div>`;
    }

    rows += `
      <tr class="border-t border-outline-variant hover:bg-surface-container">
        <td class="px-4 py-3 text-sm font-semibold text-primary">${rental.code}</td>
        <td class="px-4 py-3">
          <div class="font-semibold">${escapeHtml(rental.member_name)}</div>
          <div class="text-xs text-outline">${escapeHtml(rental.member_email)}</div>
        </td>
        <td class="px-4 py-3">${unitList}</td>
        <td class="px-4 py-3 text-sm">${formatDate(rental.rented_at)}</td>
        <td class="px-4 py-3 text-sm ${isLate ? "text-error" : "text-secondary"}">${dueText}</td>
        <td class="px-4 py-3">${statusBadge(rental.status_display)}</td>
        <td class="px-4 py-3 text-right">
          <button onclick="returnRental(${rental.id}, '${rental.code}')"
            class="inline-flex items-center gap-1 rounded-lg bg-primary-container px-3 py-1.5 text-sm font-semibold text-on-primary-container hover:opacity-90">
            <span class="icon">assignment_return</span>
            Proses Pengembalian
          </button>
        </td>
      </tr>`;
  });
  document.getElementById("rental-rows").innerHTML = rows;
}

async function returnRental(id, code) {
  if (!confirm("Proses pengembalian untuk " + code + "?")) return;

  try {
    const result = await callApi("POST", "/api/rentals/" + id + "/return");
    // kalau terlambat, pesannya ditampilkan sebagai peringatan
    showToast(result.message, !result.late);
  } catch (error) {
    showToast(error.message, false);
  }
  await loadRentals();
}

startPage();
