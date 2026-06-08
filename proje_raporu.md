# Python ve PyQt5 Kullanılarak Geliştirilen Zihin Haritası (Mind Map) Uygulaması Proje Raporu

<div style="text-align: center; margin-top: 50px;">
    <h2>T.C.</h2>
    <h2>MÜHENDİSLİK FAKÜLTESİ</h2>
    <h3>BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ</h3>
    <br><br><br><br>
    <h1>PYTHON PROGRAMLAMA DERSİ</h1>
    <h2>DÖNEM SONU PROJE RAPORU</h2>
    <br><br>
    <h3>Proje Başlığı:</h3>
    <h2>Python ve PyQt5 Kullanılarak Geliştirilen Zihin Haritası (Mind Map) Uygulaması</h2>
    <br><br><br><br>
    <table style="margin: 0 auto; text-align: left; font-size: 12pt;">
        <tr>
            <td><b>Hazırlayan:</b></td>
            <td>Ayşe Atmaca</td>
        </tr>
        <tr>
            <td><b>Öğrenci No:</b></td>
            <td>[Öğrenci Numarası]</td>
        </tr>
        <tr>
            <td><b>Ders Sorumlusu:</b></td>
            <td>[Öğretim Üyesi Unvanı ve Adı]</td>
        </tr>
    </table>
    <br><br><br><br>
    <p><b>Tarih:</b> Haziran 2026</p>
</div>

<div style="page-break-after: always;"></div>

---

## İÇİNDEKİLER

1. Özet
2. Giriş
   * 2.1. Zihin Haritası Kavramı
   * 2.2. Zihin Haritalarının Kullanım Alanları
   * 2.3. Projenin Amacı ve Önemi
3. Gereksinim Analizi
   * 3.1. Fonksiyonel Gereksinimler
   * 3.2. Tasarım ve Arayüz Kısıtları
4. Kullanılan Teknolojiler
   * 4.1. Python Programlama Dili
   * 4.2. PyQt5 GUI Kütüphanesi
   * 4.3. QGraphicsView ve QGraphicsScene Mimarisi
   * 4.4. Veri Saklama Standardı (JSON)
5. Sistem Tasarımı ve Modüller
   * 5.1. Sistem Mimarisi
   * 5.2. Modüllerin Tanımı ve Görevleri
6. Veri Yapısı Tasarımı
   * 6.1. Ağaç (Tree) Veri Yapısı
   * 6.2. Düğüm (Node) Veri Modeli
   * 6.3. Ağaç Yapısının Tercih Edilme Nedenleri
7. Uygulama Özellikleri ve Yetenekleri
   * 7.1. Etkileşimli Grafikler ve Sürükle-Bırak (Drag-and-Drop)
   * 7.2. Dinamik Düğüm Yönetimi ve Bağlantı Çizgileri
   * 7.3. Dosya Yönetimi (JSON Kaydetme/Yükleme)
   * 7.4. Gelişmiş Özelleştirme ve Arayüz Seçenekleri
8. Kullanıcı Arayüzü (UI) Tasarımı
9. Programın Çalışma Mantığı ve Kullanım Senaryosu
10. Karşılaşılan Problemler ve Çözüm Yaklaşımları
11. Sonuç ve Değerlendirme
12. Kaynakça

<div style="page-break-after: always;"></div>

---

## 1. ÖZET

Bu proje kapsamında, kullanıcıların fikirlerini görselleştirmelerine, organize etmelerine ve yapılandırmalarına olanak tanıyan etkileşimli, masaüstü tabanlı bir Zihin Haritası (Mind Map) uygulaması geliştirilmiştir. Uygulamanın geliştirilmesinde nesne yönelimli programlama ilkelerine uygun olarak Python programlama dili ve Qt kütüphanesinin Python bağlaması olan PyQt5 tercih edilmiştir. Geliştirilen yazılım, hiyerarşik bir ağaç yapısını temel alarak, bir merkez düğüm etrafında sınırsız sayıda alt düğüm oluşturulmasına imkan vermektedir.

Kullanıcı etkileşimini en üst düzeye çıkarmak amacıyla grafik arayüzünde sürükle-bırak yöntemiyle düğüm taşıma, çift tıklama ile düğüm metni düzenleme ve zengin içerikli sağ tık bağlam menüleri entegre edilmiştir. Ayrıca projenin profesyonel standartlara ulaşması adına dinamik Bezier bağlantı çizgileri, düğüm şekillerinin (yuvarlatılmış dikdörtgen, elips, kapsül) değiştirilebilmesi, simge (ikon) atamaları, özel renk tanımlamaları, otomatik hizalama (Auto Arrange) algoritması, detaylı özellikler paneli (Properties Panel), istatistik penceresi ve açık/koyu tema (Light/Dark Theme) desteği sisteme dahil edilmiştir. Uygulama verilerinin kalıcılığı JSON formatındaki dosyalar aracılığıyla sağlanmış, hazırlanan haritaların yüksek kalitede PNG formatında dışa aktarılmasına olanak tanınmıştır. Proje raporu, uygulamanın tasarım aşamalarını, veri modellerini, teknik mimarisini ve karşılaşılan mühendislik problemlerine getirilen çözümleri detaylı bir şekilde ele almaktadır.

