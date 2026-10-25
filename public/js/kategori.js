// Halaman Kelola Kategori

let categories = [];        // data dari server
let editingId = null;       // id kategori yang sedang diubah (null = sedang tambah baru)

async function startPage() {
  const user = await checkLogin("admin");
  setupAdminLayout("admin-kategori.html", user);
  await loadCategories();
}

async function loadCategories() {
  categories = await callApi("GET", "/api/categories");
  showCategories();
}

function showCategories() {
  document.getElementById("total").textContent = categories.length + " kategori";

  let rows = "";
  categories.forEach(function (category) {
    rows += `
      <tr class="border-t border-outline-variant hover:bg-surface-container">
        <td class="px-4 py-3 font-semibold">${escapeHtml(category.name)}</td>
        <td class="px-4 py-3 text-sm text-secondary">${category.units} unit</td>
        <td class="px-4 py-3 text-right">
          <button onclick="editCategory(${category.id})" title="Ubah" class="rounded-lg p-1.5 text-primary hover:bg-surface-container-highest">
            <span class="icon">edit_note</span>
          </button>
          <button onclick="deleteCategory(${category.id})" title="Hapus" class="rounded-lg p-1.5 text-error hover:bg-error-container">
            <span class="icon">delete</span>
          </button>
        </td>
      </tr>`;
  });
  document.getElementById("category-rows").innerHTML = rows;
}

function resetForm() {
  editingId = null;
  document.getElementById("name").value = "";
  document.getElementById("form-title").textContent = "Tambah Kategori";
  document.getElementById("delete-warning").classList.add("hidden");
  clearFieldErrors(["name"]);
}

function editCategory(id) {
  const category = categories.find(function (c) {
    return c.id === id;
  });
  editingId = id;
  document.getElementById("name").value = category.name;
  document.getElementById("form-title").textContent = "Ubah Kategori";
  document.getElementById("delete-warning").classList.add("hidden");
  clearFieldErrors(["name"]);
}

async function deleteCategory(id) {
  const category = categories.find(function (c) {
    return c.id === id;
  });
  if (!confirm('Hapus kategori "' + category.name + '"?')) return;

  try {
    await callApi("DELETE", "/api/categories/" + id);
    showToast("Kategori dihapus.", true);
    if (editingId === id) resetForm();
    await loadCategories();
  } catch (error) {
    // biasanya karena kategori masih dipakai unit
    const warning = document.getElementById("delete-warning");
    warning.textContent = error.message;
    warning.classList.remove("hidden");
  }
}

document.getElementById("category-form").addEventListener("submit", async function (event) {
  event.preventDefault();
  clearFieldErrors(["name"]);

  const data = { name: document.getElementById("name").value };

  try {
    if (editingId) {
      await callApi("PUT", "/api/categories/" + editingId, data);
      showToast("Kategori diperbarui.", true);
    } else {
      await callApi("POST", "/api/categories", data);
      showToast("Kategori ditambahkan.", true);
    }
    resetForm();
    await loadCategories();
  } catch (error) {
    showError(error);
  }
});

startPage();
