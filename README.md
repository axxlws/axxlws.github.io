# Portofolio Hidrologi dan Hidrogeologi Axel

Website portofolio statis untuk Axel Widjanarko Sibarani.

## Membuka website

Buka `index.html` di peramban. Website tidak memerlukan instalasi atau koneksi internet.

## Isi

- `index.html` - struktur dan konten website
- `styles.css` - tampilan responsif
- `script.js` - menu navigasi versi ponsel
- `assets/` - visual yang diekstrak dari laporan dan presentasi proyek yang disetujui untuk portofolio

## Catatan

Versi ini menampilkan studi hidrologi dan hidrogeologi untuk lamaran di bidang sumber daya air, termasuk pekerjaan lapangan, pemodelan, dan penulisan teknis.

## Visual studi Wanam

`tools/build_wanam_assets.py` membuat peta lima DAS dan kurva durasi aliran dari berkas proyek lokal. Jalankan dengan lokasi folder proyek Wanam dan folder keluaran gambar, misalnya:

```bash
python tools/build_wanam_assets.py "<folder proyek Wanam>" assets
```

Repository menyimpan gambar hasil, bukan data mentah. Kurva memakai kolom `Total Inflow (M3/S) + Baseflow` pada CSV terbaru di folder `+ Baseflow RDF` untuk kelima outlet. Q80 dihitung sebagai persentil ke-20 dari masing-masing seri 4.017 nilai harian. Baseflow analog berasal dari observasi DAS Buda yang difilter dengan metode Eckhardt, dipindahkan dengan rasio luas DAS, lalu dipasangkan berdasarkan urutan hari sebagai skenario; bukan observasi serentak di Wanam.

## Visual studi MODFLOW

Tiga gambar MODFLOW diekstrak dari presentasi akademik `UAS - Pemodelan Air Tanah. - Presentpptx.pptx`: zonasi geologi 3D (slide 3), kontur head steady-state (slide 10), dan penampang intrusi air laut (slide 16). Domain studi merupakan pulau sintetis. Presentasi tidak menyajikan validasi lapangan, sehingga hasilnya ditulis sebagai keluaran skenario, bukan prediksi kondisi nyata atau dasar desain operasional. Grafik dewatering pada slide 19 tidak digunakan karena sumbu waktunya perlu ditinjau kembali.