---

## 2. GİRİŞ

### 2.1. Zihin Haritası Kavramı
Zihin haritası (Mind Map), ilk olarak 1960'ların sonunda yazar ve eğitimci Tony Buzan tarafından popüler hale getirilen, bilgiyi görselleştirmeye ve hiyerarşik ilişkileri şematik olarak göstermeye yarayan grafiksel bir teknikdir. İnsan beyninin doğrusal olmayan, çağrışımsal düşünme biçimini taklit eden zihin haritaları, bilgiyi merkezi bir fikir etrafında radyal bir düzende yapılandırır. Geleneksel düz metin not alma yöntemlerinin aksine, renkler, şekiller, kelimeler ve semboller kullanarak beynin hem sol hem de sağ lobunu eşzamanlı olarak uyarır ve öğrenmeyi, yaratıcılığı ve hatırlama oranını artırır.

### 2.2. Zihin Haritalarının Kullanım Alanları
Zihin haritaları günümüzde eğitimden iş dünyasına, proje yönetiminden kişisel gelişime kadar oldukça geniş bir alanda kullanılmaktadır:
* **Eğitim ve Öğrenim:** Öğrencilerin karmaşık ders konularını özetlemesi, anahtar kavramları birbiriyle ilişkilendirmesi ve sınavlara hazırlanmasında etkilidir.
* **Fikir Fırtınası (Brainstorming):** Proje ekiplerinin bir araya gelerek yeni fikirler üretmesi, bu fikirleri hızlıca kategorize etmesi ve ana fikir etrafında yapılandırmasında kullanılır.
* **Proje Planlama:** Bir projenin alt görevlerini, sorumlularını, sürelerini ve hiyerarşik iş kırılım yapılarını (WBS) görselleştirmek için ideal bir araçtır.
* **Not Alma ve Sunum:** Uzun toplantıların, konferansların veya kitapların ana hatlarını çıkararak hızlı erişilebilir özetler oluşturmaya imkan tanır.

### 2.3. Projenin Amacı ve Önemi
Bu projenin temel amacı; modern masaüstü uygulama standartlarına uygun, yüksek performanslı, kullanıcı dostu ve genişletilebilir bir zihin haritası yazılımını Python ve PyQt5 teknolojilerini kullanarak sıfırdan geliştirmektir. Yazılımın kararlı bir yapıda çalışması, büyük şemalarda dahi akıcı bir kullanıcı deneyimi sunması hedeflenmiştir. Öğrencinin GUI (Grafiksel Kullanıcı Arayüzü) tasarımı, grafik sahnesi yönetimi, olay tabanlı programlama, veri serileştirme ve ağaç veri yapısı yönetimi konularında yetkinlik kazanması açısından bu proje büyük bir öneme sahiptir.

<div style="page-break-after: always;"></div>

---

## 3. GEREKSİNİM ANALİZİ

### 3.1. Fonksiyonel Gereksinimler
Yazılımın kabul kriterlerini belirleyen ve hocanın yönlendirmeleri doğrultusunda kesin olarak sağlanan fonksiyonel gereksinimler şunlardır:
1. **Merkez Düğüm (Root Node):** Uygulama açıldığında sahnede otomatik olarak bir "Merkez Düğüm" yer almalıdır. Bu düğüm silinemez olmalı ve hiyerarşinin en tepesinde bulunmalıdır.
2. **Alt Düğüm Ekleme:** Sahnedeki herhangi bir düğüm seçilerek sağ tık bağlam menüsü veya araç çubuğu üzerinden yeni bir alt düğüm oluşturulabilmelidir.
3. **Sınırsız Dallanma:** Sistem, teorik olarak sonsuz derinlikte dallanmayı (level depth) desteklemelidir. Her düğüm kendi alt düğümlerine sahip olabilmelidir.
4. **Görsel Bağlantılar:** Ebeveyn düğümler ile çocuk düğümler arasında ilişkileri gösteren bağlantı çizgileri (edge) bulunmalıdır. Bu çizgiler düğümler taşındıkça dinamik olarak güncellenmelidir.
5. **Sürükle-Bırak ile Taşıma:** Kullanıcılar fare yardımıyla düğümleri çalışma alanında serbestçe sürükleyip bırakarak taşıyabilmelidir.
6. **Çift Tıklama ile Yeniden Adlandırma:** Düğümler üzerine fare ile çift tıklandığında metin kutusu aktif hale gelmeli ve düğüm adı düzenlenebilmelidir.
7. **Sağ Tık Bağlam Menüsü:** Düğümler üzerinde sağ tıklandığında "Dal Ekle", "Dal Sil" (Merkez düğüm hariç) ve "Yeniden Adlandır" seçeneklerini içeren modern bir menü açılmalıdır.
8. **Beyaz Arka Plan:** Çalışma alanının arka plan rengi temiz, gözü yormayan beyaz tonlarında olmalıdır.
9. **Kullanılabilirlik:** Uygulamanın arayüzü basit, anlaşılır fakat tüm işlevleri kusursuz bir şekilde yerine getirebilecek kararlılıkta olmalıdır.

