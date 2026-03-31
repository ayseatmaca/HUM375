from matplotlib.pyplot import plot
import matplotlib.pyplot as plt


list = [1,2,3,4,5,6,7,8,9,10]
def sum_of_list(lst):
    total = 0
    for num in lst:
        total += num
    return total
result = sum_of_list(list)
print(f"Listenin toplamı: {result}")


def change_list(lst):
    for i in range(len(lst)):
        lst[i] = lst[i] * -1
    return lst

changed_list = change_list(list)
print(f"Değiştirilmiş liste: {changed_list}")


def sırala(lst):
    return sorted(lst)
sorted_list = sırala(changed_list)
print(f"Sıralanmış liste: {sorted_list}")



def sırala_select(lst):
    for i in range(len(lst)):
        min_index = i
        for j in range(i+1, len(lst)):
            if lst[j] < lst[min_index]:
                min_index = j
        lst[i], lst[min_index] = lst[min_index], lst[i]
    return lst
sorted_list_selection = sırala_select(changed_list)
print(f"Seçmeli sıralanmış liste: {sorted_list_selection}")


def sırala_bubble(lst):
    n = len(lst)
    for i in range(n):
        for j in range(0, n-i-1):
            if lst[j] > lst[j+1]:
                lst[j], lst[j+1] = lst[j+1], lst[j]
    return lst     
sorted_list_bubble = sırala_bubble(changed_list)
print(f"Bubble sıralanmış liste: {sorted_list_bubble}")

def harf_buyuk_kucuk(lst):
    for i in range(len(lst)):
        if isinstance(lst[i], str):
            lst[i] = lst[i].upper() if lst[i].islower() else lst[i].lower()
    return lst
string_list = ['a', 'B', 'c', 'D']
changed_string_list = harf_buyuk_kucuk(string_list)
print(f"Değiştirilmiş string listesi: {changed_string_list}")

def harf_buyuk(lst):
    for i in range(len(lst)):
        if isinstance(lst[i], str):
            lst[i] = lst[i].upper()
    return lst
changed_string_list_upper = harf_buyuk(string_list)
print(f"Büyük harfli string listesi: {changed_string_list_upper}")

import matplotlib.pyplot as plt

def histogram(lst):
    hist = {}
    for item in lst:
        if item in hist:
            hist[item] += 1
        else:
            hist[item] = 1
    return hist

# Veri kümesi
string_list_with_duplicates = ['a', 'B', 'c', 'D', 'a', 'B']

# Fonksiyonu çağırma
histogram_result = histogram(string_list_with_duplicates)
print(f"Histogram: {histogram_result}")

# Görselleştirme
plt.bar(histogram_result.keys(), histogram_result.values())
plt.title('Harflerin Histogramı')
plt.xlabel('Harfler')
plt.ylabel('Frekans')
plt.show()

def yıldız_ciz(lst):
    for item in lst:
        print('*' * item)
print("Yıldız Çizimi:")
yıldız_ciz([1, 2, 3, 4, 5])

def kelımelerile_ciz(lst):
    for item in lst:
        print('kelimelerile' * item)
print("Kelimelerle Çizim:")
kelımelerile_ciz([1, 2, 3, 4, 5])

def samsun_ciz(lst):
    for item in lst:
        print('samsun' * item)
        
print("Samsun Çizimi:")
samsun_ciz([1, 2, 3, 4, 5])
def samsun_baklava_seklinde_ciz(lst):
    for i in range(len(lst)):
        print(' ' * (len(lst) - i - 1) + 'samsun' * (2 * i + 1))
print("Samsun Baklava Şeklinde Çizimi:")
samsun_baklava_seklinde_ciz([1, 2, 3, 4, 5])

def samsun_ters_baklava_seklinde_ciz(lst):
    for i in range(len(lst)-1, -1, -1):
        print(' ' * (len(lst) - i - 1) + 'samsun' * (2 * i + 1))        
print("Samsun Ters Baklava Şeklinde Çizimi:")
samsun_ters_baklava_seklinde_ciz([1, 2, 3, 4, 5])

def kare_samsun_ciz(lst):
    for i in range(len(lst)):
        print('samsun' * len(lst))
print("Kare Samsun Çizimi:")
kare_samsun_ciz([1, 2, 3, 4, 5])

def yarım_elmas_ciz(lst):
    for i in range(len(lst)):
        print(' ' * (len(lst) - i - 1) + 'samsun' * (i + 1))    
    for i in range(len(lst)-2, -1, -1):
        print(' ' * (len(lst) - i - 1) + 'samsun' * (i + 1))
print("Yarım Elmas Çizimi:")
yarım_elmas_ciz([1, 2, 3, 4, 5])


def samsun_üçlü_samsun_ciz(lst):
    for i in range(len(lst)):
        print('samsun' * (i + 1) + ' ' * (len(lst) - i - 1) + 'samsun' * (i + 1))
print("Samsun Üçlü Samsun Çizimi:")
samsun_üçlü_samsun_ciz([1, 2, 3, 4, 5])
