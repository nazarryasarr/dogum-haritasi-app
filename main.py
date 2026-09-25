import math 
from datetime import date, datetime, time
from typing import Optional

import ephem
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from geopy.geocoders import Nominatim

app= FastAPI(
    tittle= "Astroloji Doğum Haritası API",
    description= "Kullanıcı doğum bilgilerini alarak gezegen konumlarını, yükseleni ve burç analizlerini hesaplayan servis",
    version= "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ZODİAC_SİGNS=[
    "Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak",
    "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"
]

DETAILED_INTERPRETATIONS={
    "Koç": {
        "element":"ATeş (Öncü)",
        "yönetici": "Mars",
        "özet": " Zodyak'ın ilk burcu olan Koç; saf yaşam enerjisini, cesareti, öncülüğü ve bağımsızlığı simgeler. Hayata 'Ben varım' diyerek başlar ve zorluklar karşısında yılmadan mücadele eder.",
        "guclu_yonler": "Yüksek motivasyon, kriz anlarında hızlı inisiyatif alma, dürüstlük, cesaret ve engelleri aşma azmi.",
        "golge_yonler": "Sabırsızlık, çabuk öfkelenme, başladığı işi bitirmekte zorlanma ve düşünmeden fevri kararlar alma eğilimi.",
        "tavsiye": "Enerjinizi uzun vadeli projelere sabırla kanalize etmeyi ve dinleme becerinizi geliştirmeyi deneyin.",
    },
    "Boğa": {
        "element": "Toprak (Sabit)",
        "yonetici": "Venüs",
        "ozet": "Maddi ve manevi güvenliği, istikrarı, üretkenliği ve somut değerleri temsil eder. Beş duyuya hitap eden estetik zevkleri ve sabırlı yapısıyla bilinir.",
        "guclu_yonler": "Sarsılmaz sadakat, güvenilirlik, finansal yönetim becerisi, yüksek sabır ve metodik çalışma disiplini.",
        "golge_yonler": "Değişime ve yeniliklere direnç gösterme, inatçılık, konfor alanından çıkmakta zorlanma ve aşırı sahiplenicilik.",
        "tavsiye": "Hayatın akışına ve kaçınılmaz değişimlere karşı daha esnek olmaya özen gösterin.",
    },
    "İkizler": {
        "element": "Hava (Değişken)",
        "yonetici": "Merkür",
        "ozet": "Bilgi akışını, entelektüel merakı, iletişimi ve çok yönlülüğü simgeler. Zihni durmaksızın yeni fikirler üretir ve bağlantılar kurar.",
        "guclu_yonler": "Üstün adaptasyon yeteneği, ikna kabiliyeti, hızlı öğrenme, esprili zeka ve zengin sosyal iletişim ağı.",
        "golge_yonler": "Odaklanma güçlüğü, yüzeysel bilgiyle yetinme, kararsızlık ve zihinsel aşırı yorgunluk/huzursuzluk.",
        "tavsiye": "Zihinsel enerjinizi tek bir alanda derinleştirmek uzun vadeli başarılarınızı katlayacaktır.",
    },
    "Yengeç": {
        "element": "Su (Öncü)",
        "yonetici": "Ay",
        "ozet": "Duygusal derinliği, kökleri, aile bağlarını, koruma içgüdüsünü ve yüksek sezgileri temsil eder. Güvenli bir yuva kurmak temel motivasyonudur.",
        "guclu_yonler": "Eşsiz empati gücü, fedakarlık, güçlü hafıza, sevdiklerini koruma içgüdüsü ve sanatsal sezgisellik.",
        "golge_yonler": "Duygusal iniş-çıkışlar (mood swings), alınganlık, geçmişe takılı kalma ve kabuğuna çekilerek küsme eğilimi.",
        "tavsiye": "Kendi duygusal sınırlarınızı korumayı ve geçmiş deneyimleri bir yük olarak taşımamayı öğrenmelisiniz.",
    },
    "Aslan": {
        "element": "Ateş (Sabit)",
        "yonetici": "Güneş",
        "ozet": "Yaratıcılığı, özgüveni, liderliği, cömertliği ve yaşam sevincini simgeler. Hayat sahnesinde doğal bir karizma ve ışıltıyla parlar.",
        "guclu_yonler": "Büyük vizyon kurabilme, cömertlik, motive edici liderlik, sıcak kalplilik ve yüksek yaratıcı enerji.",
        "golge_yonler": "Aşırı gurur, egonun zedelenmesine tahammülsüzlük, sürekli takdir bekleme ve otoriterleşme riski.",
        "tavsiye": "Alçakgönüllülüğü korumak ve başkalarının parlamasına alan açmak liderlik gücünüzü pekiştirir.",
    },
    "Başak": {
        "element": "Toprak (Değişken)",
        "yonetici": "Merkür",
        "ozet": "Analitik zekayı, hizmet bilincini, düzeni, titizliği ve detay hakimiyetini temsil eder. Hayattaki kaosu organize etme ustasıdır.",
        "guclu_yonler": "Detayları anında fark etme, pratik sorun çözme becerisi, yüksek iş ahlakı, yardımseverlik ve düzen kurma yeteneği.",
        "golge_yonler": "Aşırı eleştirellik, mükemmeliyetçilik kaygısı, detaylarda boğulup büyük resmi kaçırma ve yoğun evham.",
        "tavsiye": "'Mükemmel, iyinin düşmanıdır' ilkesini hatırlayarak kendinize ve çevrenize karşı daha hoşgörülü olun.",
    },
    "Terazi": {
        "element": "Hava (Öncü)",
        "yonetici": "Venüs",
        "ozet": "Dengeyi, adaleti, estetiği, diplomasiyi ve ortaklıkları simgeler. İkili ilişkilerde uyum ve barış yaratma sanatçısıdır.",
        "guclu_yonler": "Kuvvetli adalet duygusu, uzlaştırıcı diplomasi, estetik vizyon, zarafet ve empatik iletişim.",
        "golge_yonler": "Huzur bozulmasın diye 'hayır' diyememe, çatışmadan kaçma, aşırı kararsızlık ve onay bağımlılığı.",
        "tavsiye": "Kendi doğrularınız ve kararlarınızın arkasında cesaretle durmaktan çekinmeyin.",
    },
    "Akrep": {
        "element": "Su (Sabit)",
        "yonetici": "Plüton & Mars",
        "ozet": "Dönüşümü, psikolojik derinliği, tutkuyu, gizemi ve sarsılmaz iradeyi temsil eder. Yüzeysel olan hiçbir şeyle yetinmez, gerçeğin peşindedir.",
        "guclu_yonler": "Yüksek sezgi gücü, kriz yönetimi ustalığı, vazgeçmeyen irade, derin sadakat ve stratejik zeka.",
        "golge_yonler": "Şüphecilik, intikamcılık, kontrolü elden bırakamama ve duygusal olarak ketum/aşırı korumacı olma.",
        "tavsiye": "Kontrolü evrene bırakabilmeyi, affetmenin getireceği ruhsal özgürlüğü keşfetmelisiniz.",
    },
    "Yay": {
        "element": "Ateş (Değişken)",
        "yonetici": "Jüpiter",
        "ozet": "Felsefeyi, yüksek bilinci, keşif arzusunu, özgürlüğü ve iyimserliği simgeler. Yaşamı anlamlandırmak için sürekli yeni ufuklar arar.",
        "guclu_yonler": "Geniş vizyon, sınırsız iyimserlik, öğrenme tutkusu, açık sözlülük ve ilham verici rehberlik.",
        "golge_yonler": "Aşırı fanatizm, detayları hafife alma, tutamayacağı sözler verme ve pervasızlık derecesinde patavatsızlık.",
        "tavsiye": "Büyük hedefleri adım adım planlayarak realize etmek ve sözlerinizin sınırlarını çizmek faydalı olacaktır.",
    },
    "Oğlak": {
        "element": "Toprak (Öncü)",
        "yonetici": "Satürn",
        "ozet": "Sorumluluğu, disiplini, sabrı, kariyeri ve somut yapıları inşa etmeyi temsil eder. Zirveye adım adım, sağlam taşlarla tırmanır.",
        "guclu_yonler": "Üstün stratejik planlama, krizlere karşı dayanıklılık, güvenilirlik, liderlik ve yüksek sorumluluk bilinci.",
        "golge_yonler": "Aşırı katılık, duyguları bastırma, karamsarlık, işkoliklik ve hata yapma korkusu.",
        "tavsiye": "Hayatın sadece görevlerden ibaret olmadığını hatırlayarak dinlenmeye ve duygusal paylaşımlara vakit ayırın.",
    },
    "Kova": {
        "element": "Hava (Sabit)",
        "yonetici": "Uranüs & Satürn",
        "ozet": "Bireyselliği, yenilikçiliği, bilimi, hümanizmi ve özgür düşünceyi simgeler. Toplumsal kalıpların ötesinde, geleceğe odaklı yaşar.",
        "guclu_yonler": "Sıradışı vizyon, mucitlik zekası, objektif bakış açısı, insani yardımseverlik ve entelektüel özgünlük.",
        "golge_yonler": "Duygusal mesafelilik, aşırı asilik/sırf karşı çıkmak için muhalefet etme ve soğuk mantıkçılık.",
        "tavsiye": "Fikir dünyanızı zenginleştirirken kalp bağını ve duygusal yakınlığı ihmal etmeyin.",
    },
    "Balık": {
        "element": "Su (Değişken)",
        "yonetici": "Neptün & Jüpiter",
        "ozet": "Kozmik birliği, sınırsız hayal gücünü, şefkati ve ruhsal sezgileri simgeler. Zodyak'ın tüm burçlarının deneyimini içinde taşır.",
        "guclu_yonler": "Muazzam empati yeteneği, sanatsal ilham, güçlü altıncı his, koşulsuz sevgi ve ruhsal bilgelik.",
        "golge_yonler": "Gerçeklerden kaçış eğilimi, kurban psikolojisine girme, sınır koyamama ve aşırı hayalperestlik.",
        "tavsiye": "Topraklanma pratikleri yaparak hayallerinizi somut dünyada birer esere dönüştürmeye odaklanın.",
    },
}

