import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class Dish:
    def __init__(self, color, shape, price):
        # Bu sınıf, yemek özelliklerini (renk, şekil, fiyat) tutar.
        self.color = color
        self.shape = shape
        self.price = price

class RestaurantMenu:
    def __init__(self):
        # Menüdeki yemekleri ve yemeklerin özelliklerini tanımlar
        self.menu = {
            'Soups': {
                'Chicken Soup': Dish(color=(0, 0, 255), shape='star', price=12.0),
                'Tomato Soup': Dish(color=(0, 0, 255), shape='square', price=10.0),
                'Mushroom Soup': Dish(color=(0, 0, 255), shape='triangle', price=15.0),
            },
            'Main Courses': {
                'Pizza': Dish(color=(0, 255, 0), shape='star', price=20.0),
                'Kebab': Dish(color=(0, 255, 0), shape='square', price=18.0),
                'Chimichanga': Dish(color=(0, 255, 0), shape='triangle', price=22.0),
            },
            'Beverages': {
                'Coke': Dish(color=(255, 0, 0), shape='star', price=5.0),
                'Ayran': Dish(color=(255, 0, 0), shape='square', price=3.0),
                'Soda': Dish(color=(255, 0, 0), shape='triangle', price=4.0),
            },
            'Desserts': {
                'Pie': Dish(color=(255, 255, 0), shape='star', price=8.0),
                'Baklava': Dish(color=(255, 255, 0), shape='square', price=10.0),
                'Tiramisu': Dish(color=(255, 255, 0), shape='triangle', price=12.0),
            }
        }
        # Renk ve şekil tespiti yapılıp yapılmayacağını belirtir
        self.detect_color_and_shape = False
        # Tespit edilen yemekleri tutan liste. Çünkü en sonda yemeklerin toplam fiyatını yazacak. Bunu kaydeder.
        self.detected_dishes = []
        # Seçilen renk-şekil kombinasyonlarını takip eder.
        self.selected_combinations = {}

    # Tespit edilen yemekleri döndürür.
    def get_detected_dishes(self):
        return self.detected_dishes

    # Kamera görüntüsünü işleer.
    def process_frame(self, frame):
        # Eğer renk ve şekil tespiti yapılmayacaksa frame'i direkt olarak döndür
        if not self.detect_color_and_shape:
            return frame

        # Frame'i HSV formatına çevirir.
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Menüdeki her kategori ve yemek için renk ve şekil tespiti yapar.
        for category, dishes in self.menu.items():
            for dish_name, dish_info in dishes.items():
                color = dish_info.color
                shape = dish_info.shape

                # Renklerin HSV aralıklarını belirler.
                if color == (0, 0, 255):  # Kırmızı
                    lower_color = (0, 100, 100)
                    upper_color = (10, 255, 255)
                elif color == (0, 255, 0):  # Yeşil
                    lower_color = (40, 40, 40)
                    upper_color = (80, 255, 255)
                elif color == (255, 0, 0):  # Mavi
                    lower_color = (100, 100, 100)
                    upper_color = (130, 255, 255)
                elif color == (255, 255, 0):  # Sarı
                    lower_color = (20, 100, 100)
                    upper_color = (30, 255, 255)

                # Renk aralığına göre bir mask oluşturur.
                mask = cv2.inRange(hsv_frame, lower_color, upper_color)

                # Mask üzerinde konturları bulur.
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Kontur varsa ve şekil doğruysa eğer...
                if contours and self.detect_shape(contours[0], shape):
                    # Aynı renk-şekil kombinasyonunun zaten seçilip seçilmediğini kontrol eder.
                    key = f"{color}_{shape}"
                    if key in self.selected_combinations and self.selected_combinations[key] >= 1:
                        print(f"You can select only one object of the same color: {dish_name} ({category})")
                        continue

                    # Kareye konturları çizer
                    cv2.drawContours(frame, contours, -1, color, 2)
                    print(f"{dish_name} ({category}) has choosen! Price: {dish_info.price} TL")

                    # Seçilen kombinasyonları takip etmek için listeyi günceller
                    self.selected_combinations[key] = self.selected_combinations.get(key, 0) + 1

                    # Tespit edilen yemek bilgilerini listeye ekler.
                    detected_dish_info = {
                        'name': dish_name,
                        'category': category,
                        'price': dish_info.price
                    }
                    self.detected_dishes.append(detected_dish_info)

        return frame

    # Verilen konturun beklenen şekli tespit edip etmediğini kontrol eden metot.
    @staticmethod
    def detect_shape(contour, expected_shape):
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) == 3 and expected_shape == 'triangle': #Üçgeni algılar
            return True
        elif len(approx) == 4 and expected_shape == 'square': #Kareyi algılar
            return True
        elif len(approx) >= 8 and expected_shape == 'star': #Yıldızı algılar
            return True

        return False

    # Fotoğraf üzerinde işlem yapar
    def process_photo(self, photo_path):
        # Fotoğrafı okur
        frame = cv2.imread(photo_path)
        if frame is None:
            print("Error reading photo.")
            return

        # Frame'i işle
        processed_frame = self.process_frame(frame)

        # İşlenmiş frame'i yenibir pencere açarak gösterir.
        cv2.imshow('Captured Photo', processed_frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Tespit edilen yemeklerin toplam fiyatını hesaplayan metot
    def calculate_total_price(self):
        total_price = sum(dish_info['price'] for dish_info in self.detected_dishes)
        print(f"Total Price of Detected Dishes: {total_price} TL")

# Kameradan fotoğraf çekmeyi sağlayan metot
def capture_photo():
    global cap, menu_app

    # Kameradan anlık bir frame al
    ret, frame = cap.read()
    if not ret:
        print("Error capturing photo.")
        return

    # Kareyi jpg formatında  yaz
    cv2.imwrite("captured_photo.jpg", frame)
    
    # Renk ve şekil tespiti yapılacak şekilde aç
    menu_app.detect_color_and_shape = True
    # Fotoğrafı işler.
    menu_app.process_photo("captured_photo.jpg")
    # Renk ve şekil tespiti yapılacak şekilde kapat
    menu_app.detect_color_and_shape = False

    # Tespit edilen yemekleri alıyorç.
    detected_dishes = menu_app.get_detected_dishes()

    # En az bir çorba ve bir ana yemek seçildi mi diye kontrol etsin. Diğer türlü hata veriyor.
    selected_soup = any(dish_info['category'] == 'Soups' for dish_info in detected_dishes)
    selected_main_course = any(dish_info['category'] == 'Main Courses' for dish_info in detected_dishes)

    if not (selected_soup and selected_main_course):
        print("Please select at least one soup and one main course.") #Hata mesajı çıkıyor.
        return

    # Yalnızca bir kategori seçildiyse uyarı versin.
    categories = set(dish_info['category'] for dish_info in detected_dishes)
    if len(categories) == 1:
        print("Please select dishes from more than one category.")
        return

    # Tespit edilen yemekleri ve fiyatlarını ekrana yazdırır.
    print("Detected Dishes and Prices:")
    for dish_info in detected_dishes:
        print(f"{dish_info['name']} ({dish_info['category']}), Price: {dish_info['price']} TL.")
        
    print("To confirm your order, press the confirm button.") #Tesipt edilen yemek ve fiyatlardan sonra onay ister.

# Kamera görüntüsünü sürekli güncelleyen metot
def update_frame():
    ret, frame = cap.read()
    if ret:
        # Frame'İ işler ve gösterir
        processed_frame = menu_app.process_frame(frame)
        display_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        display_image = ImageTk.PhotoImage(Image.fromarray(display_frame))

        label.config(image=display_image)
        label.image = display_image

    root.after(10, update_frame)  # 10 milisaniye sonra kendini tekrar çağırıyor

# Main fonksiyon
def main():
    global cap, menu_app, root, label

    # Kamera bağlantısını açıyor.
    cap = cv2.VideoCapture(0)
    menu_app = RestaurantMenu()

    # Tkinter penceresini oluştur.
    root = tk.Tk()
    root.title("210444029 Mehmet Efe Kapısız - Restaurant Menu App")

    # Fotoğraf çekme butonu. Butona tıklayınca anlık frame'i alır.
    btn_capture = ttk.Button(root, text="Capture Photo", command=capture_photo)
    btn_capture.pack(pady=10)

    # Toplam fiyat hesaplama butonunu. Tüm siparişleri aldıktan sonra, sipraişleri onaylar.
    btn_calculate_total = ttk.Button(root, text="Confirm Order", command=menu_app.calculate_total_price)
    btn_calculate_total.pack(pady=10)

    # Görüntüyü gösterir
    label = ttk.Label(root)
    label.pack(pady=10)

    root.after(10, update_frame)  # Periyodik olarak güncellemeyi başlat

    root.mainloop()  # Tkinter döngüsünü başlatıyor

    # Kamera bağlantısını kapat
    cap.release()
    cv2.destroyAllWindows()

# Ana fonksiyonun çağrılması için gerekli
if __name__ == "__main__":
    main()