### 3.2. Tasarım ve Arayüz Kısıtları
Akademik ve profesyonel standartlara uyum sağlayabilmesi açısından arayüz tasarımı, modern fontlar (Inter, Segoe UI), tutarlı renk paletleri ve işlevsel panellerle donatılmıştır. Kullanıcının düğüm koordinatlarını, kimlik bilgisini ve ilişkilerini takip edebileceği bir özellikler paneli yer almalı, haritanın genel yapısı hakkında analiz sunan istatistik ekranı bulunmalıdır.

---

## 4. KULLANILAN TEKNOLOJİLER

### 4.1. Python Programlama Dili
Projenin geliştirilmesinde ana programlama dili olarak Python 3 tercih edilmiştir. Python; hızlı prototipleme imkanı sunması, zengin kütüphane desteği, temiz sözdizimi ve platform bağımsız çalışabilme yeteneği ile günümüz yazılım dünyasında popüler bir yere sahiptir. Özellikle nesne yönelimli programlama (OOP) prensiplerini tam olarak desteklemesi, düğüm ve bağlantı çizgisi gibi nesnelerin modüler olarak tasarlanmasına olanak tanımıştır.

### 4.2. PyQt5 GUI Kütüphanesi
PyQt5, C++ ile geliştirilmiş endüstriyel standarttaki Qt5 framework'ünün Python bağlamasıdır. PyQt5'in seçilme nedenleri şunlardır:
* **Yüksek Performans:** Grafiksel arayüz elemanlarını yerel işletim sistemi kaynaklarını kullanarak son derece hızlı bir şekilde çizer.
* **Sinyal-Slot (Signal-Slot) Mekanizması:** PyQt5'in kendine has bu yapısı, bileşenler arası asenkron olay iletişimini son derece güvenli ve temiz bir kod mimarisi ile çözmeyi sağlar.
* **Geniş Bileşen Desteği:** Araç çubukları, menüler, özellik panelleri ve özel çizim alanları için hazır ve özelleştirilebilir sınıflar sunar.

### 4.3. QGraphicsView ve QGraphicsScene Mimarisi
Zihin haritası gibi etkileşimli ve 2D grafik tabanlı uygulamalar için PyQt5 içerisinde yer alan `QGraphicsView` mimarisi kullanılmıştır. Bu mimari üç ana bileşenden oluşur:
* **QGraphicsScene (Sahne):** Grafik nesnelerinin (düğümler, çizgiler) yerleştirildiği, mantıksal koordinatların yönetildiği ve nesne çarpışma testlerinin yapıldığı container yapıdır.
* **QGraphicsView (Görünüm):** Sahnenin belirli bir kısmını ekranda gösteren penceredir. Ölçekleme (yakınlaşma/uzaklaşma) ve kaydırma (pan) işlemlerini üstlenir.
* **QGraphicsItem (Grafik Öğesi):** Sahnede çizilen ve fare olaylarına tepki veren bireysel nesnelerdir. Bu projede `Node` sınıfı `QGraphicsObject` (QGraphicsItem türevi), `Edge` sınıfı ise `QGraphicsPathItem` sınıfından türetilmiştir.

### 4.4. Veri Saklama Standardı (JSON)
Oluşturulan zihin haritaların kaydedilmesi ve daha sonra tekrar yüklenebilmesi amacıyla hafif, okunması kolay ve platformlar arası standart olan JSON (JavaScript Object Notation) veri formatı tercih edilmiştir. Python'un dahili `json` kütüphanesiyle nesne öznitelikleri doğrudan sözlük (dictionary) yapılarına dönüştürülerek dosyaya yazılabilmektedir.

<div style="page-break-after: always;"></div>

---

## 5. SİSTEM TASARIMI VE SÜREÇLERİ

### 5.1. Sistem Mimarisi
Uygulama, sorumlulukların ayrılması (Separation of Concerns) prensibine uygun olarak modüler bir mimaride tasarlanmıştır. Model-View-Controller (MVC) mimari desenine benzer şekilde, verinin saklanması, görselleştirilmesi ve kullanıcı etkileşimlerinin yönetilmesi farklı sınıflar tarafından yürütülür.

