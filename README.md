# Hera Barcode Scanner App

Barkod okuyucu ile okunan barkodları otomatik olarak heraPrinterApplication'a gönderip yazdıran basit uygulama.

## Kurulum

```bash
pip install -r requirements.txt
```

## EXE Oluşturma

PyInstaller ile exe oluşturmak için:

```bash
pip install pyinstaller
pyinstaller barcodeScannerApp.spec
```

Oluşturulan exe dosyası `dist/BarcodeScannerApp.exe` klasöründe olacaktır.

## Kullanım

### Python ile çalıştırma:
```bash
python main.py
```

### EXE ile çalıştırma:
```bash
dist/BarcodeScannerApp.exe
```

Veya farklı bir heraPrinterApplication URL'i kullanmak için:
```bash
dist/BarcodeScannerApp.exe http://192.168.1.100:8088
```

## Nasıl Çalışır?

1. Uygulama başlatıldığında klavye girişlerini dinlemeye başlar
2. Barkod okuyucu ile bir barkod okutulduğunda:
   - Okunan barkod seri numarası olarak kullanılır
   - heraPrinterApplication'ın `/api/barcodeScanner/print` endpoint'ine gönderilir
   - Etiket otomatik olarak yazdırılır
3. Çıkmak için `Ctrl+C` basın

## Notlar

- Barkod okuyucu klavye girişi olarak çalışmalıdır (HID device)
- Enter tuşu barkod okuma işlemini tamamlar
- Diğer alanlar (PRODUCT_CODE, MODEL_NUMBER, vs.) boş string olarak gönderilir
- Sadece SERIAL_NUMBER alanı okunan barkod ile doldurulur

