import cloudscraper
import time

CYAN = '\033[96m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def post_request(url, headers, payload=None):
    scraper = cloudscraper.create_scraper()
    response = scraper.post(url, json=payload, headers=headers)
    
    if response.status_code == 200 or response.status_code == 201:
        try:
            return response.json(), response.cookies
        except ValueError:
            return response.text, response.cookies
    else:
        print(f"akwowkw Request gagal dengan status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return None, None

def get_request(url, headers):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            print("Response bukan JSON.")
            return None
    else:
        print(f"akwowkw Request gagal mendapatkan informasi dengan status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return None

def read_init_data(filename):
    try:
        with open(filename, 'r') as file:
            init_data_list = [line.strip() for line in file if line.strip()]
            return init_data_list
    except FileNotFoundError:
        print(f"File {filename} tidak ditemukan.")
        return []

def get_streak_info(headers):
    url_streak = "https://api-tg-app.midas.app/api/streak"
    streak_data = get_request(url_streak, headers)

    if streak_data:
        streak_days_count = streak_data.get("streakDaysCount", "Tidak ditemukan")
        next_rewards = streak_data.get("nextRewards", {})
        points = next_rewards.get("points", "Tidak ditemukan")
        tickets = next_rewards.get("tickets", "Tidak ditemukan")
        claimable = streak_data.get("claimable", False)

        print(f"Streak Days Count: {streak_days_count}")
        print(f"Hadiah yang bisa di klaim - Points: {GREEN}{points}{RESET}, Tickets: {GREEN}{tickets}{RESET}")
        
        if claimable:
            print(f"{GREEN}Streak tersedia untuk diklaim.{RESET}")
            claim_streak(headers)
        else:
            print(f"{YELLOW}Streak tidak tersedia untuk diklaim.{RESET}")
    else:
        print("Error: Tidak dapat mengakses API streak.")

def claim_streak(headers):
    url_claim = "https://api-tg-app.midas.app/api/streak"
    response, _ = post_request(url_claim, headers)
        
    if response:
        points = response.get("points", "Tidak ditemukan")
        tickets = response.get("tickets", "Tidak ditemukan")
        print(f"{GREEN}Klaim tiket dan poin harian berhasil!{RESET}") 
    else:
        print(f"{RED}Error: Gagal melakukan klaim harian.{RESET}") 
        return 0, 0

def get_user_info(headers):
    url_user = "https://api-tg-app.midas.app/api/user"
    user_data = get_request(url_user, headers)
    
    if user_data:
        telegram_id = user_data.get("telegramId", "Tidak ditemukan")
        username = user_data.get("username", "Tidak ditemukan")
        first_name = user_data.get("firstName", "Tidak ditemukan")
        points = user_data.get("points", "Tidak ditemukan")
        tickets = user_data.get("tickets", 0)
        games_played = user_data.get("gamesPlayed", "Tidak ditemukan")
        streak_days_count = user_data.get("streakDaysCount", "Tidak ditemukan")
        
        print(f"Telegram ID: {telegram_id}")
        print(f"Username: {CYAN}{username}{RESET}")
        print(f"First Name: {CYAN}{first_name}{RESET}")
        print(f"Points: {GREEN}{points}{RESET}") 
        if tickets == 0:
            print(f"Tickets: {RED}{tickets}{RESET}") 
        else:
            print(f"Tickets: {GREEN}{tickets}{RESET}") 
        print(f"Games Played: {games_played}")
        print(f"Streak Days Count: {streak_days_count}")
        
        return tickets, points
    else:
        print("Error: Tidak dapat mengakses API user.")
        return 0, 0

def check_referral_status(headers):
    url_referral = "https://api-tg-app.midas.app/api/referral/status"
    url_referral_claim = "https://api-tg-app.midas.app/api/referral/claim"
    
    referral_data = get_request(url_referral, headers)
    
    if referral_data:
        can_claim = referral_data.get("canClaim", False)
        if can_claim:
            print(f"{GREEN}Klaim refferal tersedia! Mengeksekusi klaim...{RESET}")
            claim_response, _ = post_request(url_referral_claim, headers)
            
            if claim_response:
                total_points = claim_response.get("totalPoints", 0)
                total_tickets = claim_response.get("totalTickets", 0)
                print(f"{GREEN}Klaim refferal berhasil!{RESET} Anda mendapatkan {GREEN}{total_points}{RESET} poin dan {GREEN}{total_tickets}{RESET} tiket.")
                return total_points, total_tickets
            else:
                print(f"{RED}Error saat mengeksekusi klaim refferal.{RESET}")
                return 0, 0
        else:
            print(f"{YELLOW}Tidak ada klaim refferal yang tersedia saat ini.{RESET}")
            return 0, 0
    else:
        print(f"{RED}Request error.{RESET} {YELLOW}Mencoba kembali...{RESET}")
        return 0, 0

def play_game(headers, tickets):
    url_game = "https://api-tg-app.midas.app/api/game/play"
    total_points = 0

    while tickets > 0:
        for i in range(3, 0, -1):
            print(f"Memulai game dalam {YELLOW}{i}{RESET} detik...", end='\r')
            time.sleep(1)

        print(f"\n{YELLOW}Memulai game ...{RESET}")
        game_data, _ = post_request(url_game, headers)
    
        if game_data:
            points_earned = game_data.get("points", 0)
            total_points += points_earned
            tickets -= 1 
            print(f"Mendapatkan {GREEN}{points_earned} poin{RESET}, Total Points: {GREEN}{total_points}{RESET}, Sisa Tiket: {YELLOW}{tickets}{YELLOW}")
        else:
            print(f"{RED}Error saat bermain game.{RESET}")
            break

    return total_points

def process_init_data(init_data):
    print(f"\nMemproses initData: {YELLOW}...{init_data[-20:]}{RESET}")

    url_register = "https://api-tg-app.midas.app/api/auth/register"
    headers_register = {
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://prod-tg-app.midas.app",
        "Referer": "https://prod-tg-app.midas.app/",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": '"Android"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    }

    payload = {
        "initData": init_data
    }

    response_text, cookies = post_request(url_register, headers_register, payload)

    if response_text:
        print(f"Token yang didapat: {YELLOW}...{response_text[-20:]}{RESET}") 
        cookies_dict = cookies.get_dict()
        cookies_preview = {key: f"...{value[-20:]}" for key, value in cookies_dict.items()} 
        print(f"Cookies yang diterima: {YELLOW}{cookies_preview}{RESET}")

        token = response_text

        headers_user = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://prod-tg-app.midas.app",
            "Referer": "https://prod-tg-app.midas.app/",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Authorization": f"Bearer {token}",
            "Cookie": "; ".join([f"{key}={value}" for key, value in cookies.get_dict().items()])
        }

        get_streak_info(headers_user)

        check_referral_status(headers_user)

        tickets, points = get_user_info(headers_user)
        
        if tickets > 0:
            total_points = play_game(headers_user, tickets)
            print(f"Total Points setelah bermain game: {GREEN}{total_points}{RESET}")
        else:
            print(f"{YELLOW}Tidak ada tiket yang tersedia untuk bermain game.{RESET}")
    else:
        print("Error: Tidak dapat mendapatkan token.")

def main():
    init_data_list = read_init_data('auth.txt')
    
    while True:
        for init_data in init_data_list:
            process_init_data(init_data)
            print("Countdown 10 detik sebelum memproses akun berikutnya...")
            for i in range(10, 0, -1):
                print(f"{i} detik...", end="\r")
                time.sleep(1)
        
        print("Selesai memproses semua initData. Memulai ulang dalam 8 jam...")
        for i in range(8 * 3600, 0, -1):
            hours, remainder = divmod(i, 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"{hours:02}:{minutes:02}:{seconds:02}", end="\r")
            time.sleep(1)

if __name__ == "__main__":
    main()
        
