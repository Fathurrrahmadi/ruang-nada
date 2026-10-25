// Halaman Kelola Unit

let units = [];
let categories = [];
let editingId = null;
const fieldNames = ["unit_code", "unit_name", "daily_rate", "status", "category_ids"];

async function startPage() {
  const user = await checkLogin("admin");
  setupAdminLayout("admin-unit.html", user);

  categories = await callApi("GET", "/api/categories");
  showCategoryCheckboxes();
  await loadUnits();
}

// Checkbox kategori di dalam form
function showCategoryCheckboxes() {
  let html = "";
  categories.forEach(function (category) {
    html += `
      <label class="flex items-center gap-2">
        <input type="checkbox" class="category-checkbox" value="${category.id}" />
        ${escapeHtml(category.name)}
      </label>`;
  });
  document.getElementById("category-list").innerHTML = html;
}

// Centang checkbox sesuai daftar id kategori
function checkCategories(ids) {
  document.querySelectorAll(".category-checkbox").forEach(function (box) {
    box.checked = ids.includes(Number(box.value));
  });
}

function getCheckedCategories() {
  const ids = [];
  document.querySelectorAll(".category-checkbox").forEach(function (box) {
    if (box.checked) ids.push(Number(box.value));
  });
  return ids;
}

async function loadUnits() {
  units = await callApi("GET", "/api/units");
  showUnits();
}

function showUnits() {
  document.getElementById("total").textContent = units.length + " unit";

  let rows = "";
  units.forEach(function (unit) {
    let categoryTags = "";
    unit.categories.forEach(function (category) {
      categoryTags += `<span class="rounded bg-surface-container-highest px-2 py-0.5 text-xs text-primary-fixed">${escapeHtml(category.name)}</span> `;
    });

    rows += `
      <tr class="border-t border-outline-variant hover:bg-surface-container">
        <td class="px-4 py-3 text-sm font-semibold text-primary">${escapeHtml(unit.unit_code)}</td>
        <td class="px-4 py-3">
          <div class="font-semibold">${escapeHtml(unit.unit_name)}</div>
          <div class="text-xs text-outline">${escapeHtml(unit.description || "")}</div>
        </td>
        <td class="px-4 py-3"><div class="flex flex-wrap gap-1">${categoryTags}</div></td>
        <td class="px-4 py-3 text-sm text-secondary">${formatRupiah(unit.daily_rate)}</td>
        <td class="px-4 py-3">${statusBadge(unit.status)}</td>
        <td class="px-4 py-3 text-right">
          <button onclick="editUnit(${unit.id})" title="Ubah" class="rounded-lg p-1.5 text-primary hover:bg-surface-container-highest">
            <span class="icon">edit_note</span>
          </button>
          <button onclick="deleteUnit(${unit.id})" title="Hapus" class="rounded-lg p-1.5 text-error hover:bg-error-container">
            <span class="icon">delete</span>
          </button>
        </td>
      </tr>`;
  });
  document.getElementById("unit-rows").innerHTML = rows;
}

function resetForm() {
  editingId = null;
  document.getElementById("unit_code").value = "";
  document.getElementById("unit_name").value = "";
  document.getElementById("description").value = "";
  document.getElementById("daily_rate").value = "";
  document.getElementById("status").value = "tersedia";
  document.getElementById("status").disabled = false;
  checkCategories([]);
  document.getElementById("form-title").textContent = "Tambah Unit";
  document.getElementById("delete-warning").classList.add("hidden");
  clearFieldErrors(fieldNames);
}

function editUnit(id) {
  const unit = units.find(function (u) {
    return u.id === id;
  });
  editingId = id;
  document.getElementById("unit_code").value = unit.unit_code;
  document.getElementById("unit_name").value = unit.unit_name;
  document.getElementById("description").value = unit.description || "";
  document.getElementById("daily_rate").value = unit.daily_rate;
  document.getElementById("status").value = unit.status;
  // unit yang sedang disewa tidak boleh diubah statusnya manual
  document.getElementById("status").disabled = unit.status === "disewa";
  checkCategories(unit.categories.map(function (c) { return c.id; }));
  document.getElementById("form-title").textContent = "Ubah Unit";
  document.getElementById("delete-warning").classList.add("hidden");
  clearFieldErrors(fieldNames);
}

async function deleteUnit(id) {
  const unit = units.find(function (u) {
    return u.id === id;
  });
  if (!confirm('Hapus unit "' + unit.unit_code + '"?')) return;

  try {
    await callApi("DELETE", "/api/units/" + id);
    showToast("Unit dihapus.", true);
    if (editingId === id) resetForm();
    await loadUnits();
  } catch (error) {
    const warning = document.getElementById("delete-warning");
    warning.textContent = error.message;
    warning.classList.remove("hidden");
  }
}

document.getElementById("unit-form").addEventListener("submit", async function (event) {
  event.preventDefault();
  clearFieldErrors(fieldNames);

  const data = {
    unit_code: document.getElementById("unit_code").value,
    unit_name: document.getElementById("unit_name").value,
    description: document.getElementById("description").value,
    daily_rate: document.getElementById("daily_rate").value,
    status: document.getElementById("status").value,
    category_ids: getCheckedCategories(),
  };

  try {
    if (editingId) {
      await callApi("PUT", "/api/units/" + editingId, data);
      showToast("Unit diperbarui.", true);
    } else {
      await callApi("POST", "/api/units", data);
      showToast("Unit ditambahkan.", true);
    }
    resetForm();
    await loadUnits();
  } catch (error) {
    showError(error);
  }
});

startPage();
