import os
import googlemaps
import pandas as pd
from tqdm import tqdm
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import quote
import random

class GooglePlacesScraper:
    def __init__(self, api_key):
        """
        Inisialisasi scraper dengan Google Maps API Key
        
        Parameters:
        - api_key: API Key dari Google Cloud Console
        """
        self.client = googlemaps.Client(key=api_key)
        
        # Definisi kategori pencarian
        self.keywords = {
            'Restoran': ['restaurant', 'cafe', 'food', 'dining'],
            'Service AC': ['air conditioning service', 'ac repair', 'elektronik service'],
            'Hotel': ['hotel', 'penginapan', 'resort', 'guest house'],
            'pt':['PT', 'CV', 'UD'],
            'service':['service', 'repair', 'maintenance'],
            'klinik':['klinik', 'rumah sakit', 'dokter'],
            'toko':['toko', 'warung', 'minimarket'],
            'bank':['bank', 'atm', 'koperasi'],
            'sekolah':['sekolah', 'universitas', 'akademi'],
            'olahraga':['olahraga', 'gym', 'fitness'],
            'hiburan':['hiburan', 'bioskop', 'taman'],
        }

    def clean_phone_number(self, phone):
        """
        Clean phone number and convert to WhatsApp link format
        """
        if pd.isna(phone) or phone == '-':
            return None
        
        # Remove all non-digit characters
        clean_num = re.sub(r'[^\d]', '', str(phone))
        
        # Check if number starts with 0
        if clean_num.startswith('0'):
            clean_num = '62' + clean_num[1:]
        # If number starts with 62, keep it as is
        elif clean_num.startswith('62'):
            clean_num = clean_num
        # For numbers without country code, add 62
        else:
            clean_num = '62' + clean_num
        
        # Create WhatsApp link
        wa_link = f'wa.me/{clean_num}'
        
        return wa_link
    
    def search_places(self, lokasi, radius=5000):
        """
        Mencari tempat berdasarkan lokasi, kategori, dan radius
        
        Parameters:
        - lokasi: nama kota/wilayah
        - radius: jarak pencarian dalam meter (default 5 km)
        """
        # Geocoding untuk mendapatkan koordinat
        geocode_result = self.client.geocode(lokasi)
        if not geocode_result:
            raise ValueError(f"Lokasi {lokasi} tidak ditemukan")
        
        # Ambil latitude dan longitude
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        
        # Simpan hasil
        all_results = []
        
        # Progress bar untuk kategori
        for kategori, keyword_list in tqdm(self.keywords.items(), desc="Kategori"):
            print(f"\n🔍 Mencari {kategori} di {lokasi}")
            
            # Progress bar untuk setiap keyword
            for keyword in tqdm(keyword_list, desc=f"Pencarian {kategori}", colour='green'):
                try:
                    # Cari tempat menggunakan Places API
                    places_result = self.client.places_nearby(
                        location=(lat, lng),
                        radius=radius,
                        keyword=keyword,
                        type=self.map_keyword_to_type(keyword)
                    )
                    
                    # Proses setiap tempat
                    for place in places_result.get('results', []):
                        # Dapatkan detail lengkap
                        place_details = self.get_place_details(place['place_id'])
                        
                        # Get phone number and create WhatsApp link
                        phone_number = place_details.get('formatted_phone_number', '-')
                        whatsapp_link = self.clean_phone_number(phone_number)
                        
                        # Ekstrak informasi
                        result = {
                            'Nama': place.get('name', '-'),
                            'Kategori': kategori,
                            'Alamat': place_details.get('formatted_address', '-'),
                            'Website': place_details.get('website', '-'),
                            'No HP': phone_number,
                            'WhatsApp Link': whatsapp_link if whatsapp_link else '-',
                            'Sosial Media': self.extract_social_media(place_details)
                        }
                        
                        all_results.append(result)
                        
                except Exception as e:
                    print(f"❌ Kesalahan pada pencarian {keyword}: {e}")
        
        return all_results
    
    def get_place_details(self, place_id):
        """
        Mendapatkan detail lengkap suatu tempat
        """
        try:
            details = self.client.place(place_id)
            return details.get('result', {})
        except Exception as e:
            print(f"❌ Gagal mendapatkan detail tempat: {e}")
            return {}
    
    def extract_social_media(self, place_details):
        """
        Ekstrak link sosial media dari detail tempat
        """
        try:
            # Cek URL dalam detail
            url = place_details.get('website', '')
            
            # Identifikasi platform sosial media
            social_platforms = [
                'facebook.com', 
                'instagram.com', 
                'twitter.com', 
                'linkedin.com'
            ]
            
            for platform in social_platforms:
                if platform in url.lower():
                    return url
            
            return '-'
        except:
            return '-'
    
    def map_keyword_to_type(self, keyword):
        """
        Memetakan keyword ke tipe tempat Google Places
        """
        keyword = keyword.lower()
        if 'restaurant' in keyword or 'cafe' in keyword or 'food' in keyword:
            return 'restaurant'
        elif 'hotel' in keyword or 'resort' in keyword:
            return 'lodging'
        elif 'service' in keyword or 'repair' in keyword:
            return 'services'
        return None
    
    def save_to_excel(self, results, filename):
        """
        Simpan hasil ke file Excel
        """
        print("\n💾 Menyimpan data ke Excel...")
        df = pd.DataFrame(results)
        
        # Hapus duplikasi berdasarkan nama
        df = df.drop_duplicates(subset=['Nama'])
        
        # Remove rows where phone number is invalid or missing
        print("🧹 Membersihkan data nomor telepon tidak valid...")
        df_clean = df[df['WhatsApp Link'] != '-'].copy()
        
        # Save both full and cleaned datasets
        df.to_excel(filename, index=False, engine='openpyxl')
        cleaned_filename = filename.replace('.xlsx', '_clean.xlsx')
        df_clean.to_excel(cleaned_filename, index=False, engine='openpyxl')
        
        print(f"✅ Data lengkap berhasil disimpan di {filename}")
        print(f"✅ Data bersih berhasil disimpan di {cleaned_filename}")
        print(f"📊 Total data yang ditemukan: {len(df)}")
        print(f"📊 Total data dengan WhatsApp valid: {len(df_clean)}")
        print(f"📊 Total data yang dihapus: {len(df) - len(df_clean)}")

