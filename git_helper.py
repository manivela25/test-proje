import os
import subprocess
import sys


def run_command(command, error_msg="Komut calistirilirken hata olustu."):
    """Sistem komutunu calistirir ve hata kontrolu yapar."""
    result = subprocess.run(
        command, shell=True, text=True, capture_output=True
    )
    if result.returncode != 0:
        print(f"\n[!] HATA: {error_msg}")
        print(f"Detay: {result.stderr.strip()}")
        return False, result.stderr
    return True, result.stdout


def check_git_installed():
    """Git'in sistemde kurulu olup olmadigini denetler."""
    success, _ = run_command(
        "git --version", "Sisteminizde Git kurulu gorunmuyor."
    )
    if not success:
        print("Lutfen Git'i kurup tekrar deneyin: https://git-scm.com/")
        sys.exit(1)


def is_git_repo():
    """Bulunulan klasorun bir Git deposu olup olmadigini kontrol eder."""
    return os.path.exists(".git")


def get_current_branch():
    """Aktif dalin (branch) adini dondurur."""
    success, stdout = run_command("git branch --show-current")
    if success and stdout.strip():
        return stdout.strip()
    return "main"


def select_project_directory():
    """Kullanicidan hedef proje klasorunu alir ve o dizine gecer."""
    while True:
        path = input(
            "\nProje klasorunun yolunu girin (Bulundugunuz klasor icin Enter): "
        ).strip()

        # Terminalde surukle-birak yapildiginda olusan tirnaklari temizle
        path = path.strip("\"'")

        if not path:
            print(f"[i] Mevcut dizin secildi: {os.getcwd()}")
            return True

        if os.path.isdir(path):
            os.chdir(path)
            print(f"[+] Calisma dizini degistirildi: {os.getcwd()}")
            return True
        else:
            print("[!] Belirtilen klasor yolu bulunamadi. Tekrar deneyin.")


def setup_new_repo():
    """Yeni projeyi GitHub'a ilk kez baglayip yukler."""
    print("\n==========================================")
    print("      Yeni Proje Yukleme (Ilk Kurulum)    ")
    print("==========================================")

    if not select_project_directory():
        return

    if not is_git_repo():
        run_command("git init", "Git baslatilamadi.")
        print("[+] Git deposu baslatildi (git init).")
    else:
        print("[i] Bu klasorde zaten bir Git deposu mevcut.")

    remote_url = input(
        "\nGitHub Repository URL'sini girin (orn: https://github.com/kullanici/repo.git): "
    ).strip()
    if not remote_url:
        print("Gecerli bir URL girilmedi, islem iptal edildi.")
        return

    # Remote origin guncelleme
    run_command("git remote remove origin")
    success, _ = run_command(
        f"git remote add origin {remote_url}", "Remote origin eklenemedi."
    )
    if not success:
        return

    branch_name = (
            input("Kullanmak istediginiz dal adi (Varsayilan: main): ").strip()
            or "main"
    )
    run_command(f"git branch -M {branch_name}")

    commit_msg = (
            input("Ilk commit mesaji (Varsayilan: Initial commit): ").strip()
            or "Initial commit"
    )

    run_command("git add .", "Dosyalar eklenemedi (git add).")
    run_command(f'git commit -m "{commit_msg}"', "Commit olusturulamadi.")

    print(f"\n[+] GitHub'a yukleniyor ({branch_name})...")
    push_success, _ = run_command(
        f"git push -u origin {branch_name}",
        "GitHub'a yuklenirken hata olustu. Yetkilendirme veya baglanti ayarlarini kontrol edin.",
    )

    if push_success:
        print("\n Proje GitHub'a basariyla yuklendi!")


def update_existing_repo():
    """Mevcut depodaki degisiklikleri GitHub'a pushlar."""
    print("\n==========================================")
    print("         Mevcut Projeyi Guncelleme        ")
    print("==========================================")

    if not select_project_directory():
        return

    if not is_git_repo():
        print(
            "\n[!] HATA: Secilen klasorde bir Git deposu (.git) bulunamadi!"
        )
        print("    Eger bu yeni bir projeyse ana menuden 1. secenegi kullanin.")
        return

    # Degisiklik kontrolu
    _, status = run_command("git status --short")
    if not status.strip():
        print("\n[i] Herhangi bir degisiklik tespit edilmedi. Calisma alani temiz.")
        return

    print("\nTespit edilen degisiklikler:")
    print(status)

    commit_msg = input("\nCommit mesajini girin: ").strip()
    if not commit_msg:
        print("Commit mesaji bos birakilamaz. Islem iptal edildi.")
        return

    current_branch = get_current_branch()
    branch_name = (
            input(f"Hedef dal (Varsayilan: {current_branch}): ").strip()
            or current_branch
    )

    print("\n[+] Dosyalar ekleniyor (git add .)...")
    run_command("git add .", "Dosyalar eklenemedi.")

    print(f"[+] Commit olusturuluyor: '{commit_msg}'...")
    run_command(f'git commit -m "{commit_msg}"', "Commit olusturulamadi.")

    pull_choice = (
        input(
            "Push oncesi uzak depodan cekme (git pull) yapilsin mi? (e/h, Varsayilan: e): "
        )
        .strip()
        .lower()
    )
    if pull_choice != "h":
        print("[+] Guncellemeler kontrol ediliyor (git pull)...")
        run_command(
            f"git pull origin {branch_name} --rebase",
            "Uzak degisiklikler cekilirken cakisma (conflict) olustu.",
        )

    print(f"[+] GitHub'a gonderiliyor (git push origin {branch_name})...")
    push_success, _ = run_command(
        f"git push origin {branch_name}",
        "Push basarisiz oldu. Dal izinlerini veya cakismalari kontrol edin.",
    )

    if push_success:
        print("\n Projeniz basariyla guncellendi!")


def main():
    check_git_installed()

    while True:
        print("\n===============================")
        print("   GitHub Yonetim Araci")
        print("===============================")
        print("1. Yeni Proje Yukle (Ilk Kurulum)")
        print("2. Mevcut Projeyi Guncelle (Push)")
        print("3. Cikis")

        choice = input("\nBir islem secin (1-3): ").strip()

        if choice == "1":
            setup_new_repo()
            break
        elif choice == "2":
            update_existing_repo()
            break
        elif choice == "3":
            print("Cikis yapildi.")
            break
        else:
            print("[!] Gecersiz secim. Lutfen 1, 2 veya 3 yazin.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nIslem kullanici tarafindan iptal edildi.")
        sys.exit(0)
