# Kamera Ön İzleme ve Kayıt Uygulaması

Bu Python masaüstü uygulaması, aynı anda 6 farklı kamerayı eşzamanlı olarak izlemeyi, karelerini almayı ve video kaydı yapmayı sağlar. OpenCV ve PyQt5 kütüphaneleri kullanılarak geliştirilmiştir.

## Özellikler

- **6 adede kadar RTSP kamera desteği**
- **Gerçek zamanlı ön izleme**
- **Video kaydı başlatma ve durdurma**
- **Her kamera için ayrı kayıt kuyruğu yönetimi**
- **Kameralar arasında geçiş yapma ve detaylı görüntüleme**

## Gereksinimler

Aşağıdaki bağımlılıkların sisteminizde yüklü olduğundan emin olun:

- Python 3.x
- OpenCV (`cv2`)
- PyQt5
- numpy 

Kurulum için aşağıdaki komutu çalıştırabilirsiniz:

```bash
pip install opencv-python PyQt5
```

## Kullanım

1. **Uygulamayı başlatın:**
   ```bash
   python main.py
   ```
2. **"Kamera Ekle" butonuna tıklayarak** RTSP kamera URL'sini girin.
3. Kameraların canlı görüntüsünü ana ekranda görebilirsiniz.
4. **"Video Kaydı Başlat"** butonuna basarak tüm kameralar için kayıt başlatabilirsiniz.
5. **"Video Kaydı Durdur"** butonu ile kaydı durdurabilirsiniz.
6. Kaydedilen videolar `kamera_kayitlarim` klasörüne `.avi` formatında kaydedilir.

## Proje Yapısı

```
📂 proje_konumu
 ├── main.py  # Uygulamanın ana dosyası
 ├── kamera_kayitlarim/  # Kaydedilen videoların saklandığı klasör
 ├── README.md  # Bu dosya
```

## Ekstra Bilgiler

- **Çoklu thread yönetimi**: Kameralar eşzamanlı çalıştırılır ve kayıt işlemi için ayrı iş parçacıkları (threads) kullanılır.
- **Görüntü boyutu**: Videolar 1280x720 çözünürlüğünde ve 30 FPS olarak kaydedilir.
- **Kuyruk yönetimi**: Her kamera için ayrı bir `deque` veri yapısı kullanılarak frame'ler yönetilir.

## Lisans

Bu proje açık kaynaklıdır ve herhangi bir ticari kullanım için serbesttir.