Mantıksal olarak, `MainWindow` (main.py) kullanıcı ekranını, pencereleri, üst menüyü ve sağdaki Properties panelini koordine eder. `MindMapView` ve `MindMapScene` (scene.py) tuvali yönetir ve düğüm ile çizgileri üzerinde taşır. `Node` (node.py) görsel kutuları, şekil, ikon ve renkleri yönetirken, `Edge` (edge.py) bu kutular arasındaki dinamik çizgileri çizer. Son olarak `storage.py` bu çizim yapısını dosya olarak saklar.

### 5.2. Modüllerin Tanımı ve Görevleri
* **`main.py` (Ana Yönetici):** Uygulamamanın giriş noktasıdır. `MainWindow` sınıfını barındırır. Menü çubuğu, araç çubuğu, özellikler paneli, durum çubuğu ve tema yönetimini oluşturur. Sahne bileşeninden gelen sinyalleri yakalayarak kullanıcıyı bilgilendirir ve arayüzü günceller.
* **`node.py` (Düğüm Nesnesi):** Zihin haritasındaki her bir konuyu temsil eden `Node` grafik nesnesini tanımlar. Düğümün şeklini (dikdörtgen, elips, kapsül), rengini, ikonunu, gölgesini ve metnini çizer. Çift tıklama, sağ tıklama ve sürükleme olaylarını yönetir.
* **`edge.py` (Bağlantı Nesnesi):** Ebeveyn ve çocuk düğümler arasındaki ilişkiyi gösteren `Edge` sınıfını barındırır. İki düğümün sınır koordinatlarını hesaplayarak aralarında dinamik, pürüzsüz bir Bezier eğrisi çizer.
* **`scene.py` (Sahne ve Görünüm):** `MindMapScene` ve `MindMapView` sınıflarını içerir. Sahneye düğüm eklenmesi, düğümlerin silinmesi, radyal yerleşim koordinatlarının hesaplanması ve otomatik hizalama algoritmasının çalıştırılmasından sorumludur. Görünüm sınıfı ise yakınlaştırma (Zoom) ve sahne üzerinde kaydırma (Pan) olaylarını yakalar.
* **`storage.py` (Dosya Sistemi):** Sahnedeki düğümleri hiyerarşik ilişkileriyle birlikte analiz ederek JSON formatında kaydeder. Kayıtlı dosyaları okuyarak bellek üzerinde nesneleri yeniden oluşturur ve sahneye yerleştirir.

<div style="page-break-after: always;"></div>

---

## 6. VERİ YAPISI TASARIMI

### 6.1. Ağaç (Tree) Veri Yapısı
Zihin haritası uygulaması, doğası gereği hiyerarşik bir veri modeline dayanır. Bu doğrultuda yazılımın temelinde doğrusal olmayan veri yapılarından biri olan **Ağaç (Tree)** yapısı kullanılmıştır. Ağaç yapısı, tek bir kök düğümden (root) başlayarak alt dallara ayrılan ve döngü içermeyen (acyclic) bir graf türüdür.

Her dalın yalnızca tek bir ebeveyni olabileceği bu yapıda, hiyerarşik ilişkiler kesintisiz olarak devam eder. Kök düğüm sahnede tekildir ve diğer tüm düğümler doğrudan veya dolaylı yollarla bu kök düğüme bağlıdır.

### 6.2. Düğüm (Node) Veri Modeli
Sahnede oluşturulan her bir düğüm nesnesi, bellekte ve JSON dosyasında aşağıdaki öznitelikleri saklamaktadır:
* **`id` (String):** UUID standartlarında üretilen, her düğüme özel benzersiz kimlik anahtarıdır. İlişkilerin kurulmasında referans alınır.
* **`text` (String):** Düğümün üzerinde yazan metinsel bilgiyi saklar.
* **`parent` (Node/String):** Düğümün bağlı olduğu ebeveyn düğümün referansını veya kimlik numarasını tutar. Kök düğüm için bu değer `None`'dır.
* **`children` (List):** Düğümün doğrudan bağlı olan alt çocuk düğümlerinin listesini saklar.
* **`x` ve `y` (Float):** Düğümün sahne üzerindeki mantıksal 2D koordinatlarıdır.
* **`shape_type` (String):** Düğümün çizileceği şekli (yuvarlatılmış dikdörtgen, elips, kapsül) belirler.
* **`custom_color` (String):** Düğüme atanan özel renk değerini (Hex kodu) saklar.
* **`icon_type` (String):** Düğüm içerisinde gösterilecek opsiyonel simge türünü belirtir.

