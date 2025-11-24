import sys
import requests
import json
import time

try:
    import serial
    from serial import SerialException
except ImportError:
    print("pyserial kütüphanesi bulunamadı. Yüklemek için: pip install pyserial")
    sys.exit(1)


DEFAULT_SERIAL_SETTINGS = {
    "PortName": "COM7",
    "BaudRate": 9600,
    "Parity": "None",
    "DataBits": 8,
    "StopBits": "One",
    "IsAppDevelopmentMode": False,
}


class BarcodeScannerApp:
    def __init__(self, hera_printer_url="http://10.254.240.40:8088", serial_settings=None):
        self.hera_printer_url = hera_printer_url
        if serial_settings:
            self.serial_settings = serial_settings.copy()
        else:
            self.serial_settings = DEFAULT_SERIAL_SETTINGS.copy()

        self.running = False
        self.is_app_dev_mode = bool(self.serial_settings.get("IsAppDevelopmentMode"))

    def process_barcode(self, barcode_data):
        """Okunan barkodu işle ve yazdır"""
        print(f"\n📦 Barkod okundu: {barcode_data}")

        try:
            url = f"{self.hera_printer_url}/api/barcodeScanner/print"

            payload = {
                "SERIAL_NUMBER": barcode_data
            }

            headers = {"Content-Type": "application/json"}

            if self.is_app_dev_mode:
                print("🧪 IsAppDevelopmentMode aktif; yazdırma isteği gönderilmedi.")
                return

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

    def _open_serial_connection(self):
        """Seri portu verilen ayarlarla aç."""
        settings = self.serial_settings

        parity_map = {
            "None": serial.PARITY_NONE,
            "Odd": serial.PARITY_ODD,
            "Even": serial.PARITY_EVEN,
            "Mark": serial.PARITY_MARK,
            "Space": serial.PARITY_SPACE,
        }

        stop_bits_map = {
            "One": serial.STOPBITS_ONE,
            "OnePointFive": serial.STOPBITS_ONE_POINT_FIVE,
            "Two": serial.STOPBITS_TWO,
        }

        data_bits_map = {
            5: serial.FIVEBITS,
            6: serial.SIXBITS,
            7: serial.SEVENBITS,
            8: serial.EIGHTBITS,
        }

        try:
            return serial.Serial(
                port=settings["PortName"],
                baudrate=settings["BaudRate"],
                parity=parity_map.get(settings.get("Parity", "None"), serial.PARITY_NONE),
                bytesize=data_bits_map.get(settings.get("DataBits", 8), serial.EIGHTBITS),
                stopbits=stop_bits_map.get(settings.get("StopBits", "One"), serial.STOPBITS_ONE),
                timeout=1,
            )
        except KeyError as key_err:
            raise ValueError(f"Seri port ayarı eksik: {key_err}") from key_err

    def start_listening(self):
        """Seri porttan barkod okuyucuyu dinlemeye başla"""
        print("=" * 60)
        print("🔍 Barkod Okuyucu Uygulaması Başlatıldı")
        print("=" * 60)
        print(f"📡 heraPrinterApplication URL: {self.hera_printer_url}")
        print(f"🛠️  Seri Port: {self.serial_settings['PortName']} / {self.serial_settings['BaudRate']} baud")
        print(f"💡 Çıkmak için Ctrl+C basın")
        print("=" * 60)
        print()

        try:
            with self._open_serial_connection() as serial_conn:
                self.running = True
                print("🎧 Barkod okuyucu dinleniyor...")

                while self.running:
                    try:
                        raw_line = serial_conn.readline()
                    except SerialException as serial_err:
                        print(f"\n❌ Seri port okuma hatası: {serial_err}")
                        break

                    if not raw_line:
                        continue

                    try:
                        barcode_data = raw_line.decode("utf-8", errors="ignore").strip()
                    except UnicodeDecodeError:
                        print("⚠️  Barkod verisi UTF-8 değil, atlandı.")
                        continue

                    if barcode_data:
                        self.process_barcode(barcode_data)
                    else:
                        time.sleep(0.05)

        except SerialException as conn_err:
            print(f"\n❌ Seri porta bağlanılamadı: {conn_err}")
        except KeyboardInterrupt:
            print("\n\n🛑 Uygulama kapatılıyor...")
        except Exception as e:
            print(f"\n❌ Beklenmeyen hata: {e}")
        finally:
            self.running = False


def main():
    """Ana fonksiyon"""
    hera_url = "http://10.254.240.40:8088"
    if len(sys.argv) > 1:
        hera_url = sys.argv[1]

    app = BarcodeScannerApp(hera_url)
    app.start_listening()


if __name__ == "__main__":
    main()
