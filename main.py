import sys
import os
import requests
import json
from datetime import datetime
from threading import Thread
import time

try:
    from pynput import keyboard
except ImportError:
    print("pynput kütüphanesi bulunamadı. Yüklemek için: pip install pynput")
    sys.exit(1)

class BarcodeScannerApp:
    def __init__(self, hera_printer_url="http://localhost:8088"):
        self.hera_printer_url = hera_printer_url
        self.current_barcode = ""
        self.listener = None
        self.running = False
        
    def on_key_press(self, key):
        """Klavye tuşuna basıldığında çağrılır"""
        try:
            # Enter tuşu - barkod okuma tamamlandı
            if key == keyboard.Key.enter:
                if self.current_barcode.strip():
                    self.process_barcode(self.current_barcode.strip())
                    self.current_barcode = ""
                return False  # Enter'dan sonra yeni barkod için hazır ol
            
            # Karakter tuşları
            if hasattr(key, 'char') and key.char:
                self.current_barcode += key.char
            # Özel tuşlar (backspace, space vs.)
            elif key == keyboard.Key.backspace:
                if self.current_barcode:
                    self.current_barcode = self.current_barcode[:-1]
            elif key == keyboard.Key.space:
                self.current_barcode += " "
                
        except Exception as e:
            print(f"Key press error: {e}")
    
    def process_barcode(self, barcode_data):
        """Okunan barkodu işle ve yazdır"""
        print(f"\n📦 Barkod okundu: {barcode_data}")
        
        try:
            url = f"{self.hera_printer_url}/api/barcodeScanner/print"

            payload = {
                "SERIAL_NUMBER": barcode_data
            }
            
            headers = {"Content-Type": "application/json"}
            
            print(f"🖨️  Yazdırma isteği gönderiliyor...")
            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Etiket başarıyla yazdırıldı!")
                print(f"   Response: {response.text}")
            else:
                print(f"❌ Yazdırma hatası: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Bağlantı hatası: heraPrinterApplication çalışmıyor olabilir ({self.hera_printer_url})")
        except requests.exceptions.Timeout:
            print(f"❌ Zaman aşımı: Yazdırma işlemi çok uzun sürdü")
        except Exception as e:
            print(f"❌ Hata: {e}")
    
    def start_listening(self):
        """Barkod okuyucuyu dinlemeye başla"""
        print("=" * 60)
        print("🔍 Barkod Okuyucu Uygulaması Başlatıldı")
        print("=" * 60)
        print(f"📡 heraPrinterApplication URL: {self.hera_printer_url}")
        print(f"⌨️  Barkod okuyucuyu kullanarak bir barkod okutun...")
        print(f"💡 Çıkmak için Ctrl+C basın")
        print("=" * 60)
        print()
        
        self.running = True
        
        try:
            while self.running:
                # Klavye dinleyicisini başlat
                with keyboard.Listener(on_press=self.on_key_press) as listener:
                    listener.join()
                    
                # Enter'a basıldıktan sonra kısa bir bekleme
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Uygulama kapatılıyor...")
            self.running = False
        except Exception as e:
            print(f"\n❌ Hata: {e}")
            self.running = False

def main():
    """Ana fonksiyon"""
    # Komut satırı argümanlarından URL al (opsiyonel)
    hera_url = "http://localhost:8088"
    if len(sys.argv) > 1:
        hera_url = sys.argv[1]
    
    app = BarcodeScannerApp(hera_url)
    app.start_listening()

if __name__ == "__main__":
    main()