### 6.3. Ağaç Yapısının Tercih Edilme Nedenleri
Ağaç veri yapısının bu projede kullanılmasının teorik ve pratik gerekçeleri şu şekildedir:
* **Hiyerarşik Uyum:** Zihin haritasındaki her alt başlığın yalnızca bir ebeveyne sahip olması gerekliliği, ağaç yapısının tek-ebeveyn (single-parent) kuralıyla mükemmel bir şekilde eşleşir.
* **Döngü Önleme:** Ağaç yapısı döngülere (cycle) izin vermediği için, bir alt düğümün yanlışlıkla kendi üst ebeveynine bağlanarak sonsuz döngü oluşturması engellenmiş olur.
* **Hızlı Erişim ve Arama:** Düğümler üzerinden derinlemesine arama (DFS - Depth First Search) yapılarak bir alt dalın tüm alt kırılımlarına saniyeler içerisinde erişilebilir. Bu sayede bir dal silindiğinde o dala bağlı tüm alt dalların temizlenmesi işlemi kolayca gerçekleştirilir.

<div style="page-break-after: always;"></div>

---

## 7. UYGULAMA ÖZELLİKLERİ VE YETENEKLERİ

### 7.1. Etkileşimli Grafikler ve Sürükle-Bırak (Drag-and-Drop)
Uygulama, kullanıcının çalışma alanı ile doğrudan etkileşime girmesini sağlar. Herhangi bir düğüm sol tıklama ile seçilip sahne üzerinde serbestçe sürüklenebilir. Sürükleme işlemi sırasında PyQt5'in `ItemPositionHasChanged` olayı tetiklenerek düğüme bağlı tüm bağlantı çizgileri gerçek zamanlı olarak yeniden çizilir. Kullanıcı sahne boşluğuna tıklayıp fareyi sürüklediğinde ise tüm çalışma alanını kaydırabilir (Pan özelliği). Fare tekerleği yardımıyla sahneye yakınlaşma ve uzaklaşma (Zoom) işlemleri akıcı bir şekilde gerçekleştirilir.

### 7.2. Dinamik Düğüm Yönetimi ve Bağlantı Çizgileri
Kullanıcı bir düğüm seçip sağ tıkladığında açılan menüden yeni bir alt düğüm (dal) oluşturabilir. Düğümün yerleşimi, karmaşayı önlemek amacıyla ebeveyn düğümün konumuna göre **Radyal Yerleşim Algoritması** ile hesaplanır. Kök düğümün çocukları dairesel bir açıyla ($360^\circ$) dağıtılırken, alt seviyedeki düğümlerin çocukları ebeveynlerinin kökten olan açısına göre dışa doğru yönlendirilir. İki düğüm arasındaki bağlantılar doğrusal çizgiler yerine, profesyonel haritalama yazılımlarında kullanılan pürüzsüz **Cubic Bezier Eğrileri** ile çizilir. Ebeveyn ve çocuk düğümlerin karşılıklı kenar sınırları hesaplanarak çizgilerin düğüm sınırlarından başlaması sağlanır.

### 7.3. Dosya Yönetimi (JSON Kaydetme/Yükleme)
Uygulamada hazırlanan çalışmalar `File -> Save` menüsü aracılığıyla JSON formatında diske kaydedilebilir. Kayıt işlemi sırasında bellek üzerindeki ağaç yapısı serileştirilerek hiyerarşik bağları kaybetmeyecek şekilde düz bir düğüm listesine dönüştürülür. `File -> Open` menüsü ile bu JSON dosyaları okunarak hiyerarşi (ID eşleşmeleri üzerinden) bellek üzerinde yeniden inşa edilir. Böylece platform bağımsız dosya paylaşımı ve sürdürülebilir çalışma ortamı sağlanmış olur. Ayrıca `File -> Export as PNG` özelliği ile çalışma alanındaki tüm düğümleri kapsayacak sınırlar (bounding rect) otomatik tespit edilerek, arka plan rengiyle birlikte yüksek çözünürlüklü bir görsel dosya olarak dışa aktarım sağlanır.

### 7.4. Gelişmiş Özelleştirme ve Arayüz Seçenekleri
* **Düğüm Şekilleri:** Kullanıcılar sağ tık menüsünden her düğümün şeklini değiştirebilir. Yuvarlatılmış dikdörtgen, elips ve kapsül şekilleri desteklenir. Şekil değiştiğinde metnin dışarı taşmaması için iç dolgu payları (padding) dinamik olarak güncellenir.
* **Görsel İkonlar:** Düğümlere anlam katmak amacıyla iç kısımlarına yerleştirilmek üzere "Fikir 💡", "Klasör 📁", "Görev ☑️", "Not 📝" ve "Yıldız ⭐" simgeleri eklenebilir.
* **Renk Özelleştirme:** Her düğümün arka plan rengi renk paletinden seçilebilir. Uygulama, seçilen rengin parlaklığını (luminance) ölçerek üzerindeki metin rengini otomatik olarak beyaza veya siyaha ayarlar.
* **Açık ve Koyu Tema:** Tek bir tıklama ile tüm uygulama ve grafik sahnesi açık veya koyu temaya geçirilebilir. Koyu temada arka plan koyu lacivert tonlarına bürünürken, menüler, araç çubukları ve düğüm varsayılan renkleri yüksek kontrastlı alternatifleriyle güncellenir.

<div style="page-break-after: always;"></div>

