import requests
import time
from colorama import Fore, Style, init
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
init(autoreset=True)

url_register = "https://api-tg-app.midas.app/api/auth/register"
url_user = "https://api-tg-app.midas.app/api/user"
url_game = "https://api-tg-app.midas.app/api/game/play"
url_referral = "https://api-tg-app.midas.app/api/referral/status"
url_referral_claim = "https://api-tg-app.midas.app/api/referral/claim"
url_streak = "https://api-tg-app.midas.app/api/streak"

user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"

def read_cookie(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def read_init_data(file_path):
    with open(file_path, 'r') as file:
        init_data = [line.strip() for line in file.readlines()]
    return init_data

def get_auth_token(init_data):
    cookie = read_cookie('cookie.txt')
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://prod-tg-app.midas.app",
        "Referer": "https://prod-tg-app.midas.app/",
        "Sec-Ch-Ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\"",
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": "\"Android\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": user_agent,
        "Cookie": cookie
    }

    body = {
        "initData": init_data
    }

    try:
        response = requests.post(url_register, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        token = response.text
        if token:
            print(f"Berhasil mendapatkan token: ...{token[-20:]}")
            return token
        else:
            print(f"{Fore.RED}Token tidak ditemukan dalam respons.{Style.RESET_ALL}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error saat mendapatkan token otorisasi: {e}")
        return None

def get_request(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

def post_request(url, headers):
    try:
        response = requests.post(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

def claim_referral_rewards(headers, retries=3):
    cookie = read_cookie('cookie.txt')
    referral_headers = headers.copy()
    referral_headers.update({
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://prod-tg-app.midas.app",
        "Referer": "https://prod-tg-app.midas.app/",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Cookie": cookie
    })

    for attempt in range(retries):
        referral_data = get_request(url_referral, referral_headers)
        
        if referral_data:
            can_claim = referral_data.get("canClaim", False)
            if can_claim:
                print(f"{Fore.GREEN}Klaim tersedia! Mengeksekusi klaim...{Style.RESET_ALL}")
                claim_response = post_request(url_referral_claim, referral_headers)
                
                if claim_response:
                    total_points = claim_response.get("totalPoints", 0)
                    total_tickets = claim_response.get("totalTickets", 0)
                    print(f"Klaim berhasil! Anda mendapatkan {total_points} poin dan {total_tickets} tiket.")
                    return total_points, total_tickets
                else:
                    print(f"{Fore.RED}Error saat mengeksekusi klaim.{Style.RESET_ALL}")
                    return 0, 0
            else:
                print(f"{Fore.YELLOW}Tidak ada klaim yang tersedia saat ini.{Style.RESET_ALL}")
                return 0, 0
        else:
            print(f"{Fore.RED}Request error. Mencoba kembali... ({attempt+1}/{retries}){Style.RESET_ALL}")
            time.sleep(5)
            
    print("Gagal mengakses API referral setelah beberapa percobaan.")
    return 0, 0

def claim_streak_rewards(headers, retries=3):
    cookie = read_cookie('cookie.txt')
    streak_headers = headers.copy()
    streak_headers.update({
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://prod-tg-app.midas.app",
        "Referer": "https://prod-tg-app.midas.app/",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Cookie": cookie
    })

    for attempt in range(retries):
        streak_data = get_request(url_streak, streak_headers)
        
        if streak_data:
            claimable = streak_data.get("claimable", False)
            next_rewards = streak_data.get("nextRewards", {})
            points = next_rewards.get("points", 0)
            tickets = next_rewards.get("tickets", 0)

            if claimable:
                print(f"{Fore.GREEN}Klaim streak harian tersedia! Mengeksekusi klaim...{Style.RESET_ALL}")
                claim_response = post_request(url_streak, streak_headers)
                
                if claim_response:
                    points_claimed = claim_response.get("points", points)
                    tickets_claimed = claim_response.get("tickets", tickets)
                    print(f"Klaim streak harian berhasil! Anda mendapatkan {points_claimed} poin dan {tickets_claimed} tiket.")
                    return points_claimed, tickets_claimed
                else:
                    print(f"{Fore.RED}Error saat mengeksekusi klaim streak.{Style.RESET_ALL}")
                    return 0, 0
            else:
                print(f"{Fore.YELLOW}Tidak ada klaim streak yang tersedia saat ini.{Style.RESET_ALL}")
                return 0, 0
        else:
            print(f"{Fore.RED}Request error. Mencoba kembali... ({attempt+1}/{retries}){Style.RESET_ALL}")
            time.sleep(5)
            
    return 0, 0

def get_user_info(headers):
    cookie = read_cookie('cookie.txt')
    user_headers = headers.copy()
    user_headers.update({
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://prod-tg-app.midas.app",
        "Referer": "https://prod-tg-app.midas.app/",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Cookie": cookie
    })

    data = get_request(url_user, user_headers)
    if data:
        telegram_id = data.get("telegramId", "Tidak ditemukan")
        username = data.get("username", "Tidak ditemukan")
        first_name = data.get("firstName", "Tidak ditemukan")
        points = data.get("points", "Tidak ditemukan")
        tickets = data.get("tickets", 0)
        games_played = data.get("gamesPlayed", "Tidak ditemukan")
        streak_days_count = data.get("streakDaysCount", "Tidak ditemukan")

        print(f"Telegram ID: {telegram_id}")
        print(f"Username: {Fore.CYAN}{username}{Style.RESET_ALL}")
        print(f"First Name: {first_name}")
        print(f"Points: {points}")
        print(f"Tickets: {tickets}")
        print(f"Games Played: {games_played}")
        print(f"Streak Days Count: {streak_days_count}")
           
        return points, tickets
    else:
        print("Error: Tidak dapat mengakses API user.")
        return 0, 0

def play_game(headers):
    cookie = read_cookie('cookie.txt')
    game_headers = headers.copy()
    game_headers.update({
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://prod-tg-app.midas.app",
        "Referer": "https://prod-tg-app.midas.app/",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Cookie": cookie
    })

    total_points = 0
    taps = 9

    for i in range(taps):
        print(f"Memulai game {i+1}...")
        game_data = post_request(url_game, game_headers)
        if game_data:
            points_earned = game_data.get("points", 0)
            total_points += points_earned
               
            print(f"Round {i+1}: Earned {points_earned} points, Total Points: {total_points}")
               
            if total_points >= 16:
                print("Game selesai! Total poin telah mencapai 16.")
                break
        else:
            print(f"{Fore.RED}Error saat memainkan game.{Style.RESET_ALL}")
            break
           
        time.sleep(1)
       
    if total_points < 16:
        print(f"Game selesai! Anda telah mendapatkan {total_points} poin.")

    return total_points

if __name__ == "__main__":
    while True:
        init_data_list = read_init_data('auth.txt')
        total_points_sum = 0
        total_points_per_user = {}
           
        for init_data in init_data_list:
            print(f"\n{Fore.YELLOW}{'-'*50}{Style.RESET_ALL}")
            print(f"Memproses initData: ...{init_data[:10]}...")
               
            token = get_auth_token(init_data)
            if not token:
                print(f"{Fore.RED}Gagal mendapatkan token otorisasi.{Style.RESET_ALL}")
                continue

            headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": user_agent
            }

            user_total_points = 0

            print("Memeriksa klaim referral...")
            claimed_points, claimed_tickets = claim_referral_rewards(headers)
            user_total_points += claimed_points
            claimed_tickets_used = False

            print("Memeriksa klaim streak...")
            streak_points, streak_tickets = claim_streak_rewards(headers)
            user_total_points += streak_points
            claimed_tickets += streak_tickets


            if claimed_tickets > 0:
                print(f"Tiket dari klaim: {claimed_tickets}")
            else:
                print(f"Tidak ada tiket yang diperoleh dari klaim.")

            while True:
                print("Mendapatkan informasi user...")
                points, tickets = get_user_info(headers)
                user_total_points += points - user_total_points
                   
                if tickets == 0 and claimed_tickets > 0 and not claimed_tickets_used:
                    tickets += claimed_tickets
                    claimed_tickets_used = True
                   
                if tickets > 0:
                    print(f"\nTiket tersedia: {tickets}. Bermain game...")
                    earned_game_points = play_game(headers)
                    user_total_points += earned_game_points
                    tickets -= 1
                    claimed_tickets = 0
                    time.sleep(2)
                else:
                    print("Tiket habis. Tidak bisa bermain lagi.")
                    break

            total_points_per_user[init_data[:10]] = user_total_points
            total_points_sum += user_total_points

        for user, points in total_points_per_user.items():
                    print(f"Total points untuk user {user}: {points}")
           
        print(f"{Fore.GREEN}Total points dari semua user: {total_points_sum}{Style.RESET_ALL}")

        print(f"{Fore.YELLOW}Menunggu 60 menit sebelum eksekusi ulang...{Style.RESET_ALL}")
        time.sleep(3600)
