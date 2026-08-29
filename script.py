import streamlit as st
from datetime import datetime, time
import ephem
import math
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
import numpy as np


st.set_page_config(page_title="Doğum Haritası & Analiz",page_icon="⚝", layout="centered")
st.title("⚝ Doğum Haritası, Evler  & Kişilik Analizi")
st.write("Doğum bilgilerinizi girerek haritanızı, ev sisteminizi ve detaylı astrolojik analizlerinizi keşfedin..")

ZODIAC_SIGNS=[
    "KOÇ(Aries)", "BOĞA(Taurus)", "İKİZLER(Gemini)", "YENGEÇ(Cancer)",
    "ASLAN(Leo)", "BAŞAK(Virgo)", "TERAZİ(Libra)", "AKREP(Scorpio)",
    "YAY(Sagittarius)", "OĞLAK(Capricorn)", "KOVA(Aquarius)", "BALIK(Pisces)"
]

def deg_to_zodiac(degrees):
    degrees= degrees % 360
    sign_idx = int(degrees // 30)
    sign_deg= degrees % 30
    return ZODIAC_SIGNS[sign_idx], round(sign_deg,2)

DETAILED_INTERPRETATIONS={
"KOÇ": {
        "element": "Ateş (Öncü)",
        "yonetici": "Mars",
        "ozet": "Zodyak'ın ilk burcu olan Koç; saf yaşam enerjisini, cesareti, öncülüğü ve bağımsızlığı simgeler. Hayata 'Ben varım' diyerek başlar ve zorluklar karşısında yılmadan mücadele eder.",
        "guclu_yonler": "Yüksek motivasyon, kriz anlarında hızlı inisiyatif alma, dürüstlük, cesaret ve engelleri aşma azmi.",
        "golge_yonler": "Sabırsızlık, çabuk öfkelenme, başladığı işi bitirmekte zorlanma ve düşünmeden fevri kararlar alma eğilimi.",
        "tavsiye": "Enerjinizi uzun vadeli projelere sabırla kanalize etmeyi ve dinleme becerinizi geliştirmeyi deneyin."
    },
"BOĞA": {
        "element": "Toprak (Sabit)",
        "yonetici": "Venüs",
        "ozet": "Maddi ve manevi güvenliği, istikrarı, üretkenliği ve somut değerleri temsil eder. Beş duyuya hitap eden estetik zevkleri ve sabırlı yapısıyla bilinir.",
        "guclu_yonler": "Sarsılmaz sadakat, güvenilirlik, finansal yönetim becerisi, yüksek sabır ve metodik çalışma disiplini.",
        "golge_yonler": "Değişime ve yeniliklere direnç gösterme, inatçılık, konfor alanından çıkmakta zorlanma ve aşırı sahiplenicilik.",
        "tavsiye": "Hayatın akışına ve kaçınılmaz değişimlere karşı daha esnek olmaya özen gösterin."
    },
"İKİZLER": {
        "element": "Hava (Değişken)",
        "yonetici": "Merkür",
        "ozet": "Bilgi akışını, entelektüel merakı, iletişimi ve çok yönlülüğü simgeler. Zihni durmaksızın yeni fikirler üretir ve bağlantılar kurar.",
        "guclu_yonler": "Üstün adaptasyon yeteneği, ikna kabiliyeti, hızlı öğrenme, esprili zeka ve zengin sosyal iletişim ağı.",
        "golge_yonler": "Odaklanma güçlüğü, yüzeysel bilgiyle yetinme, kararsızlık ve zihinsel aşırı yorgunluk/huzursuzluk.",
        "tavsiye": "Zihinsel enerjinizi tek bir alanda derinleştirmek uzun vadeli başarılarınızı katlayacaktır."
    },
    "YENGEÇ": {
        "element": "Su (Öncü)",
        "yonetici": "Ay",
        "ozet": "Duygusal derinliği, kökleri, aile bağlarını, koruma içgüdüsünü ve yüksek sezgileri temsil eder. Güvenli bir yuva kurmak temel motivasyonudur.",
        "guclu_yonler": "Eşsiz empati gücü, fedakarlık, güçlü hafıza, sevdiklerini koruma içgüdüsü ve sanatsal sezgisellik.",
        "golge_yonler": "Duygusal iniş-çıkışlar (mood swings), alınganlık, geçmişe takılı kalma ve kabuğuna çekilerek küsme eğilimi.",
        "tavsiye": "Kendi duygusal sınırlarınızı korumayı ve geçmiş deneyimleri bir yük olarak taşımamayı öğrenmelisiniz."
    },
    "ASLAN": {
        "element": "Ateş (Sabit)",
        "yonetici": "Güneş",
        "ozet": "Yaratıcılığı, özgüveni, liderliği, cömertliği ve yaşam sevincini simgeler. Hayat sahnesinde doğal bir karizma ve ışıltıyla parlar.",
        "guclu_yonler": "Büyük vizyon kurabilme, cömertlik, motive edici liderlik, sıcak kalplilik ve yüksek yaratıcı enerji.",
        "golge_yonler": "Aşırı gurur, egonun zedelenmesine tahammülsüzlük, sürekli takdir bekleme ve otoriterleşme riski.",
        "tavsiye": "Alçakgönüllülüğü korumak ve başkalarının parlamasına alan açmak liderlik gücünüzü pekiştirir."
    },
    "BAŞAK": {
        "element": "Toprak (Değişken)",
        "yonetici": "Merkür",
        "ozet": "Analitik zekayı, hizmet bilincini, düzeni, titizliği ve detay hakimiyetini temsil eder. Hayattaki kaosu organize etme ustasıdır.",
        "guclu_yonler": "Detayları anında fark etme, pratik sorun çözme becerisi, yüksek iş ahlakı, yardımseverlik ve düzen kurma yeteneği.",
        "golge_yonler": "Aşırı eleştirellik, mükemmeliyetçilik kaygısı, detaylarda boğulup büyük resmi kaçırma ve yoğun evham.",
        "tavsiye": "'Mükemmel, iyinin düşmanıdır' ilkesini hatırlayarak kendinize ve çevrenize karşı daha hoşgörülü olun."
    },
    "TERAZİ": {
        "element": "Hava (Öncü)",
        "yonetici": "Venüs",
        "ozet": "Dengeyi, adaleti, estetiği, diplomasiyi ve ortaklıkları simgeler. İkili ilişkilerde uyum ve barış yaratma sanatçısıdır.",
        "guclu_yonler": "Kuvvetli adalet duygusu, uzlaştırıcı diplomasi, estetik vizyon, zarafet ve empatik iletişim.",
        "golge_yonler": "Huzur bozulmasın diye 'hayır' diyememe, çatışmadan kaçma, aşırı kararsızlık ve onay bağımlılığı.",
        "tavsiye": "Kendi doğrularınız ve kararlarınızın arkasında cesaretle durmaktan çekinmeyin."
    },
    "AKREP": {
        "element": "Su (Sabit)",
        "yonetici": "Plüton & Mars",
        "ozet": "Dönüşümü, psikolojik derinliği, tutkuyu, gizemi ve sarsılmaz iradeyi temsil eder. Yüzeysel olan hiçbir şeyle yetinmez, gerçeğin peşindedir.",
        "guclu_yonler": "Yüksek sezgi gücü, kriz yönetimi ustalığı, vazgeçmeyen irade, derin sadakat ve stratejik zeka.",
        "golge_yonler": "Şüphecilik, intikamcılık, kontrolü elden bırakamama ve duygusal olarak ketum/aşırı korumacı olma.",
        "tavsiye": "Kontrolü evrene bırakabilmeyi, affetmenin getireceği ruhsal özgürlüğü keşfetmelisiniz."
    },
    "YAY": {
        "element": "Ateş (Değişken)",
        "yonetici": "Jüpiter",
        "ozet": "Felsefeyi, yüksek bilinci, keşif arzusunu, özgürlüğü ve iyimserliği simgeler. Yaşamı anlamlandırmak için sürekli yeni ufuklar arar.",
        "guclu_yonler": "Geniş vizyon, sınırsız iyimserlik, öğrenme tutkusu, açık sözlülük ve ilham verici rehberlik.",
        "golge_yonler": "Aşırı fanatizm, detayları hafife alma, tutamayacağı sözler verme ve pervasızlık derecesinde patavatsızlık.",
        "tavsiye": "Büyük hedefleri adım adım planlayarak realize etmek ve sözlerinizin sınırlarını çizmek faydalı olacaktır."
    },
    "OĞLAK": {
        "element": "Toprak (Öncü)",
        "yonetici": "Satürn",
        "ozet": "Sorumluluğu, disiplini, sabrı, kariyeri ve somut yapıları inşa etmeyi temsil eder. Zirveye adım adım, sağlam taşlarla tırmanır.",
        "guclu_yonler": "Üstün stratejik planlama, krizlere karşı dayanıklılık, güvenilirlik, liderlik ve yüksek sorumluluk bilinci.",
        "golge_yonler": "Aşırı katılık, duyguları bastırma, karamsarlık, işkoliklik ve hata yapma korkusu.",
        "tavsiye": "Hayatın sadece görevlerden ibaret olmadığını hatırlayarak dinlenmeye ve duygusal paylaşımlara vakit ayırın."
    },
    "KOVA": {
        "element": "Hava (Sabit)",
        "yonetici": "Uranüs & Satürn",
        "ozet": "Bireyselliği, yenilikçiliği, bilimi, hümanizmi ve özgür düşünceyi simgeler. Toplumsal kalıpların ötesinde, geleceğe odaklı yaşar.",
        "guclu_yonler": "Sıradışı vizyon, mucitlik zekası, objektif bakış açısı, insani yardımseverlik ve entelektüel özgünlük.",
        "golge_yonler": "Duygusal mesafelilik, aşırı asilik/sırf karşı çıkmak için muhalefet etme ve soğuk mantıkçılık.",
        "tavsiye": "Fikir dünyanızı zenginleştirirken kalp bağını ve duygusal yakınlığı ihmal etmeyin."
    },
    "BALIK": {
        "element": "Su (Değişken)",
        "yonetici": "Neptün & Jüpiter",
        "ozet": "Kozmik birliği, sınırsız hayal gücünü, şefkati ve ruhsal sezgileri simgeler. Zodyak'ın tüm burçlarının deneyimini içinde taşır.",
        "guclu_yonler": "Muazzam empati yeteneği, sanatsal ilham, güçlü altıncı his, koşulsuz sevgi ve ruhsal bilgelik.",
        "golge_yonler": "Gerçeklerden kaçış eğilimi, kurban psikolojisine girme, sınır koyamama ve aşırı hayalperestlik.",
        "tavsiye": "Topraklanma pratikleri yaparak hayallerinizi somut dünyada birer esere dönüştürmeye odaklanın."
    }
}




def draw_chart_wheel(planets_data, asc_deg_total):
    fig, ax= plt.subplots(figsize=(9,9), subplot_kw={'projection': 'polar'})
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    colors= ['#FF4B4B', '#FFAA00', '#00D4B2','#0068C9']*3
    signs_short= ["KOÇ", "BOĞA", "İKİZLER", "YENGEÇ", "ASLAN", "BAŞAK", "TERAZİ", "AKREP", "YAY", "OĞLAK", "KOVA", "BALIK"]

    for i in range(12):
        start_rad= np.radians(i*30)
        ax.bar(x=start_rad + np.radians(15), height=2.0, width= np.radians(30), bottom=8.0, color=colors[i], alpha=0.35, edgecolor='#4B5563', linewidth=1)
        ax.text(start_rad + np.radians(15), 9.0, signs_short[i],
                color='white', fontsize=9, fontweight='bold', ha='center', va='center')
    theta = np.linspace(0, 2 * np.pi, 200)
    ax.plot(theta, [8.0] * len(theta), color='#4B5563', lw=1.5)
    ax.plot(theta, [10.0] * len(theta), color='#4B5563', lw=1.5)
    ax.plot(theta, [4.0] * len(theta), color='#374151', lw=1, linestyle='--')

    for h in range(12):
        house_deg= (asc_deg_total + h*30)%360
        house_rad= np.radians(house_deg)
        ax.plot([house_rad, house_rad], [0,8.0], color="#374151", lw=0.8, linestyle='--')
        h_label_rad= np.radians((house_deg+15)%360)
        ax.text(h_label_rad, 3.2, str(h+1), color='#9CA3AF' ,fontsize=8,ha='center' ,va='center')





    planet_symbols = {
        "Güneş (Sun)": "☉ Sun", "Ay (Moon)": "☽ Moon", "Merkür (Mercury)": "☿ Mer",
        "Venüs (Venus)": "♀ Ven", "Mars": "♂ Mar", "Jüpiter (Jupiter)": "♃ Jup",
        "Satürn (Saturn)": "♄ Sat", "Uranüs (Uranus)": "♅ Ura",
        "Neptün (Neptune)": "♆ Nep", "Plüton (Pluto)": "♇ Plu"
    }

    radii=[7.2, 6.3, 5.4, 4.5, 7.2, 6.3, 5.4, 4.5, 6.8, 5.8]
    planet_positions=[]


    for idx, p in enumerate(planets_data):
        deg_str=str(p.get("Toplam Eliptik Boylam", p.get("Toplam Boylam",0))).replace("°", "")
        deg=float(deg_str)
        rad=np.radians(deg)
        r=radii[idx%len(radii)]
        planet_positions.append((rad, r, deg))


        name= p["Gezegen"]
        label=planet_symbols.get(p["Gezegen"],p["Gezegen"][:3])
        deg_label = p.get("Derece", p.get("Derece", ""))


        ax.scatter(rad,r, color= '#FFD700', s=35, zorder=5)
        ax.text(rad, r+0.35, f"{label}\n{p['Derece']}", color='#E0E0E0', fontsize=7.5, ha='center', weight='bold')

        asc_rad= np.radians(asc_deg_total)
        ax.annotate('', xy=(asc_rad, 8.0), xytext=(asc_rad,0), arrowprops= dict(arrowstyle="->", color="#00FFAA", lw=2))
        ax.text(asc_rad, 8.4, "ASC", color="#00FFAA", fontweight="bold", fontsize=10, ha="center")

        num_planets= len(planet_positions)
        for i in range (num_planets):
            for j in range(i+1, num_planets):
                rad1, r1, deg1= planet_positions[i]
                rad2, r2, deg2= planet_positions[j]
                diff= abs(deg1-deg2)
                angle= min(diff, 360-diff)

                if abs(angle-120)<=5:
                    ax.plot([rad1, rad2], [r1,r2], color='#00D4B2', lw=1.2,alpha=0.6)
                elif abs(angle-90)<=5 or abs(angle-180)<=5:
                    ax.plot([rad1,rad2], [r1,r2], color='#FF4B4B', lw=1.2, alpha=0.6)
        asc_rad= np.radians(asc_deg_total)
        ax.annotate('', xy=(asc_rad, 8.0), xytext= (asc_rad, 0), arrowprops= dict(arrowstyle="->", color="#00FFAA", lw=2.5))
        ax.text(asc_rad, 8.4, "ASC", color="#00FFAA", fontweight= "bold", fontsize=10, ha="center")



        ax.set_theta_zero_location('E')
        ax.set_theta_direction(1)
        ax.set_rticks([])
        ax.set_xticks([])
        ax.spines['polar'].set_visible(False)
        ax.grid(False)

    return fig


with st.form("astrology_form"):
    col1, col2= st.columns(2)
    with col1:
        birth_date = st.date_input(
            "Doğum Tarihi",
            min_value=datetime(1920, 1, 1).date(),
            max_value=datetime.today().date(),
            value=datetime(2000, 1, 1).date()
        )

    with col2:
        birth_time= st.time_input("Doğum Saati", value=time(12,0))

    city= st.text_input("Doğum Yeri (Şehir, Ülke)", value="Mersin, Türkiye")
    submitted= st.form_submit_button("Haritayı Hesapla")

def calculate_astrology(b_date, b_time, city_name):
    geolocator = Nominatim(user_agent="astro_py314_app")
    location = geolocator.geocode(city_name)

    if not location:
        return None, "Konum bulunamadı. Lütfen geçerli bir şehir yazın."


    obs = ephem.Observer()
    obs.lat = str(location.latitude)
    obs.lon = str(location.longitude)
    obs.elevation = 0

    dt_local = datetime.combine(b_date, b_time)
    dt_utc = ephem.Date(dt_local) - (3.0 / 24.0)
    obs.date = dt_utc

    celestial_bodies = {
        "Güneş(Sun)": ephem.Sun(obs),
        "Ay(Moon)": ephem.Moon(obs),
        "Merkür(Mercury)": ephem.Mercury(obs),
        "Venüs": ephem.Venus(obs),
        "Mars": ephem.Mars(obs),
        "Jupiter": ephem.Jupiter(obs),
        "Saturn": ephem.Saturn(obs),
        "Uranüs": ephem.Uranus(obs),
        "Neptune": ephem.Neptune(obs),
        "Pluto": ephem.Pluto(obs),
    }

    planet_results = []
    for name, body in celestial_bodies.items():
        ecl = ephem.Ecliptic(body)
        lon_deg = math.degrees(ecl.lon)
        sign, deg = deg_to_zodiac(lon_deg)
        planet_results.append({
            "Gezegen": name,
            "Burç": sign,
            "Derece": f"{deg}°",
            "Toplam Eliptik Boylam": f"{round(lon_deg, 2)}°"
        })

    sidereal_time = obs.sidereal_time()
    lat_rad = obs.lat
    eps = math.radians(23.4392911)

    asc_rad = math.atan2(
        math.cos(sidereal_time),
        -math.sin(sidereal_time) * math.cos(eps) - math.tan(lat_rad) * math.sin(eps)

    )
    asc_deg = (math.degrees(asc_rad) + 360) % 360
    asc_sign, asc_sig_deg = deg_to_zodiac(asc_deg)

    return {
        "sun": planet_results[0],
        "moon": planet_results[1],
        "asc": {"sign": asc_sign, "deg": asc_sig_deg},
        "asc_deg_raw": asc_deg,
        "planets": planet_results
    }, None




if submitted:
    with st.spinner("Haritanız çıkarılıyor ve analizler hazırlanıyor..."):
        data, err = calculate_astrology(birth_date, birth_time, city)
        if err:
            st.error(err)
        else:
            st.success("Hesaplama tamamlandı! ")
            st.subheader("Temel Yerleşimler")
            m1, m2, m3 = st.columns(3)
            sun_deg= data['sun'].get('Derece', data['sun'].get('Derece, '))
            m1.metric("Güneş Burcu", f"{data['sun']['Burç']} {data['sun']['Derece']}")
            m2.metric("Yükselen (ASC)", f"{data['asc']['sign']} {data['asc']['deg']}°")
            moon_deg= data['moon'].get('Derece', '')
            m3.metric("Ay Burcu", f"{data['moon']['Burç']} {moon_deg}")


            st.write("---")


            st.subheader("Derinlemesine Astrolojik Kişilik Analizi")
            sun_key= data['sun']['Burç'].split("(")[0].strip()
            asc_key= data['asc']['sign'].split("(")[0].strip()
            moon_key= data['moon']['Burç'].split("(")[0].strip()
            sun_info= DETAILED_INTERPRETATIONS.get(sun_key,{})
            asc_info= DETAILED_INTERPRETATIONS.get(asc_key,{})
            moon_info= DETAILED_INTERPRETATIONS.get(moon_key,{})

            with st.expander(f"GÜNEŞ BURCUNUZ: {data['sun']['Burç']}(Öz Benlik & Yaşam Amacı", expanded=True):
                st.markdown(f"**Element/Nitelik:** `{sun_info.get('element')}` | **Yönetici Gezegen:** `{sun_info.get('yonetici')}`")
                st.write(sun_info.get("ozet"))
                col_g1, col_g2= st.columns(2)
                with col_g1:
                    st.success(f"**Güçlü Yönler:** \n\n{sun_info.get('guclu_yonler')}")
                with col_g2:
                    st.warning(f"**Dikkat Edilmesi Gerekenler:**\n\n{sun_info.get('golge_yonler')}")
                st.info(f" **Gelişim Tavsiyesi:** {sun_info.get('tavsiye')}")

            with st.expander(f" YÜKSELEN BURCUNUZ: {data['asc']['sign']} (Dış Dünya Maskesi & Sosyal İmaj)",
                             expanded=False):
                st.markdown(
                    f"**Element / Nitelik:** `{asc_info.get('element')}` | **Yönetici Gezegen:** `{asc_info.get('yonetici')}`")
                st.write(
                    f"İnsanların sizi ilk gördüklerinde algıladıkları enerji, duruşunuz ve fiziki motivasyonunuz bu burcun nitelikleriyle şekillenir: {asc_info.get('ozet')}")
                st.write(f"**Sosyal Duruş:** {asc_info.get('guclu_yonler')}")


            with st.expander(f" AY BURCUNUZ: {data['moon']['Burç']} (Bilinçaltı & Duygusal İhtiyaçlar)",
                             expanded=False):
                st.markdown(
                    f"**Element / Nitelik:** `{moon_info.get('element')}` | **Yönetici Gezegen:** `{moon_info.get('yonetici')}`")
                st.write(
                    f"Duygusal güvenlik arayışınız, iç dünyanız ve yalnız kaldığınızda verdiğiniz tepkiler bu burç tarafından yönetilir: {moon_info.get('ozet')}")
                st.write(f"**Duygusal İhtiyaç:** {moon_info.get('tavsiye')}")

            st.write("---")

            st.subheader(" Dairesel Doğum Haritası Çarkı")
            fig = draw_chart_wheel(data["planets"], data["asc_deg_raw"])
            st.pyplot(fig)