---

## 8. KULLANICI ARAYÜZÜ (UI) TASARIMI

Uygulamanın kullanıcı arayüzü modern, temiz ve sezgisel bir yerleşim düzenine sahiptir. Arayüzün bileşenleri ve düzeni ana pencere üzerinde bütünleşik bir biçimde sunulmaktadır.

* **Ana Ekran (Çalışma Alanı - Şekil 5):** Arayüzün merkezinde, `QGraphicsView` bileşeni kullanılarak oluşturulan zihin haritası tuvali yer alır. Arka plan rengi hocanın belirttiği üzere temiz beyaz tonlarındadır. Koyu tema seçildiğinde ise otomatik olarak koyu slate tonlarına bürünür.
* **Üst Araç Çubuğu (Toolbar - Şekil 6):** Sıklıkla kullanılan dosya işlemleri (Yeni, Aç, Kaydet, PNG Aktar) ve düğüm düzenleme butonları (Düğüm Ekle, Yeniden Adlandır, Sil, Otomatik Hizala) bu kısımda yer alır. Butonlar üzerine gelindiğinde durum çubuğunda açıklayıcı ipuçları (Tooltips) gösterilir.
* **Özellikler Paneli (Properties Panel - Şekil 7):** Ekranın sağ tarafına yerleştirilmiş bu panel, sahnede seçilen düğümün detaylı bilgilerini yansıtır. Düğüm adı, benzersiz kimliği (ID), bağlı olduğu ebeveynin adı, derinlik seviyesi (Level) ve sahip olduğu alt düğüm sayısı bu panelden anlık olarak izlenebilir. Ayrıca kullanıcının doğrudan bu panel üzerindeki sayı kutularını (SpinBox) kullanarak düğümü piksel hassasiyetinde taşımasına veya renk butonunu kullanarak rengini değiştirmesine imkan tanır.
* **Durum Çubuğu (Status Bar):** Ekranın en altında yer alır ve kullanıcıya sistemi nasıl kullanacağına dair rehber ipuçları gösterir. Bir işlem yapıldığında (örneğin "Düğüm başarıyla eklendi") kullanıcıya geri bildirim mesajları sunar.

*Şekil 5: Zihin Haritası Çalışma Alanı ve Genel Görünüm*  
*Şekil 6: Üst Araç Çubuğu ve Erişim Düğmeleri*  
*Şekil 7: Özellikler Paneli ve Değer Değiştirme Alanları*  

<div style="page-break-after: always;"></div>

---

## 9. PROGRAMIN ÇAŞILMA MANTIĞI VE KULLANIM SENARYOSU

Kullanıcının sıfırdan başlayarak profesyonel bir zihin haritası oluşturma, biçimlendirme ve kaydetme süreci adım adım aşağıda açıklanmıştır:

1. **Uygulamanın Başlatılması:** Program çalıştırıldığında, bellek üzerinde boş bir `MindMapScene` nesnesi kurulur ve sahnenin tam merkezinde (0,0) konumunda "Central Idea" isimli ebeveyni olmayan bir kök düğüm otomatik olarak çizilir. Properties paneli boş durumdadır.
2. **Merkez Konunun Belirlenmesi:** Kullanıcı merkez düğümün üzerine çift tıklar veya düğümü seçip F2 tuşuna basar. Düğüm üzerindeki metin alanı düzenleme moduna geçer. Kullanıcı "Python Eğitimi" yazarak Enter tuşuna basar. Düğümün boyutu yazılan yeni metnin genişliğine göre kendiliğinden genişler.
3. **Ana Dallar oluşturma:** Kullanıcı merkez düğüme sağ tıklar ve "Add Child Node" seçeneğini seçer. Sahne yöneticisi otomatik olarak radyal açıyı hesaplar, merkez düğümün sağına doğru yeni bir çocuk düğüm yerleştirir ve odağı bu düğüme alarak düzenleme modunu açar. Kullanıcı buraya "PyQt5 Arayüzü" yazar. Aynı işlem tekrarlanarak sol tarafa "Temel Konular" dalı eklenir.
4. **Alt Dallarla Derinleştirme:** Kullanıcı "PyQt5 Arayüzü" düğümünü seçip yeni bir çocuk eklediğinde, uygulama bu düğümün merkez düğümden olan açısını hesaplar ve aynı doğrultuda dışarıya doğru yeni bir düğüm açar. Kullanıcı bu düğüme "QGraphicsView" ismini verir.
5. **Görsel Özelleştirme:** Kullanıcı "Python Eğitimi" düğümünü daha belirgin kılmak için sağ tıklar, "Node Shape" menüsünden "Capsule" seçeneğini işaretler. Ardından "Node Color -> Change Node Color" seçeneğinden kırmızı rengi seçer. Kırmızı rengin parlaklık derecesi düşük olduğundan metin rengi beyaz olarak kalır. "PyQt5 Arayüzü" düğümüne ise sağ tıklayıp "Set Icon" menüsünden "Idea" simgesini (ampul simgesi 💡) yerleştirir.
6. **Düzenleme ve Hizalama:** Kullanıcı düğümleri sürükleyerek kendi göz zevkine göre konumlandırır. Eğer düğümler çok dağılırsa, araç çubuğundaki "Auto Arrange" butonuna tıklar. Sistem milisaniyeler içerisinde ağaç yapısını analiz eder ve tüm düğümleri hiçbir şekilde üst üste binmeyecek (overlap) biçimde radyal ağaç şablonuna göre otomatik olarak yeniden dizer.
7. **Projenin Kaydedilmesi:** Harita tamamlandığında `Ctrl+S` kısayolu ile dosya kaydetme penceresi açılır. Kullanıcı dosyayı "python_dersi.json" olarak kaydeder. Sistem tüm ağaç verisini JSON formatına dönüştürerek diske yazar.

