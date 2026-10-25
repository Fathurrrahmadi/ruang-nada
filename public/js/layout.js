// Menu samping dan bagian atas halaman.
// Ditaruh di satu file supaya tidak perlu menulis ulang di setiap halaman.

const adminMenu = [
  { href: "admin-dashboard.html", icon: "dashboard", label: "Dashboard" },
  { href: "admin-unit.html", icon: "library_music", label: "Kelola Unit" },
  { href: "admin-kategori.html", icon: "category", label: "Kelola Kategori" },
  { href: "admin-anggota.html", icon: "group", label: "Kelola Anggota" },
  { href: "admin-disewa.html", icon: "assignment_return", label: "Unit Sedang Disewa" },
  { href: "admin-riwayat.html", icon: "history", label: "Riwayat Peminjaman" },
];

const memberMenu = [
  { href: "katalog.html", label: "Daftar Unit" },
  { href: "anggota-sewa.html", label: "Sewa Saya" },
  { href: "profil.html", label: "Profil" },
];

// activePage = nama file halaman yang sedang dibuka, supaya menunya ditandai
function setupAdminLayout(activePage, user) {
  const links = adminMenu
    .map(function (item) {
      const isActive = item.href === activePage;
      const color = isActive
        ? "bg-primary-container text-on-primary-container font-semibold"
        : "text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface";
      return `
        <a href="${item.href}" class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm ${color}">
          <span class="icon">${item.icon}</span>
          ${item.label}
        </a>`;
    })
    .join("");

  document.getElementById("sidebar").innerHTML = `
    <div class="mb-8 flex items-center gap-2 px-2">
      <span class="icon h-7 w-7 text-primary">music_note</span>
      <div>
        <div class="font-serif text-xl">Ruang Nada</div>
        <div class="text-xs text-outline">Panel Admin</div>
      </div>
    </div>
    <nav class="flex flex-col gap-1">${links}</nav>
    <div class="mt-8 rounded-lg bg-surface-container p-3 text-xs text-on-surface-variant">
      Batas sewa: 2 unit per anggota<br />
      Durasi standar: maksimal 5 hari
    </div>`;

  document.getElementById("topbar").innerHTML = `
    <span class="text-sm text-outline">Selamat datang kembali</span>
    <div class="flex items-center gap-4">
      <div class="text-right">
        <div class="text-sm font-semibold">${escapeHtml(user.name)}</div>
        <div class="text-xs text-outline">Admin</div>
      </div>
      <button onclick="logout()" title="Keluar" class="rounded-full bg-surface-container-high p-2 text-on-surface-variant hover:bg-error-container hover:text-on-error-container">
        <span class="icon">logout</span>
      </button>
    </div>`;
}

function setupMemberLayout(activePage, user) {
  const links = memberMenu
    .map(function (item) {
      const isActive = item.href === activePage;
      const color = isActive
        ? "bg-primary-container text-on-primary-container font-semibold"
        : "text-on-surface-variant hover:bg-surface-container-high";
      return `<a href="${item.href}" class="rounded-lg px-4 py-2 text-sm ${color}">${item.label}</a>`;
    })
    .join("");

  document.getElementById("topbar").innerHTML = `
    <div class="flex items-center gap-8">
      <div class="flex items-center gap-2">
        <span class="icon h-7 w-7 text-primary">music_note</span>
        <span class="font-serif text-xl">Ruang Nada</span>
      </div>
      <nav class="flex gap-1">${links}</nav>
    </div>
    <div class="flex items-center gap-4">
      <div class="text-right">
        <div class="text-sm font-semibold">${escapeHtml(user.name)}</div>
        <div class="text-xs text-outline">Anggota</div>
      </div>
      <button onclick="logout()" title="Keluar" class="rounded-full bg-surface-container-high p-2 text-on-surface-variant hover:bg-error-container hover:text-on-error-container">
        <span class="icon">logout</span>
      </button>
    </div>`;
}
