import tkinter as tk
from tkinter import messagebox
import random
import time
import pygame

CUMLELER = [
    "rocket launch",
    "solar panel",
    "space mission",
    "alien invasion",
    "galactic empire",
    "quantum drive",
    "wormhole jump"
]

TUZAK_HARFLER = set("xzjq")
MAX_HATA = 6
TAHMIN_SURE = 20  # saniye

pygame.mixer.init()

def ses_cal(dosya):
    try:
        pygame.mixer.music.load(dosya)
        pygame.mixer.music.play()
    except Exception:
        pass

def skor_kaydet(sonuc, cumle, sure):
    with open("scores.txt", "a", encoding="utf-8") as f:
        tarih = time.strftime("%Y-%m-%d %H:%M")
        f.write(f"{tarih} | {sonuc} | {cumle} | {sure} saniye\n")

class UzayliOyun:
    def __init__(self, master):
        self.master = master
        master.title("Uzaylıdan Kaçış")
        master.geometry("500x400")
        # master.resizable(False, False)  # Bunu kaldırdık, pencere büyütülebilir oldu
        # master.state("zoomed")  # İsterseniz açılışta tam ekran için bu satırı açabilirsiniz
        master.configure(bg="#222831")
        self.cumle = random.choice(CUMLELER)
        self.gorunen = ["_" if c.isalpha() else c for c in self.cumle]
        self.tahmin_edilen = set()
        self.hata = 0
        self.uzayli_adim = 0
        self.ipucu_kullanildi = False
        self.baslangic_zamani = time.time()
        self.sure = TAHMIN_SURE
        self.sure_id = None

        self.label_baslik = tk.Label(master, text="UZAYLIDAN KAÇIŞ", font=("Consolas", 22, "bold"), fg="#FFD369", bg="#222831")
        self.label_baslik.pack(pady=10)

        self.label_cumle = tk.Label(master, text=" ".join(self.gorunen), font=("Consolas", 20), fg="#EEEEEE", bg="#222831")
        self.label_cumle.pack(pady=10)

        self.label_uzayli = tk.Label(master, text=self.uzayli_grafik(), font=("Consolas", 18), fg="#00ADB5", bg="#222831")
        self.label_uzayli.pack(pady=10)

        self.label_sure = tk.Label(master, text=f"Kalan süre: {self.sure} sn", font=("Arial", 12), fg="#FFD369", bg="#222831")
        self.label_sure.pack()

        self.label_hak = tk.Label(master, text=f"Kalan Hak: {MAX_HATA - self.hata}", font=("Arial", 12), fg="#FFD369", bg="#222831")
        self.label_hak.pack(pady=5)

        self.label_skor = tk.Label(master, text="", font=("Arial", 10), fg="#EEEEEE", bg="#222831")
        self.label_skor.pack(pady=2)

        self.entry = tk.Entry(master, width=5, font=("Consolas", 16), justify="center")
        self.entry.pack()
        self.entry.focus()
        self.entry.bind("<Return>", lambda event: self.tahmin_et())

        self.btn_tahmin = tk.Button(master, text="Tahmin Et", command=self.tahmin_et, bg="#393E46", fg="#FFD369", font=("Arial", 12, "bold"))
        self.btn_tahmin.pack(pady=5)

        self.btn_ipucu = tk.Button(master, text="İpucu Al", command=self.ipucu_al, bg="#393E46", fg="#FFD369", font=("Arial", 12, "bold"))
        self.btn_ipucu.pack(pady=5)

        self.sureyi_baslat()
        self.skor_goster()

    def uzayli_grafik(self):
        return "👾" + "-" * (MAX_HATA - self.uzayli_adim) + "🚀"

    def sureyi_baslat(self):
        self.sure = TAHMIN_SURE
        self.guncelle_sure()

    def guncelle_sure(self):
        self.label_sure.config(text=f"Kalan süre: {self.sure} sn")
        if self.sure > 0:
            self.sure -= 1
            self.sure_id = self.master.after(1000, self.guncelle_sure)
        else:
            self.hata_arttir(tuzak=False, sure_bitti=True)

    def tahmin_et(self):
        harf = self.entry.get().lower()
        self.entry.delete(0, tk.END)
        if not harf or not harf.isalpha() or len(harf) != 1:
            return
        if harf in self.tahmin_edilen:
            return
        self.tahmin_edilen.add(harf)
        if harf in self.cumle:
            for i, c in enumerate(self.cumle):
                if c == harf:
                    self.gorunen[i] = harf
            self.label_cumle.config(text=" ".join(self.gorunen))
            ses_cal("correct.mp3")
            if "_" not in self.gorunen:
                self.oyun_bitti(kazandi=True)
            else:
                self.sure = TAHMIN_SURE
                self.label_sure.config(text=f"Kalan süre: {self.sure} sn")
        else:
            tuzak = harf in TUZAK_HARFLER
            self.hata_arttir(tuzak)
        self.label_hak.config(text=f"Kalan Hak: {MAX_HATA - self.hata}")

    def hata_arttir(self, tuzak=False, sure_bitti=False):
        adim = 2 if tuzak else 1
        self.hata += adim
        self.uzayli_adim += adim
        self.label_uzayli.config(text=self.uzayli_grafik())
        self.label_hak.config(text=f"Kalan Hak: {MAX_HATA - self.hata}")
        if sure_bitti:
            ses_cal("wrong.mp3")
            messagebox.showinfo("Süre Doldu", "Süre doldu! Uzaylı yaklaşıyor.")
        elif tuzak:
            ses_cal("wrong.mp3")
            messagebox.showinfo("Tuzak Harf", "Tuzak harf girdiniz! Uzaylı 2 adım yaklaştı.")
        else:
            ses_cal("wrong.mp3")
        self.sure = TAHMIN_SURE
        self.label_sure.config(text=f"Kalan süre: {self.sure} sn")
        if self.hata >= MAX_HATA:
            self.oyun_bitti(kazandi=False)
        else:
            if self.sure_id:
                self.master.after_cancel(self.sure_id)
            self.sureyi_baslat()

    def ipucu_al(self):
        if self.ipucu_kullanildi:
            return
        self.ipucu_kullanildi = True
        ilk_harf = next((c for c in self.cumle if c.isalpha()), None)
        if ilk_harf:
            for i, c in enumerate(self.cumle):
                if c == ilk_harf:
                    self.gorunen[i] = ilk_harf
            self.label_cumle.config(text=" ".join(self.gorunen))
        # Ekstra 1 yanlış sayılır
        self.hata_arttir(tuzak=False)
        self.label_hak.config(text=f"Kalan Hak: {MAX_HATA - self.hata}")
        self.btn_ipucu.config(state=tk.DISABLED)

    def oyun_bitti(self, kazandi):
        if self.sure_id:
            self.master.after_cancel(self.sure_id)
        toplam_sure = int(time.time() - self.baslangic_zamani)
        if kazandi:
            ses_cal("win.mp3")
            messagebox.showinfo("Tebrikler!", f"Kazandınız! Şifre: {self.cumle}")
            skor_kaydet("KAZANDI", self.cumle, toplam_sure)
        else:
            ses_cal("lose.mp3")
            messagebox.showinfo("Kaybettiniz!", f"Kaybettiniz! Şifre: {self.cumle}")
            skor_kaydet("KAYBETTİ", self.cumle, toplam_sure)
        self.skor_goster()
        if messagebox.askyesno("Oyun Bitti", "Tekrar oynamak ister misiniz?"):
            self.master.destroy()
            main()
        else:
            self.master.destroy()

    def skor_goster(self):
        try:
            with open("scores.txt", "r", encoding="utf-8") as f:
                satirlar = f.readlines()[-5:]
            skorlar = "".join(satirlar)
            self.label_skor.config(text="Son Skorlar:\n" + skorlar)
        except Exception:
            self.label_skor.config(text="")

def main():
    root = tk.Tk()
    UzayliOyun(root)
    root.mainloop()

if __name__ == "__main__":
    main()