<div style="page-break-after: always;"></div>

---

## 10. KARŞILAŞILAN PROBLEMLER VE ÇÖZÜM YAKLAŞIMLARI

### 10.1. Düğümler Arası Bağlantıların Dinamik Güncellenmesi
* **Problem:** Düğümler çalışma alanında sürüklendiğinde veya otomatik hizalandığında, aralarındaki bağlantı çizgilerinin kopması veya eski koordinatlarda kalması sorunu yaşanmıştır.
* **Çözüm:** `Node` sınıfı içinde `ItemSendsGeometryChanges` özelliği aktif edilmiştir. Düğümün konumu değiştiğinde tetiklenen `itemChange()` metodu aşırı yüklenerek (override), düğüme bağlı olan tüm `Edge` nesnelerinin referansları taranmış ve her bir bağlantı çizgisinin `update_position()` fonksiyonu çağrılmıştır. Böylece sürükleme esnasında çizgiler düğümleri pürüzsüzce takip etmiştir.

### 10.2. Alt Dalların Ebeveynle Birlikte Taşınması
* **Problem:** Bir alt ebeveyn düğüm sürüklendiğinde, ona bağlı olan onlarca çocuk düğümün sabit kalması, dalların birbirinden kopmasına ve haritanın görsel yapısının bozulmasına neden olmuştur.
* **Çözüm:** Sahnede hiyerarşik grup yapısı kurmak yerine, sürükleme olayı tamamlandığında veya koordinat değişimi algılandığında çalışan rekürsif bir taşıma fonksiyonu geliştirilmiştir. Bir düğümün konumu güncellendiğinde, aradaki fark vektörü (Delta X, Delta Y) hesaplanmakta ve bu fark düğümün tüm alt soyundan gelen (descendants) çocuk düğümlerin koordinatlarına rekürsif olarak eklenmektedir.

### 10.3. Grafik Sahnesi Sınırları ve Kırpılma Sorunları
* **Problem:** Düğümlerin etrafına eklenen modern gölge efektleri (QGraphicsDropShadowEffect) ve kalın kenarlıklar, `QGraphicsItem` nesnesinin varsayılan sınır çizgilerinin (boundingRect) dışına taşarak ekranda çizim kalıntısı (artifact) ve kırpılma hataları oluşturmuştur.
* **Çözüm:** `Node` sınıfının `boundingRect()` fonksiyonu güncellenerek, çizim alanının sınırları her yönden 6 piksel oranında genişletilmiştir (`rect.adjusted(-6, -6, 6, 6)`). Bu sayede gölgeler ve dış çizgiler sahne tarafından hiçbir kırpılmaya maruz kalmadan pürüzsüzce işlenmiştir.

### 10.4. Hiyerarşik Yapının JSON Formatında Saklanması
* **Problem:** Python bellek referanslarına sahip olan ağaç yapısının doğrudan JSON formatına dönüştürülememesi (circular reference hatası) ve dosya yüklenirken nesne ilişkilerinin kaybolması.
* **Çözüm:** Serileştirme işlemi için benzersiz kimlik (UUID) mimarisine geçilmiştir. Kaydetme sırasında her düğüm kendi ebeveyninin ID bilgisini saklar. Yükleme sırasında ise öncelikle tüm düğüm nesneleri koordinat ve metinleriyle düz bir sözlük olarak belleğe alınır, ikinci adımda ise ID eşleşmeleri üzerinden parent-child ilişkileri yeniden kurularak ağaç yapısı hatasız bir şekilde canlandırılır.

<div style="page-break-after: always;"></div>

---

## 11. SONUÇ VE DEĞERLENDİRME

Bu proje çalışması ile Python programlama dili ve PyQt5 kütüphanesi kullanılarak, akademik ve sektörel standartlara uygun, son derece kararlı ve modern görsel tasarıma sahip etkileşimli bir Zihin Haritası uygulaması başarıyla tamamlanmıştır. Geliştirme süreci boyunca teorik bilgisayar bilimleri kavramları pratik bir yazılım ürününe dönüştürülmüştür.