def deg_to_zodiac(degrees: float):
    degrees= degrees % 360
    sign_idx= int( degrees//30)
    sign_deg= degrees%30
    return ZODİAC_SİGNS[sign_idx], round(sign_deg,2)

class BirthChartRequest(BaseModel):
    birth_date: str= Field(
        ...,
        dedscription= "Doğum tarihi (Gün.Ay.Yıl ÖRN:15.05.2000)",
        EXAMPLE="15.05.2000",

    )

    birth_time: time = Field(default= time(12,0), exampple="14:30:00")
    city: Optional[str]= Field(default=None, example="Mersin.Türkiye")
    latitude: Optional[float]= Field(default=None, exapmle=36.80)
    longitude: Optional[float]= Field(default=None, example=34.63)

    @field_validator("birth_date")
    @classmethod
    def validate_and_parse_birth_date(cls, v: str)-> str:
        formats= ["%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
        parsed_date= None

        for fmt in formats:
            try:
                parsed_date= datetime.strptime(v.strip(), fmt).date()
                break
            except ValueError:
                continue

        if not parsed_date:
            raise ValueError(
                "Ge.ersiz tarih formatı! Lütfen 'GG.AA.YYYY' şeklinde geçerli bir gün, ay, yıl girin."

            )
        min_date= date(1900,1,1)
        max_date= date.today()

        if parsed_date<min_date or parsed_date>max_date:
            raise ValueError(
                f"Tarih 1900 ile günümüz ({max_date.strftime('%d.%m.%Y')}) arasında olmalıdır!"
            )
        return parsed_date.strftime("%d.%m.%Y")
@app.get("/")
def health_check():
    return{
        "status": "online",
        "message": "Astroloji Doğum Haritası API servisi aktif."
    }


@app.post("/api/birth-chart")
def calculate_birth_chart(payload: BirthChartRequest):
    parsed_birth_date= datetime.strptime(payload.birth_date, "%d.%m.%Y").date()

    lat= payload.latitude
    lon= payload.longitude

    if lat is None or lon is None:
        if not payload.city:
            raise HTTPException(
                status_code=400,
                detail="Lütfen  ' city' (şehir adı) veya 'latitude' / 'longitude' koordinatlarını girin.",

            )
        geolocator= Nominatim(user_agent="astro_flutter_backend_app")
        location= geolocator.geocode(payload.city)
        if not location:
            raise HTTPException(
                status_code=404,
                detail="Belirtilen şehir konumu bulunamadı. Lütfen geçerli bir şehir yazın",

            )
        lat= location.latitude
        lon= location.longitude

    obs= ephem.Observer()
    obs.lat= str(lat)
    obs.lon=str(lon)
    obs.elevation= 0

    dt_local= datetime.combine(parsed_birth_date, payload.birth_time)
    dt_utc= ephem.Date(dt_local)- (3.0/24.0)
    obs.date= dt_utc

    celestial_bodies={
        "Güneş": ephem.Sun(obs),
        "Ay": ephem.Moon(obs),
        "Merkür": ephem.Mercury(obs),
        "Venüs": ephem.Venus(obs),
        "Mars": ephem.Mars(obs),
        "Jüpiter": ephem.Jupiter(obs),
        "Satürn": ephem.Saturn(obs),
        "Uranüs": ephem.Uranus(obs),
        "Neptün": ephem.Neptune(obs),
        "Plüton": ephem.Pluto(obs),

    }


    planet_results= []
    for name, body in celestial_bodies.items():
        ecl= ephem.Ecliptic(body)
        lon_deg= math.degrees(ecl.lon)
        sign, deg= deg_to_zodiac(lon_deg)
        planet_results.append(
            {
                "planet": name,
                "sign": sign,
                "degree": deg,
                "total_ecliptic_longitude": round(lon_deg,2),
            }
        )

    sidereal_time= obs.sidereal_time()
    lat_rad= float(obs.lat)
    eps= math.radians(23.4392911)

    asc_rad= math.atan2(
        math.cos(sidereal_time),
        -math.sin(sidereal_time)* math.cos(eps)
        -math.tan(lat_rad)* math.sin(eps),
    )

    asc_deg= (math.degrees(asc_rad)+360)%360
    asc_sign, asc_deg_in_sign= deg_to_zodiac(asc_deg)
    sun_data= planet_results[0]
    moon_data= planet_results[1]

    return{
        "input_summary":{
            "birth_date": payload.birth_date,
            "bith_time": str(payload.birth_time),
            "location_used":{
                "city": payload.city,
                "latitude": round(lat,4),
                "longitude": round(lon,4),
            },
        },
        "core_placements":{
            "sign": sun_data["sign"],
            "degree": sun_data["degree"],
            "total_degree": sun_data["total_ecliptic_longitude"],
            "analysis": DETAILED_INTERPRETATIONS.get(sun_data["sign"],{}),
        
        },

        "rising":{
            "sign": asc_sign,
            "degree":asc_deg_in_sign,
            "total_degree": round(asc_deg,2),
            "analysis": DETAILED_INTERPRETATIONS.get(asc_sign,{}),
        },
        "moon":{
            
            "sign": moon_data["sign"],
            "degree": moon_data["degree"],
            "total_degree": moon_data["total_ecliptic_longitude"],
            "analysis": DETAILED_INTERPRETATIONS.get(moon_data["sign"],{}),
        },
        "all_planets": planet_results,
        "raw_ascending_degree": round(asc_deg,2),


    }




        

   

                           
                           
