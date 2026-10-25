// Halaman Sewa Saya (anggota)

let allRentals = [];
let currentTab = "semua";
const tabs = [
  { value: "semua", label: "Semua" },
  { value: "aktif", label: "Aktif" },
  { value: "selesai", label: "Selesai" },
  { value: "terlambat", label: "Terlambat" },
];

async function startPage() {
  const user = await checkLogin("anggota");
  setupMemberLayout("anggota-sewa.html", user);

  allRentals = await callApi("GET", "/api/my/rentals");
  showSummary();
  showRentals();
}

// Kartu ringkasan di atas tabel
function showSummary() {
  let activeUnits = 0;
  let nearestDue = null;

  allRentals.forEach(function (rental) {
    if (!rental.returned_at) {
      activeUnits += rental.units.length;
      if (nearestDue === null || rental.due_at < nearestDue) {
        nearestDue = rental.due_at;
      }
    }
  });

  document.getElementById("active-count").textContent = activeUnits;
  document.getElementById("nearest-due").textContent = nearestDue ? formatDate(nearestDue) : "-";
  document.getElementById("total-count").textContent = allRentals.length;
}

function showRentals() {
  // tombol tab (Semua / Aktif / Selesai / Terlambat)
  let tabHtml = "";
  tabs.forEach(function (tab) {
    const color = tab.value === currentTab
      ? "bg-primary-container text-on-primary-container"
      : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high";
    tabHtml += `<button onclick="changeTab('${tab.value}')" class="rounded-full px-3 py-1 text-xs ${color}">${tab.label}</button>`;
  });
  document.getElementById("tabs").innerHTML = tabHtml;

  const rentals = allRentals.filter(function (rental) {
    return currentTab === "semua" || rental.status_display === currentTab;
  });
  document.getElementById("total").textContent = rentals.length + " dari " + allRentals.length + " transaksi";
  document.getElementById("empty-message").classList.toggle("hidden", rentals.length > 0);

  let rows = "";
  rentals.forEach(function (rental) {
    let unitList = "";
    rental.units.forEach(function (unit) {
      unitList += `<div class="font-semibold">${escapeHtml(unit.unit_name)}</div>
                   <div class="text-xs text-outline">${escapeHtml(unit.unit_code)}</div>`;
    });

    let fine = "-";
    if (rental.fine_amount !== null) {
      fine = formatRupiah(rental.fine_amount);
    } else if (rental.days_late > 0) {
      fine = "Dicatat Admin";
    }

    rows += `
      <tr class="border-t border-outline-variant hover:bg-surface-container">
        <td class="px-4 py-3 text-sm font-semibold text-primary">${rental.code}</td>
        <td class="px-4 py-3">${unitList}</td>
        <td class="px-4 py-3 text-sm">${formatDate(rental.rented_at)}</td>
        <td class="px-4 py-3 text-sm text-secondary">${formatDate(rental.due_at)}</td>
        <td class="px-4 py-3 text-sm">${formatDate(rental.returned_at)}</td>
        <td class="px-4 py-3">${statusBadge(rental.status_display)}</td>
        <td class="px-4 py-3 text-xs text-outline">${fine}</td>
      </tr>`;
  });
  document.getElementById("rental-rows").innerHTML = rows;
}

function changeTab(value) {
  currentTab = value;
  showRentals();
}

startPage();
