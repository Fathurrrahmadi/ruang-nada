// Halaman Profil (anggota)

async function startPage() {
  const user = await checkLogin("anggota");
  setupMemberLayout("profil.html", user);

  const profile = await callApi("GET", "/api/my/profile");
  fillForm(profile);
}

function fillForm(profile) {
  document.getElementById("name").value = profile.name;
  document.getElementById("email").value = profile.email;
  document.getElementById("phone").value = profile.phone || "";
  document.getElementById("address").value = profile.address || "";

  const status = document.getElementById("member-status");
  if (profile.is_member) {
    status.textContent = "Anggota terdaftar";
    status.className = "text-sm text-tertiary";
  } else {
    status.textContent = "Belum terdaftar sebagai anggota";
    status.className = "text-sm text-secondary";
  }
}

document.getElementById("profile-form").addEventListener("submit", async function (event) {
  event.preventDefault();
  clearFieldErrors(["name"]);

  const data = {
    name: document.getElementById("name").value,
    phone: document.getElementById("phone").value,
    address: document.getElementById("address").value,
  };

  try {
    const profile = await callApi("PUT", "/api/my/profile", data);
    fillForm(profile);
    showToast("Profil diperbarui. Muat ulang halaman untuk melihat nama baru di bagian atas.", true);
  } catch (error) {
    showError(error);
  }
});

startPage();