Projenin geliştirilmesinde elde edilen en önemli kazanımlardan biri **Ağaç (Tree) Veri Yapısı**'nın gerçek bir uygulamada nasıl yönetileceğinin deneyimlenmesi olmuştur. Teorik derslerde görülen düğüm ekleme, silme ve rekürsif ağaç dolaşma (traversal) algoritmalarının, grafik arayüzündeki görsel öğelerle nasıl senkronize edileceği uygulamalı olarak öğrenilmiştir. Özellikle bir düğüm silindiğinde onun altındaki tüm dalların bellekten ve grafik sahnesinden güvenli bir şekilde temizlenmesi (garbage collection) ve bu esnada oluşan boşluğun kapatılması için kardeş düğümlerin yeniden konumlandırılması gibi karmaşık algoritmalar geliştirilmiştir.

Grafiksel kullanıcı arayüzü tasarımı tarafında, PyQt5'in `QGraphicsView` ve `QGraphicsScene` mimarisi derinlemesine incelenmiştir. Grafik nesnelerinin çizim süreçleri (Paint metodunun ezilmesi), koordinat sistemleri arasındaki dönüşümler (sahne koordinatlarından ekran koordinatlarına) ve fare/klavye olaylarının (event handling) özelleştirilmesi konularında uzmanlaşılmıştır. Kullanıcı deneyimini (UX) artırmak adına entegre edilen otomatik hizalama (Auto Arrange) algoritması, büyük şemaların karmaşasını tek bir tuşla çözebilen bir radyal yerleşim sunmuştur. Bu algoritmanın kodlanması sürecinde trigonometrik fonksiyonlar (sinüs, kosinüs, ark tanjant) aktif olarak kullanılmış, matematiksel modellerin yazılım dünyasındaki doğrudan karşılıkları gözlemlenmiştir.

Yazılım mimarisi açısından, modüler programlama ve nesneler arası zayıf bağ (loose coupling) kurma prensipleri başarıyla uygulanmıştır. Kodların `main.py`, `node.py`, `edge.py` gibi mantıksal sınıflara ayrılması, projenin okunabilirliğini artırdığı gibi, sonradan eklenen özelliklerin (örneğin şekil ve ikon özelleştirmeleri, renk kontrast ayarı, tema desteği) mevcut kararlı sisteme zarar vermeden kolayca entegre edilmesini sağlamıştır. Sinyal-slot mekanizmasının kullanımı, arayüz bileşenleri ile grafik sahnesindeki nesnelerin birbirlerinin iç işleyişlerini bilmeden asenkron haberleşebilmesine olanak tanımıştır.

Dosya yönetimi ve kalıcılık katmanında JSON tabanlı veri serileştirme modelleri kurulmuştur. Bellekteki nesnelerin diskteki dosyalara aktarılması ve geri okunması sırasında oluşan referans kayıplarını önlemek amacıyla UUID sistemleri geliştirilmiş, bu sayede kararlı bir yükleme sistemi elde edilmiştir. Ayrıca PNG dışa aktarım motoru ile sahnedeki nesnelerin sınırlarını algılayan bir piksel eşleme sistemi yazılmıştır.

Sonuç olarak bu proje, masaüstü uygulama geliştirme süreçlerinin tüm aşamalarını (gereksinim analizi, veri yapısı tasarımı, arayüz prototipleme, kodlama, hata ayıklama ve belgelendirme) kapsayan kapsamlı bir mühendislik çalışması olmuştur. Proje çıktısı olan zihin haritası uygulaması, öğrencilerin ve profesyonellerin günlük çalışmalarında kullanabilecekleri işlevsellikte ve kararlılıkta bir yazılım ürünü haline getirilmiştir. Elde edilen tecrübeler, nesne yönelimli tasarım kalıpları ve grafiksel kullanıcı arayüzü mimarileri konularında ileri düzey yazılımlar tasarlamak için güçlü bir temel oluşturmuştur.

<div style="page-break-after: always;"></div>

---

## 12. KAYNAKÇA

1. Buzan, T. (2006). *The Mind Map Book: How to Use Radiant Thinking to Maximize Your Brain's Untapped Potential*. BBC Active.
2. Summerfield, M. (2018). *Rapid GUI Programming with Python and Qt: The Definitive Guide to PyQt Programming*. Prentice Hall.
3. Rischpater, R. (2013). *Application Development with Qt5*. Packt Publishing.
4. Python Software Foundation. (2026). *Python Language Reference, Version 3.10*. Available at: https://www.python.org
5. Riverbank Computing. (2025). *PyQt5 Reference Guide*. Available at: https://www.riverbankcomputing.com/static/Docs/PyQt5/
6. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.
7. Lhotka, R. (2008). *Visual Studio and Qt Designer Integration Handbook*. Microsoft Press.
