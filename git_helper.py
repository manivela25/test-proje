import os
import subprocess
import sys


def run_command(command, error_msg="Komut çalıştırılırken hata oluştu."):
    """Sistem komutunu çalıştırır ve hata kontrolü yapar."""
    result = subprocess.run(
        command, shell=True, text=True, capture_output=True
    )
    if result.returncode != 0:
        print(f"\n[!] HATA: {error_msg}")
        print(f"Detay: {result.stderr.strip()}")
        return False, result.stderr
    return True, result.stdout


def check_git_installed():
    """Git'in sistemde kurulu olup olmadığını denetler."""
    success, _ = run_command(
        "git --version", "Sisteminizde Git kurulu görünmüyor."
    )
    if not success:
        print("Lütfen Git'i kurup tekrar deneyin: https://git-scm.com/")
        sys.exit(1)


def is_git_repo():
    """Bulunulan klasörün bir Git deposu olup olmadığını kontrol eder."""
    return os.path.exists(".git")


def get_current_branch():
    """Aktif dalın (branch) adını döndürür."""
    success, stdout = run_command("git branch --show-current")
    if success and stdout.strip():
        return stdout.strip()
    return "main"


def setup_new_repo():
    """Yeni projeyi GitHub'a ilk kez bağlayıp yükler."""
    print("\n--- Yeni Proje Yükleme (İlk Kurulum) ---")

    if not is_git_repo():
        run_command("git init", "Git başlatılamadı.")
        print("[+] Git deposu başlatıldı (git init).")

    remote_url = input(
        "\nGitHub Repository URL'sini girin (örn: https://github.com/kullanici/repo.git): "
    ).strip()
    if not remote_url:
        print("Geçerli bir URL girilmedi, işlem iptal edildi.")
        return

    # Remote origin ekleme / güncelleme
    run_command("git remote remove origin")
    success, _ = run_command(
        f"git remote add origin {remote_url}", "Remote origin eklenemedi."
    )
    if not success:
        return

    branch_name = (
            input("Kullanmak istediğiniz dal adı (Varsayılan: main): ").strip()
            or "main"
    )
    run_command(f"git branch -M {branch_name}")

    commit_msg = (
            input("İlk commit mesajı (Varsayılan: Initial commit): ").strip()
            or "Initial commit"
    )

    run_command("git add .", "Dosyalar sahnelenemedi (git add).")
    run_command(f'git commit -m "{commit_msg}"', "Commit oluşturulamadı.")

    print(f"\n[+] GitHub'a yükleniyor ({branch_name})...")
    push_success, _ = run_command(
        f"git push -u origin {branch_name}",
        "GitHub'a yüklenirken hata oluştu. Giriş bilgilerinizi ve depo izinlerinizi kontrol edin.",
    )

    if push_success:
        print("\n Proje GitHub'a başarıyla yüklendi!")


def update_existing_repo():
    """Mevcut depodaki değişiklikleri GitHub'a pushlar."""
    print("\n--- Mevcut Projeyi Güncelleme ---")

    if not is_git_repo():
        print(
            "[!] Bu klasörde bir Git deposu bulunamadı. Lütfen önce yeni kurulum yapın."
        )
        return

    # Durum kontrolü
    _, status = run_command("git status --short")
    if not status.strip():
        print("[i] Herhangi bir değişiklik tespit edilmedi. Çalışma alanı temiz.")
        return

    print("\nTespit edilen değişiklikler:")
    print(status)

    commit_msg = input("\nCommit mesajını girin: ").strip()
    if not commit_msg:
        print("Commit mesajı boş bırakılamaz. İşlem iptal edildi.")
        return

    current_branch = get_current_branch()
    branch_name = (
            input(f"Hedef dal (Varsayılan: {current_branch}): ").strip()
            or current_branch
    )

    # Değişiklikleri sahnele ve commit at
    print("\n[+] Dosyalar ekleniyor...")
    run_command("git add .", "Dosyalar eklenemedi.")

    print("[+] Commit oluşturuluyor...")
    run_command(f'git commit -m "{commit_msg}"', "Commit oluşturulamadı.")

    # İsteğe bağlı pull uyarısı / kontrolü
    pull_choice = (
        input(
            "Push öncesi uzak depodan çekme (git pull) yapılsın mı? (e/h, Varsayılan: e): "
        )
        .strip()
        .lower()
    )
    if pull_choice != "h":
        print("[+] Güncellemeler kontrol ediliyor (git pull)...")
        run_command(
            f"git pull origin {branch_name} --rebase",
            "Uzak değişiklikler çekilirken çakışma (conflict) oluştu.",
        )

    print(f"[+] GitHub'a gönderiliyor (git push origin {branch_name})...")
    push_success, _ = run_command(
        f"git push origin {branch_name}",
        "Push başarısız oldu. Dal izinlerini veya çakışmaları kontrol edin.",
    )

    if push_success:
        print("\n Projeniz başarıyla güncellendi!")


def main():
    check_git_installed()

    while True:
        print("\n===============================")
        print("   GitHub Yükleme & Güncelleme")
        print("===============================")
        print(f"Çalışma Dizini: {os.getcwd()}")
        print("1. Sıfırdan Yeni Proje Yükle (İlk Kurulum)")
        print("2. Mevcut Projeyi Güncelle (Add -> Commit -> Push)")
        print("3. Çıkış")

        choice = input("\nBir seçenek belirleyin (1-3): ").strip()

        if choice == "1":
            setup_new_repo()
            break
        elif choice == "2":
            update_existing_repo()
            break
        elif choice == "3":
            print("Çıkış yapıldı.")
            break
        else:
            print("[!] Geçersiz seçim. Lütfen 1, 2 veya 3 girin.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nİşlem kullanıcı tarafından iptal edildi.")
        sys.exit(0)
