"""
============================================================
  PROJECT UTS : SISTEM NILAI MAHASISWA
  Penerapan Konsep Object Oriented Programming (OOP)
  ----------------------------------------------------------
  Pilar OOP yang diterapkan:
    1. Abstraction   -> class abstrak Mahasiswa
    2. Encapsulation -> atribut private + property setter
    3. Inheritance   -> subclass MahasiswaReguler & MahasiswaKaryawan
    4. Polymorphism  -> override method hitung_nilai_akhir()
============================================================
"""

from abc import ABC, abstractmethod
import json
import os


# ============================================================
# 1. ABSTRACT CLASS : Mahasiswa
# ============================================================
class Mahasiswa(ABC):
    """
    Base class (abstract) untuk semua jenis mahasiswa.
    Tidak dapat di-instansiasi langsung.
    """

    def __init__(self, nim, nama, tugas, uts, uas):
        # Menggunakan setter -> validasi otomatis dijalankan
        self.nim   = nim
        self.nama  = nama
        self.tugas = tugas
        self.uts   = uts
        self.uas   = uas

    # ---------------- PROPERTY : NIM ----------------
    @property
    def nim(self):
        return self.__nim

    @nim.setter
    def nim(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("NIM harus berupa teks dan tidak boleh kosong.")
        self.__nim = value.strip()

    # ---------------- PROPERTY : NAMA ----------------
    @property
    def nama(self):
        return self.__nama

    @nama.setter
    def nama(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nama tidak boleh kosong.")
        self.__nama = value.strip()

    # ---------------- PROPERTY : NILAI ----------------
    @property
    def tugas(self):
        return self.__tugas

    @tugas.setter
    def tugas(self, value):
        self.__tugas = self._validasi_nilai(value, "Tugas")

    @property
    def uts(self):
        return self.__uts

    @uts.setter
    def uts(self, value):
        self.__uts = self._validasi_nilai(value, "UTS")

    @property
    def uas(self):
        return self.__uas

    @uas.setter
    def uas(self, value):
        self.__uas = self._validasi_nilai(value, "UAS")

    # ---------------- HELPER ----------------
    def _validasi_nilai(self, value, field):
        try:
            angka = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Nilai {field} harus berupa angka.")
        if not (0 <= angka <= 100):
            raise ValueError(f"Nilai {field} harus berada di rentang 0 - 100.")
        return angka

    # ---------------- ABSTRACT METHOD ----------------
    @abstractmethod
    def hitung_nilai_akhir(self):
        """Wajib diimplementasikan ulang oleh setiap subclass."""
        pass

    # ---------------- METHOD UMUM ----------------
    def get_grade(self):
        na = self.hitung_nilai_akhir()
        if na >= 85:
            return "A"
        elif na >= 75:
            return "B"
        elif na >= 65:
            return "C"
        elif na >= 55:
            return "D"
        return "E"

    def get_status(self):
        return "LULUS" if self.hitung_nilai_akhir() >= 60 else "TIDAK LULUS"

    def jenis(self):
        return self.__class__.__name__

    def to_dict(self):
        """Konversi objek ke dict untuk disimpan ke JSON."""
        return {
            "jenis": self.jenis(),
            "nim":   self.nim,
            "nama":  self.nama,
            "tugas": self.tugas,
            "uts":   self.uts,
            "uas":   self.uas,
        }

    def __str__(self):
        return f"{self.nim} - {self.nama}"


# ============================================================
# 2. SUBCLASS : MahasiswaReguler
# ============================================================
class MahasiswaReguler(Mahasiswa):
    """Bobot: Tugas 30% | UTS 35% | UAS 35%."""

    def hitung_nilai_akhir(self):
        return (0.30 * self.tugas) + (0.35 * self.uts) + (0.35 * self.uas)


# ============================================================
# 3. SUBCLASS : MahasiswaKaryawan
# ============================================================
class MahasiswaKaryawan(Mahasiswa):
    """Bobot: Tugas 40% | UTS 30% | UAS 30%."""

    def hitung_nilai_akhir(self):
        return (0.40 * self.tugas) + (0.30 * self.uts) + (0.30 * self.uas)


# ============================================================
# 4. CLASS MANAGER : SistemNilai
# ============================================================
class SistemNilai:
    """
    Mengelola seluruh data mahasiswa (CRUD) + simpan/muat JSON.
    """

    FILE = "data_nilai.json"

    def __init__(self):
        self.__data = {}         # {nim: objek Mahasiswa}
        self.muat()

    # ---------------- CREATE ----------------
    def tambah(self, mhs: Mahasiswa):
        if not isinstance(mhs, Mahasiswa):
            raise TypeError("Objek harus turunan dari class Mahasiswa.")
        if mhs.nim in self.__data:
            raise ValueError(f"NIM {mhs.nim} sudah terdaftar.")
        self.__data[mhs.nim] = mhs

    # ---------------- READ ----------------
    def cari(self, nim):
        return self.__data.get(nim)

    def semua(self):
        return list(self.__data.values())

    def jumlah(self):
        return len(self.__data)

    # ---------------- DELETE ----------------
    def hapus(self, nim):
        if nim not in self.__data:
            raise KeyError(f"NIM {nim} tidak ditemukan.")
        del self.__data[nim]

    # ---------------- STATISTIK ----------------
    def rata_rata(self):
        data = self.semua()
        if not data:
            return 0.0
        return sum(m.hitung_nilai_akhir() for m in data) / len(data)

    # ---------------- PERSISTENSI ----------------
    def simpan(self):
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump([m.to_dict() for m in self.semua()], f, indent=4)

    def muat(self):
        if not os.path.exists(self.FILE):
            return
        try:
            with open(self.FILE, "r", encoding="utf-8") as f:
                isi = json.load(f)
            for d in isi:
                if d["jenis"] == "MahasiswaReguler":
                    obj = MahasiswaReguler(d["nim"], d["nama"],
                                           d["tugas"], d["uts"], d["uas"])
                else:
                    obj = MahasiswaKaryawan(d["nim"], d["nama"],
                                            d["tugas"], d["uts"], d["uas"])
                self.__data[obj.nim] = obj
        except (json.JSONDecodeError, KeyError):
            print("[!] File data rusak, diabaikan.")


# ============================================================
# 5. TAMPILAN / VIEW
# ============================================================
def tampil_tabel(sistem: SistemNilai):
    data = sistem.semua()
    if not data:
        print("\n[!] Belum ada data mahasiswa.")
        return

    print("\n" + "=" * 105)
    print(f"{'NIM':<12}{'Nama':<22}{'Jenis':<20}{'Tugas':<8}"
          f"{'UTS':<8}{'UAS':<8}{'Akhir':<10}{'Grade':<7}{'Status':<12}")
    print("-" * 105)
    for m in data:
        print(f"{m.nim:<12}{m.nama:<22}{m.jenis():<20}"
              f"{m.tugas:<8.1f}{m.uts:<8.1f}{m.uas:<8.1f}"
              f"{m.hitung_nilai_akhir():<10.2f}"
              f"{m.get_grade():<7}{m.get_status():<12}")
    print("=" * 105)


def tampil_detail(m: Mahasiswa):
    print("\n--- DETAIL MAHASISWA ---")
    print(f"Jenis       : {m.jenis()}")
    print(f"NIM         : {m.nim}")
    print(f"Nama        : {m.nama}")
    print(f"Nilai Tugas : {m.tugas}")
    print(f"Nilai UTS   : {m.uts}")
    print(f"Nilai UAS   : {m.uas}")
    print(f"Nilai Akhir : {m.hitung_nilai_akhir():.2f}")
    print(f"Grade       : {m.get_grade()}")
    print(f"Status      : {m.get_status()}")


def tampil_statistik(sistem: SistemNilai):
    data = sistem.semua()
    if not data:
        print("\n[!] Belum ada data mahasiswa.")
        return

    print("\n--- STATISTIK NILAI ---")
    print(f"Jumlah Mahasiswa   : {sistem.jumlah()}")
    print(f"Rata-rata Nilai    : {sistem.rata_rata():.2f}")

    distribusi = {}
    for m in data:
        g = m.get_grade()
        distribusi[g] = distribusi.get(g, 0) + 1

    print("Distribusi Grade   :")
    for g in sorted(distribusi):
        print(f"   Grade {g} : {distribusi[g]} mahasiswa")

    lulus = sum(1 for m in data if m.get_status() == "LULUS")
    print(f"Lulus              : {lulus} mahasiswa")
    print(f"Tidak Lulus        : {len(data) - lulus} mahasiswa")


# ============================================================
# 6. HELPER INPUT
# ============================================================
def input_mahasiswa(jenis):
    print(f"\n--- Tambah Mahasiswa {jenis.title()} ---")
    nim   = input("NIM         : ")
    nama  = input("Nama        : ")
    tugas = input("Nilai Tugas : ")
    uts   = input("Nilai UTS   : ")
    uas   = input("Nilai UAS   : ")

    if jenis == "reguler":
        return MahasiswaReguler(nim, nama, tugas, uts, uas)
    return MahasiswaKaryawan(nim, nama, tugas, uts, uas)


# ============================================================
# 7. MENU UTAMA
# ============================================================
def main():
    sistem = SistemNilai()

    while True:
        print("\n" + "=" * 45)
        print("   SISTEM NILAI MAHASISWA (OOP)")
        print("=" * 45)
        print("1. Tambah Mahasiswa Reguler")
        print("2. Tambah Mahasiswa Karyawan")
        print("3. Tampilkan Semua Data")
        print("4. Cari Mahasiswa (NIM)")
        print("5. Hapus Mahasiswa (NIM)")
        print("6. Statistik Nilai")
        print("7. Simpan Data ke File")
        print("0. Keluar")
        print("=" * 45)

        pilihan = input("Pilih menu [0-7]: ").strip()

        try:
            if pilihan == "1":
                mhs = input_mahasiswa("reguler")
                sistem.tambah(mhs)
                print(f"[OK] Mahasiswa '{mhs.nama}' berhasil ditambahkan.")

            elif pilihan == "2":
                mhs = input_mahasiswa("karyawan")
                sistem.tambah(mhs)
                print(f"[OK] Mahasiswa '{mhs.nama}' berhasil ditambahkan.")

            elif pilihan == "3":
                tampil_tabel(sistem)

            elif pilihan == "4":
                nim = input("Masukkan NIM: ").strip()
                m = sistem.cari(nim)
                if m is None:
                    print(f"[X] NIM '{nim}' tidak ditemukan.")
                else:
                    tampil_detail(m)

            elif pilihan == "5":
                nim = input("Masukkan NIM yang akan dihapus: ").strip()
                sistem.hapus(nim)
                print(f"[OK] Data NIM '{nim}' berhasil dihapus.")

            elif pilihan == "6":
                tampil_statistik(sistem)

            elif pilihan == "7":
                sistem.simpan()
                print(f"[OK] Data tersimpan ke '{SistemNilai.FILE}'.")

            elif pilihan == "0":
                sistem.simpan()   # auto-save saat keluar
                print("\nData telah disimpan. Terima kasih! 👋")
                break

            else:
                print("[!] Pilihan tidak valid, coba lagi.")

        except ValueError as e:
            print(f"[ERROR] {e}")
        except KeyError as e:
            print(f"[ERROR] {e}")
        except TypeError as e:
            print(f"[ERROR] {e}")
        except Exception as e:
            print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()