class WhatsAppSender:
    def __init__(self):
        """Initialize the WhatsApp sender with Chrome WebDriver"""
        print("🔧 Menyiapkan Chrome Driver...")
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--start-maximized")
        
        # Setup Chrome driver with automatic installation
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
    
    def login(self):
        """Open WhatsApp Web and wait for manual login"""
        print("🌐 Membuka WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        print("⚠️ Silakan scan QR Code untuk login WhatsApp Web")
        
        # Wait for WhatsApp to load
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
        ))
        print("✅ Login berhasil!")
    
    def send_message(self, phone_number, business_name):
        """Send a message to a specific phone number"""
        try:
            # Remove 'wa.me/' from phone number if present
            phone_number = phone_number.replace('wa.me/', '')
            
            # Format the message
            message = f"""Perkenalkan, saya Ridha Fahmi dari Geografis Design. Kami menyediakan layanan pembuatan website dan company profile yang profesional untuk membantu bisnis seperti {business_name} tampil lebih menarik dan terpercaya di era digital.

Apakah Anda memiliki waktu sejenak untuk mendiskusikannya? Saya akan dengan senang hati menjelaskan lebih lanjut bagaimana layanan kami dapat mendukung perkembangan bisnis Anda."""

            # Create WhatsApp Web URL
            url = f"https://web.whatsapp.com/send?phone={phone_number}&text={quote(message)}"
            self.driver.get(url)
            
            # Wait for chat to load and send button to appear
            send_button = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//span[@data-icon="send"]')
            ))
            
            # Random delay to seem more human-like
            time.sleep(random.uniform(1.5, 3.0))
            
            # Click send button
            send_button.click()
            
            # Wait for message to be sent
            time.sleep(random.uniform(2.0, 4.0))
            
            return True
            
        except TimeoutException:
            print(f"❌ Timeout error untuk nomor {phone_number}")
            return False
        except Exception as e:
            print(f"❌ Error untuk nomor {phone_number}: {str(e)}")
            return False
    
    def send_bulk_messages(self, excel_file):
        """Send messages to all numbers in the Excel file"""
        try:
            # Read Excel file
            print(f"📖 Membaca file {excel_file}...")
            df = pd.read_excel(excel_file)
            
            if 'WhatsApp Link' not in df.columns or 'Nama' not in df.columns:
                raise ValueError("Column 'WhatsApp Link' atau 'Nama' tidak ditemukan di Excel file")
            
            # Login to WhatsApp
            self.login()
            
            # Wait for initial setup
            time.sleep(5)
            
            # Track success and failures
            successful = 0
            failed = 0
            
            # Process each number
            total = len(df)
            for index, row in df.iterrows():
                phone = row['WhatsApp Link']
                business_name = row['Nama']
                
                # Skip if no phone number
                if pd.isna(phone) or phone == '-':
                    continue
                
                print(f"\n📱 Mengirim pesan ke {business_name} ({phone})")
                print(f"📝 Progress: {index + 1}/{total}")
                
                # Send message
                if self.send_message(phone, business_name):
                    successful += 1
                    print("✅ Pesan terkirim!")
                else:
                    failed += 1
                    print("❌ Gagal mengirim pesan")
                
                # Random delay between messages
                delay = random.uniform(10.0, 15.0)
                print(f"⏳ Menunggu {delay:.1f} detik sebelum pesan berikutnya...")
                time.sleep(delay)
            
            # Print summary
            print("\n📊 Ringkasan Pengiriman:")
            print(f"✅ Berhasil: {successful}")
            print(f"❌ Gagal: {failed}")
            print(f"📱 Total: {total}")
            
        except Exception as e:
            print(f"❌ Terjadi kesalahan: {str(e)}")
        finally:
            # Safely close the browser
            self.quit()
            
    def quit(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

def print_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("🛠️  BUSINESS TOOLS MENU")
    print("="*50)
    print("1. 🔍 Google Places Scraper")
    print("2. 📱 WhatsApp Bulk Sender")
    print("3. ❌ Keluar")
    print("="*50)

def run_places_scraper():
    """Run the Google Places Scraper functionality"""
    print("\n🔍 GOOGLE PLACES SCRAPER")
    print("="*50)
    
    # Get API Key
    API_KEY = input("Masukkan Google Places API Key: ")
    
    # Get location
    lokasi = input("Masukkan nama kota/wilayah: ")
    
    try:
        # Initialize and run scraper
        scraper = GooglePlacesScraper(API_KEY)
        results = scraper.search_places(lokasi)
        
        # Save results
        filename = f'google_places_data_{lokasi}.xlsx'
        scraper.save_to_excel(results, filename)
        
        print("\n✅ Scraping selesai! Data tersimpan di:", filename)
        
        # Ask if user wants to send WhatsApp messages
        send_wa = input("\nApakah Anda ingin mengirim pesan WhatsApp ke data yang baru diambil? (y/n): ")
        if send_wa.lower() == 'y':
            # Use the clean version of the file
            clean_filename = filename.replace('.xlsx', '_clean.xlsx')
            run_whatsapp_sender(clean_filename)
            
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {str(e)}")

def run_whatsapp_sender(excel_file=None):
    """Run the WhatsApp Sender functionality"""
    print("\n📱 WHATSAPP BULK SENDER")
    print("="*50)
    
    try:
        # If file not provided, ask for input
        if not excel_file:
            excel_file = input("Masukkan nama file Excel: ")
        
        # Confirm before starting
        total_rows = len(pd.read_excel(excel_file))
        print(f"\n⚠️ Akan mengirim pesan ke {total_rows} nomor")
        print("\nFormat pesan yang akan dikirim:")
        print("---")
        print("""Perkenalkan, saya Ridha Fahmi dari Geografis Design. Kami menyediakan layanan pembuatan website dan company profile yang profesional untuk membantu bisnis seperti [nama bisnis] tampil lebih menarik dan terpercaya di era digital.

Apakah Anda memiliki waktu sejenak untuk mendiskusikannya? Saya akan dengan senang hati menjelaskan lebih lanjut bagaimana layanan kami dapat mendukung perkembangan bisnis Anda.""")
        print("---")
        
        confirm = input("\nLanjutkan pengiriman? (y/n): ")
        
        if confirm.lower() == 'y':
            sender = WhatsAppSender()
            sender.send_bulk_messages(excel_file)
        else:
            print("❌ Dibatalkan")
            
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {str(e)}")

def main():
    """Main program loop"""
    print("\n🌟 Selamat datang di Business Tools!")
    print("Tool ini membantu Anda mengumpulkan data bisnis dan mengirim pesan WhatsApp.")
    
    while True:
        try:
            print_menu()
            choice = input("\nPilih menu (1-3): ")
            
            if choice == '1':
                run_places_scraper()
            elif choice == '2':
                run_whatsapp_sender()
            elif choice == '3':
                print("\n👋 Terima kasih telah menggunakan Business Tools!")
                break
            else:
                print("\n❌ Menu tidak valid. Silakan pilih 1-3.")
            
            # Ask if user wants to continue
            if choice in ['1', '2']:
                input("\nTekan Enter untuk kembali ke menu utama...")
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Program dihentikan oleh pengguna.")
            break
        except Exception as e:
            print(f"\n❌ Terjadi kesalahan: {str(e)}")
            input("\nTekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Terjadi kesalahan fatal: {str(e)}")
    finally:
        print("\n👋 Program selesai.")