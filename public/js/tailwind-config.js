// Konfigurasi tema Tailwind.
// Warna-warna ini diambil dari desain Stitch, supaya tampilannya sama.
// Contoh pemakaian di HTML: class="bg-surface-container-low text-primary"

tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Latar dan permukaan
        "background": "#0b1326",
        "surface": "#0b1326",
        "surface-container-lowest": "#060e20",
        "surface-container-low": "#131b2e",
        "surface-container": "#171f33",
        "surface-container-high": "#222a3d",
        "surface-container-highest": "#2d3449",

        // Teks dan garis
        "on-surface": "#dae2fd",
        "on-surface-variant": "#cbc3d7",
        "outline": "#958ea0",
        "outline-variant": "#494454",

        // Warna utama (ungu)
        "primary": "#d0bcff",
        "on-primary": "#3c0091",
        "primary-container": "#a078ff",
        "on-primary-container": "#340080",
        "primary-fixed": "#e9ddff",

        // Warna pendukung
        "secondary": "#ffb95f",
        "tertiary": "#4edea3",
        "tertiary-container": "#00a572",
        "on-tertiary-container": "#00311f",

        // Warna error
        "error": "#ffb4ab",
        "error-container": "#93000a",
        "on-error-container": "#ffdad6"
      },
    },
  },
};
