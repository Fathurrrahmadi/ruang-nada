// Halaman Kelola Anggota

let members = [];
let editingId = null;
const fieldNames = ["name", "email", "password"];

async function startPage() {
  const user = await checkLogin("admin");
  setupAdminLayout("admin-anggota.html", user);
  await loadMembers();
}

async function loadMembers() {
  members = await callApi("GET", "/api/members");
  showMembers();
}

function showMembers() {
  document.getElementById("total").textContent = members.length + " anggota";

  let rows = "";
  members.forEach(function (member) {
    const status = member.is_member
      ? '<span class="text-tertiary">Terdaftar</span>'
      : '<span class="text-secondary">Belum terdaftar</span>';

    rows += `
      <tr class="border-t border-outline-variant hover:bg-surface-container">
        <td class="px-4 py-3">
          <div class="font-semibold">${escapeHtml(member.name)}</div>
          <div class="text-xs text-outline">${escapeHtml(member.email)}</div>
        </td>
        <td class="px-4 py-3 text-sm">${escapeHtml(member.phone || "-")}</td>
        <td class="px-4 py-3 text-sm">${status}</td>
        <td class="px-4 py-3 text-sm">${member.active_units} / 2</td>
        <td class="px-4 py-3 text-right">
          <button onclick="editMember(${member.id})" title="Ubah" class="rounded-lg p-1.5 text-primary hover:bg-surface-container-highest">
            <span class="icon">edit_note</span>
          </button>
          <button onclick="deleteMember(${member.id})" title="Hapus" class="rounded-lg p-1.5 text-error hover:bg-error-container">
            <span class="icon">delete</span>
          </button>
        </td>
      </tr>`;
  });
  document.getElementById("member-rows").innerHTML = rows;
}

function resetForm() {
  editingId = null;
  document.getElementById("name").value = "";
  document.getElementById("email").value = "";
  document.getElementById("phone").value = "";
  document.getElementById("address").value = "";
  document.getElementById("password").value = "";
  document.getElementById("is_member").checked = true;
  document.getElementById("form-title").textContent = "Tambah Anggota";
  document.getElementById("password-hint").classList.add("hidden");
  document.getElementById("delete-warning").classList.add("hidden");
  clearFieldErrors(fieldNames);
}

function editMember(id) {
  const member = members.find(function (m) {
    return m.id === id;
  });
  editingId = id;
  document.getElementById("name").value = member.name;
  document.getElementById("email").value = member.email;
  document.getElementById("phone").value = member.phone || "";
  document.getElementById("address").value = member.address || "";
  document.getElementById("password").value = "";
  document.getElementById("is_member").checked = member.is_member;
  document.getElementById("form-title").textContent = "Ubah Anggota";
  document.getElementById("password-hint").classList.remove("hidden");
  document.getElementById("delete-warning").classList.add("hidden");
  clearFieldErrors(fieldNames);
}

async function deleteMember(id) {
  const member = members.find(function (m) {
    return m.id === id;
  });
  if (!confirm('Hapus anggota "' + member.name + '" beserta profilnya?')) return;

  try {
    await callApi("DELETE", "/api/members/" + id);
    showToast("Anggota dihapus.", true);
    if (editingId === id) resetForm();
    await loadMembers();
  } catch (error) {
    const warning = document.getElementById("delete-warning");
    warning.textContent = error.message;
    warning.classList.remove("hidden");
  }
}

document.getElementById("member-form").addEventListener("submit", async function (event) {
  event.preventDefault();
  clearFieldErrors(fieldNames);

  const data = {
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    phone: document.getElementById("phone").value,
    address: document.getElementById("address").value,
    password: document.getElementById("password").value,
    is_member: document.getElementById("is_member").checked,
  };

  try {
    if (editingId) {
      await callApi("PUT", "/api/members/" + editingId, data);
      showToast("Data anggota diperbarui.", true);
    } else {
      await callApi("POST", "/api/members", data);
      showToast("Anggota ditambahkan.", true);
    }
    resetForm();
    await loadMembers();
  } catch (error) {
    showError(error);
  }
});

startPage();
