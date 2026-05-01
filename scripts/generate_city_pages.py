#!/usr/bin/env python3
"""Generate city SEO landing pages for piumosso.pl/slub/[city]/"""
import os, re, textwrap
from pathlib import Path

ROOT = Path(__file__).parent.parent
SLUB = ROOT / "slub"

# Read NL_TOKEN from index.html
def get_nl_token():
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r'const NL_TOKEN = (\[[\d,]+\]\.map\(c=>String\.fromCharCode\(c\)\)\.join\(""\));', src)
    return m.group(1) if m else '["token_not_found"]'

NL_TOKEN_JS = get_nl_token()

CITIES = [
    {"slug":"warszawa","name":"Warszawa","lok":"w Warszawie","gen":"Warszawy","miej":"Warszawie",
     "region":"Mazowsze","venues":["Katedrze Świętego Jana Chrzciciela","Bazylice Świętego Krzyża","Kościele Świętej Anny","Zamku Królewskim","Pałacu w Wilanowie"],
     "venues_short":["Katedra Świętego Jana","Bazylika Świętego Krzyża","Kościół Świętej Anny","Zamek Królewski","Pałac Wilanów"],
     "desc_extra":"stolica Polski z tysiącem wyjątkowych miejsc na ceremonię — od gotyckich kościołów Starego Miasta po eleganckie pałace na Mazowszu"},
    {"slug":"krakow","name":"Kraków","lok":"w Krakowie","gen":"Krakowa","miej":"Krakowie",
     "region":"Małopolska","venues":["Kościele Mariackim","Bazylice Bożego Ciała","Kaplicy Królewskiej na Wawelu","Pałacu Bonerowski","Kościele Świętej Katarzyny"],
     "venues_short":["Kościół Mariacki","Bazylika Bożego Ciała","Kaplica na Wawelu","Pałac Bonerowski","Stara Zajezdnia"],
     "desc_extra":"królewskie miasto z niezrównaną architekturą — Wawel, Kazimierz i Stare Miasto tworzą idealne tło dla muzyki klasycznej"},
    {"slug":"poznan","name":"Poznań","lok":"w Poznaniu","gen":"Poznania","miej":"Poznaniu",
     "region":"Wielkopolska","venues":["Katedrze Poznańskiej na Ostrowie Tumskim","Farze Poznańskiej","Zamku Cesarskim","Pałacu Działyńskich","Kościele Świętego Marcina"],
     "venues_short":["Katedra Poznańska","Fara Poznańska","Zamek Cesarski","Pałac Działyńskich","Centrum Kongresowe MTP"],
     "desc_extra":"nasze rodzinne miasto — znamy każdy kościół, każdą salę i każdą akustykę. Gramy tutaj najczęściej"},
    {"slug":"wroclaw","name":"Wrocław","lok":"we Wrocławiu","gen":"Wrocławia","miej":"Wrocławiu",
     "region":"Dolny Śląsk","venues":["Katedrze Wrocławskiej","Kościele Świętego Krzyża","Auli Leopoldina","Hali Stulecia","Pałacu Hatzfeldów"],
     "venues_short":["Katedra Wrocławska","Kościół Świętego Krzyża","Aula Leopoldina","Hala Stulecia","Pałac Hatzfeldów"],
     "desc_extra":"miasto stu mostów z wyjątkową przestrzenią muzyczną — Ostrów Tumski i zabytkowe sale Dolnego Śląska to jedne z najpiękniejszych dekoracji na ślub"},
    {"slug":"gdansk","name":"Gdańsk","lok":"w Gdańsku","gen":"Gdańska","miej":"Gdańsku",
     "region":"Trójmiasto / Pomorze","venues":["Kościele Mariackim w Gdańsku","Dworze Artusa","Bazylice Oliwskiej","Pałacu Opatów w Oliwie","Kościele Świętego Mikołaja"],
     "venues_short":["Kościół Mariacki","Dwór Artusa","Bazylika Oliwska","Pałac Opatów","Długi Targ"],
     "desc_extra":"port morski z historyczną atmosferą — Stare Miasto Gdańska i Oliwa oferują przestrzenie o niepowtarzalnym klimacie"},
    {"slug":"lodz","name":"Łódź","lok":"w Łodzi","gen":"Łodzi","miej":"Łodzi",
     "region":"Łódź","venues":["Kościele Wniebowzięcia NMP","Pałacu Poznańskiego","Katedrze Łódzkiej","EC1","Pałacu Herbsta"],
     "venues_short":["Kościół Wniebowzięcia NMP","Pałac Poznańskiego","Katedra Łódzka","EC1 Łódź","Pałac Herbsta"],
     "desc_extra":"miasto przemysłowych pałaców — XIX-wieczne rezydencje fabrykanckie i kościoły Łodzi tworzą nieoczekiwanie eleganckie tło dla muzyki klasycznej"},
    {"slug":"szczecin","name":"Szczecin","lok":"w Szczecinie","gen":"Szczecina","miej":"Szczecinie",
     "region":"Zachodniopomorskie","venues":["Katedrze Świętego Jakuba","Bazylice Świętego Wojciecha","Zamku Książąt Pomorskich","Filharmonii Szczecińskiej","Kościele Świętego Piotra i Pawła"],
     "venues_short":["Katedra Świętego Jakuba","Bazylika Świętego Wojciecha","Zamek Książąt Pomorskich","Filharmonia Szczecińska","Kościół Świętego Piotra"],
     "desc_extra":"miasto nad Odrą z silnymi tradycjami muzycznymi — nowa Filharmonia Szczecińska należy do najpiękniejszych sal koncertowych w Polsce"},
    {"slug":"bydgoszcz","name":"Bydgoszcz","lok":"w Bydgoszczy","gen":"Bydgoszczy","miej":"Bydgoszczy",
     "region":"Kujawy-Pomorze","venues":["Katedrze Bydgoskiej","Kościele Klarysek","Filharmonii Pomorskiej","Operze Nova","Kościele Świętego Andrzeja Boboli"],
     "venues_short":["Katedra Bydgoska","Kościół Klarysek","Filharmonia Pomorska","Opera Nova","Kościół Świętego Andrzeja"],
     "desc_extra":"muzyczne miasto nad Brdą — Filharmonia Pomorska i zabytkowe kościoły Bydgoszczy to przestrzenie z doskonałą akustyką"},
    {"slug":"lublin","name":"Lublin","lok":"w Lublinie","gen":"Lublina","miej":"Lublinie",
     "region":"Lubelszczyzna","venues":["Katedrze Lubelskiej","Kościele Świętego Ducha","Zamku Lubelskim","Centrum Spotkania Kultur","Pałacu Czartoryskich"],
     "venues_short":["Katedra Lubelska","Kościół Świętego Ducha","Zamek Lubelski","Centrum Spotkania Kultur","Pałac Czartoryskich"],
     "desc_extra":"miasto na skrzyżowaniu kultur — historyczny Lublin z gotycką katedrą i renesansowym zamkiem tworzy wyjątkowe tło dla ceremonii ślubnej"},
    {"slug":"katowice","name":"Katowice","lok":"w Katowicach","gen":"Katowic","miej":"Katowicach",
     "region":"Śląsk","venues":["Archikatedrze Chrystusa Króla","Kościele Wniebowzięcia NMP","NOSPR","Pałacu Goldsteinów","MCK Katowice"],
     "venues_short":["Archikatedra Chrystusa Króla","Kościół Wniebowzięcia NMP","NOSPR Katowice","Pałac Goldsteinów","MCK Katowice"],
     "desc_extra":"śląskie miasto z niezwykłą sceną muzyczną — NOSPR i nowoczesne centrum kongresowe sąsiadują z historycznymi kościołami Górnego Śląska"},
    {"slug":"torun","name":"Toruń","lok":"w Toruniu","gen":"Torunia","miej":"Toruniu",
     "region":"Kujawy-Pomorze","venues":["Katedrze Świętych Janów","Kościele Świętego Jakuba","Ratuszu Staromiejskim","Domu Kopernika","Kościele Świętej Marii Magdaleny"],
     "venues_short":["Katedra Świętych Janów","Kościół Świętego Jakuba","Ratusz Staromiejski","Dom Kopernika","Zamek Krzyżacki"],
     "desc_extra":"gotyckie miasto Kopernika — UNESCO World Heritage, gdzie gotyckie kościoły i renesansowy ratusz tworzą jedną z najpiękniejszych scenerii ślubnych w Polsce"},
    {"slug":"rzeszow","name":"Rzeszów","lok":"w Rzeszowie","gen":"Rzeszowa","miej":"Rzeszowie",
     "region":"Podkarpacie","venues":["Katedrze Rzeszowskiej","Kościele Świętego Krzyża","Zamku Lubomirskich","Filharmonii Podkarpackiej","Pałacyku Szefnerów"],
     "venues_short":["Katedra Rzeszowska","Kościół Świętego Krzyża","Zamek Lubomirskich","Filharmonia Podkarpacka","Pałacyk Szefnerów"],
     "desc_extra":"dynamicznie rozwijające się miasto Podkarpacia — zabytkowe kościoły i eleganckie sale recepcyjne Rzeszowa przyciągają pary z całego regionu"},
]


def page(c):
    slug = c["slug"]
    name = c["name"]
    lok  = c["lok"]
    gen  = c["gen"]
    miej = c["miej"]
    region = c["region"]
    venues = c["venues"]
    venues_short = c["venues_short"]
    desc_extra = c["desc_extra"]

    v0, v1 = venues_short[0], venues_short[1]
    venues_cards = "\n".join(
        f'      <div class="venue-card"><div class="venue-name">{v}</div></div>'
        for v in venues_short
    )
    venues_list_str = ", ".join(venues[:3])

    faq_items = [
        (f"Czy Più Mosso gra {lok}?",
         f"Tak — gramy {lok} regularnie. Dojeżdżamy do {gen} z Poznania, a koszt dojazdu ustalamy indywidualnie. Napisz do nas podając datę i miejsce."),
        (f"Jakie miejsca {gen} polecacie na muzykę na żywo?",
         f"Gramy m.in. w {', '.join(venues[:3])} i wielu innych. Najważniejsza jest akustyka — pomożemy ocenić, czy Twoje wymarzone miejsce dobrze brzmi."),
        ("Jakie instrumenty gracie na ślubach?",
         "Najczęściej: skrzypce + organy (do kościoła), skrzypce + fortepian (do sali). Możliwy też skład z wokalem. Dobieramy skład pod konkretne miejsce i charakter uroczystości."),
        (f"Ile kosztuje muzyk na ślub {lok}?",
         f"Cennik ustalamy indywidualnie — zależy od składu, repertuaru i terminu. Napisz do nas podając datę, miejscowość i typ ceremonii, a odpowiemy jeszcze tego samego dnia."),
        ("Jak wcześniej trzeba zarezerwować termin?",
         "Im wcześniej, tym lepiej. Szczyt sezonu (maj–czerwiec, sierpień–wrzesień) rozchodzi się często z kilkumiesięcznym wyprzedzeniem. Sprawdzimy wolny termin od razu po wiadomości."),
    ]
    faq_html = "\n".join(
        f'''    <div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
      <h3 class="faq-q" itemprop="name">{q}</h3>
      <div class="faq-a" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
        <p itemprop="text">{a}</p>
      </div>
    </div>'''
        for q, a in faq_items
    )

    schema = f"""{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "MusicGroup",
      "name": "Più Mosso",
      "url": "https://piumosso.pl/slub/{slug}/",
      "image": "https://piumosso.pl/DSCF3970.jpeg",
      "description": "Muzyk na ślub {lok} — duet skrzypiec i organów/fortepianu",
      "areaServed": {{"@type":"City","name":"{name}"}},
      "genre": ["Classical","Sacred"],
      "member": [
        {{"@type":"Person","name":"Zofia Andersz","instrument":"Skrzypce"}},
        {{"@type":"Person","name":"Piotr Górski","instrument":"Organy, fortepian"}}
      ],
      "contactPoint": {{"@type":"ContactPoint","contactType":"Reservations","email":"kontakt@piumosso.pl"}}
    }},
    {{
      "@type": "FAQPage",
      "mainEntity": [{",".join(
          '{"@type":"Question","name":' + repr(q) + ',"acceptedAnswer":{"@type":"Answer","text":' + repr(a) + '}}'
          for q,a in faq_items
      )}]
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type":"ListItem","position":1,"name":"Strona główna","item":"https://piumosso.pl/"}},
        {{"@type":"ListItem","position":2,"name":"Muzyk na ślub","item":"https://piumosso.pl/slub/"}},
        {{"@type":"ListItem","position":3,"name":"Muzyk na ślub {name}","item":"https://piumosso.pl/slub/{slug}/"}}
      ]
    }}
  ]
}}"""

    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">

<title>Muzyk na ślub {name} — Più Mosso | Skrzypce, organy i fortepian</title>
<meta name="description" content="Muzyk na ślub {lok} — duet Più Mosso. Skrzypce i organy lub fortepian. Gramy w {v0}, {v1} i innych pięknych miejscach {gen}. Zapytaj o wolny termin.">

<link rel="icon" href="../../favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="../../favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="../../apple-touch-icon.png">
<meta name="theme-color" content="#0f0b08">

<meta property="og:type" content="website">
<meta property="og:url" content="https://piumosso.pl/slub/{slug}/">
<meta property="og:title" content="Muzyk na ślub {name} — Più Mosso">
<meta property="og:description" content="Skrzypce i organy na ślub {lok}. Duet Più Mosso — elegancka oprawa ceremonii ślubnej. Gramy {lok} od lat.">
<meta property="og:image" content="https://piumosso.pl/DSCF3970.jpeg">
<meta name="twitter:card" content="summary_large_image">

<link rel="canonical" href="https://piumosso.pl/slub/{slug}/">
<link rel="alternate" hreflang="pl" href="https://piumosso.pl/slub/{slug}/">
<link rel="alternate" hreflang="x-default" href="https://piumosso.pl/slub/{slug}/">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<script type="application/ld+json">
{schema}
</script>

<style>
:root{{
  --bg:#0f0b08;--bg2:#18120d;
  --surf:rgba(30,22,16,.88);--surf2:rgba(25,19,14,.95);
  --ink:#f8f1e5;--muted:rgba(248,241,229,.76);--muted2:rgba(248,241,229,.58);
  --gold:#d7b472;--gold2:#c79c52;
  --line:rgba(215,180,114,.18);--line2:rgba(255,255,255,.06);
  --shadow:0 32px 80px rgba(0,0,0,.44);
  --max:1200px;--r:26px;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth;scroll-padding-top:100px}}
body{{font-family:"Manrope",sans-serif;font-size:17px;line-height:1.72;color:var(--ink);background:radial-gradient(900px 460px at 8% -8%,rgba(215,180,114,.13),transparent 60%),radial-gradient(740px 420px at 100% 8%,rgba(146,104,48,.16),transparent 60%),linear-gradient(180deg,var(--bg2) 0%,var(--bg) 100%);-webkit-font-smoothing:antialiased}}
body::before{{content:"";position:fixed;inset:0;pointer-events:none;opacity:.12;background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);background-size:34px 34px;mask-image:linear-gradient(180deg,rgba(0,0,0,.75),transparent 88%)}}
a{{color:inherit;text-decoration:none;transition:opacity .2s}}
a:hover{{opacity:.7}}
img{{display:block;max-width:100%}}
h1,h2,h3,h4{{font-family:"Cormorant Garamond",serif;font-weight:600;line-height:1.05;letter-spacing:-.01em;color:var(--ink)}}
h1{{font-size:clamp(3.2rem,7vw,6.4rem);line-height:.97}}
h2{{font-size:clamp(2.2rem,4.5vw,4.2rem);line-height:1.0}}
h3{{font-size:clamp(1.4rem,2.5vw,2.2rem)}}
p{{color:var(--muted)}}
strong{{color:var(--ink)}}
.wrap{{width:min(calc(100% - 48px),var(--max));margin:0 auto}}
.eyebrow{{display:inline-flex;align-items:center;gap:14px;font-size:.72rem;letter-spacing:.28em;text-transform:uppercase;color:var(--muted2);font-family:"Manrope",sans-serif;font-weight:600}}
.eyebrow::before{{content:"";width:38px;height:1px;background:var(--gold);opacity:.6}}
.rule{{width:100%;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);opacity:.22}}
/* NAV */
nav{{position:fixed;top:0;inset:0 0 auto 0;z-index:60;padding:20px 24px;background:rgba(15,11,8,.72);backdrop-filter:blur(18px);border-bottom:1px solid transparent;transition:background .3s,border-color .3s}}
nav.scrolled{{background:rgba(15,11,8,.92);border-bottom:1px solid rgba(215,180,114,.12);padding:14px 24px}}
.nav-inner{{max-width:var(--max);margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:20px}}
.nav-brand{{display:flex;flex-direction:column;gap:5px}}
.nav-brand span{{font-size:.62rem;letter-spacing:.22em;text-transform:uppercase;color:var(--muted2);font-weight:600;white-space:nowrap}}
.nav-brand strong{{font-family:"Cormorant Garamond",serif;font-size:1.55rem;font-weight:600;letter-spacing:.04em;color:var(--ink);line-height:1}}
.nav-links{{display:flex;align-items:center;gap:26px}}
.nav-links a{{font-size:.85rem;font-weight:600;letter-spacing:.04em;color:var(--muted)}}
.nav-links a.cta{{padding:10px 20px;border:1px solid var(--line);border-radius:999px;color:var(--gold);background:rgba(212,176,106,.06)}}
.nav-links a.cta:hover{{background:rgba(212,176,106,.12);opacity:1}}
.nav-toggle{{display:none;width:44px;height:44px;background:none;border:1px solid var(--line2);border-radius:10px;cursor:pointer;color:var(--ink);flex-direction:column;align-items:center;justify-content:center;gap:5px}}
.nav-toggle span{{display:block;width:18px;height:1.5px;background:currentColor;border-radius:2px}}
/* HERO */
.city-hero{{min-height:78vh;display:flex;align-items:center;padding:clamp(120px,18vh,180px) 0 clamp(60px,8vh,100px);position:relative;overflow:hidden}}
.city-hero::before{{content:"";position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 20% 50%,rgba(215,180,114,.07),transparent 60%),radial-gradient(ellipse 60% 80% at 85% 20%,rgba(146,104,48,.09),transparent 55%);pointer-events:none}}
.city-hero .eyebrow{{color:var(--gold);margin-bottom:20px;display:block}}
.city-hero h1{{margin-bottom:clamp(18px,3vh,28px);max-width:18ch}}
.city-hero .hero-sub{{max-width:56ch;font-size:1.05rem;color:var(--muted);margin-bottom:clamp(24px,4vh,40px);line-height:1.65}}
.hero-actions{{display:flex;flex-wrap:wrap;gap:14px;align-items:center}}
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:52px;padding:0 28px;border-radius:999px;font-size:.88rem;font-weight:700;letter-spacing:.04em;border:1px solid transparent;transition:opacity .2s,transform .15s}}
.btn:hover{{opacity:.85;transform:translateY(-1px)}}
.btn-gold{{background:linear-gradient(160deg,#e4c98a,var(--gold));color:#1a130a;box-shadow:0 12px 32px rgba(212,176,106,.24)}}
.btn-ghost{{background:rgba(255,255,255,.04);border-color:rgba(212,176,106,.22);color:var(--ink)}}
/* SECTIONS */
section{{padding:clamp(72px,10vw,140px) 0;position:relative}}
.section-head{{margin-bottom:clamp(36px,5vw,64px)}}
.section-head .eyebrow{{margin-bottom:18px}}
.section-head h2{{max-width:22ch}}
.section-head p{{max-width:56ch;margin-top:16px;font-size:1.02rem}}
/* VENUES */
.venues-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:2px;margin-top:8px}}
.venue-card{{background:var(--surf);border:1px solid var(--line);padding:22px 24px;border-radius:0}}
.venue-card:first-child{{border-radius:var(--r) 0 0 var(--r)}}
.venue-card:last-child{{border-radius:0 var(--r) var(--r) 0}}
.venue-name{{font-family:"Cormorant Garamond",serif;font-size:1.05rem;font-weight:600;color:var(--ink);line-height:1.3}}
/* OFFER */
.offer-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:2px}}
.offer-card{{background:var(--surf);border:1px solid var(--line);padding:clamp(28px,4vw,46px)}}
.offer-card:first-child{{border-radius:var(--r) 0 0 var(--r);border-right:none}}
.offer-card:last-child{{border-radius:0 var(--r) var(--r) 0;border-left:none}}
.offer-card:nth-child(2){{border-left:none;border-right:none}}
.offer-tag{{font-size:.67rem;letter-spacing:.24em;text-transform:uppercase;color:var(--gold);font-weight:700;margin-bottom:16px}}
.offer-card h3{{font-size:clamp(1.3rem,2vw,1.8rem);margin-bottom:14px}}
.offer-card p{{font-size:.95rem;margin-bottom:18px}}
.offer-list{{list-style:none;display:grid;gap:10px}}
.offer-list li{{position:relative;padding-left:16px;font-size:.9rem;color:var(--muted)}}
.offer-list li::before{{content:"";position:absolute;left:0;top:.72em;width:5px;height:5px;border-radius:50%;background:var(--gold);opacity:.6}}
.offer-cta{{display:inline-flex;align-items:center;gap:6px;margin-top:24px;font-size:.8rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:2px;transition:color .2s,border-color .2s}}
.offer-cta:hover{{color:var(--gold);border-color:var(--gold);opacity:1}}
/* WHY */
.why-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:2px}}
.why-card{{background:var(--surf);border:1px solid var(--line);padding:clamp(24px,3.5vw,40px)}}
.why-card:first-child{{border-right:none;border-radius:var(--r) 0 0 var(--r)}}
.why-card:last-child{{border-left:none;border-radius:0 var(--r) var(--r) 0}}
.why-card:nth-child(2),.why-card:nth-child(3){{border-left:none;border-right:none}}
.why-icon{{font-size:2rem;margin-bottom:14px;line-height:1}}
.why-card h3{{font-size:1.2rem;margin-bottom:10px}}
.why-card p{{font-size:.9rem}}
/* FAQ */
.faq-list{{display:grid;gap:3px;margin-top:8px}}
.faq-item{{background:var(--surf);border:1px solid var(--line);padding:clamp(20px,3vw,36px)}}
.faq-item:first-child{{border-radius:var(--r) var(--r) 0 0}}
.faq-item:last-child{{border-radius:0 0 var(--r) var(--r)}}
.faq-q{{font-size:clamp(1rem,1.6vw,1.28rem);margin-bottom:12px;color:var(--ink)}}
.faq-a p{{font-size:.95rem}}
/* CONTACT */
.contact-grid{{display:grid;grid-template-columns:1fr 1fr;gap:2px}}
.contact-copy{{background:var(--surf);border:1px solid var(--line);border-right:none;border-radius:var(--r) 0 0 var(--r);padding:clamp(36px,5vw,64px)}}
.contact-copy h2{{font-size:clamp(1.8rem,3.5vw,3.2rem);margin:18px 0 18px;max-width:18ch}}
.contact-copy p{{font-size:.97rem;max-width:46ch}}
.contact-direct{{margin-top:28px;display:flex;flex-direction:column;gap:12px}}
.contact-direct a{{display:inline-flex;align-items:center;gap:10px;font-size:.92rem;color:var(--ink);border-bottom:1px solid var(--line);padding-bottom:4px;width:fit-content}}
.contact-direct a:hover{{border-color:var(--gold);color:var(--gold);opacity:1}}
.contact-form-wrap{{background:var(--surf2);border:1px solid var(--line);border-left:none;border-radius:0 var(--r) var(--r) 0;padding:clamp(36px,5vw,64px)}}
.contact-form-wrap h3{{font-size:1.7rem;margin-bottom:24px}}
form{{display:grid;gap:14px}}
label{{display:grid;gap:6px;font-size:.82rem;color:var(--muted2);letter-spacing:.04em;font-weight:600}}
input,select,textarea{{width:100%;padding:14px 16px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:12px;color:var(--ink);font-size:.95rem;font-family:"Manrope",sans-serif;transition:border-color .2s,box-shadow .2s}}
input::placeholder,textarea::placeholder{{color:rgba(248,241,229,.28)}}
select option{{background:#1a130a}}
input:focus,select:focus,textarea:focus{{outline:none;border-color:rgba(212,176,106,.4);box-shadow:0 0 0 4px rgba(212,176,106,.08)}}
textarea{{resize:vertical;min-height:110px}}
button[type="submit"]{{appearance:none;border:0;cursor:pointer;margin-top:4px}}
.form-success{{padding:28px 20px;text-align:center;color:var(--ink);font-size:1.05rem;line-height:1.6;border:1px solid var(--gold);border-radius:var(--r)}}
.form-success strong{{display:block;font-size:1.18rem;color:var(--gold);margin-bottom:8px}}
.form-note{{margin-top:12px;font-size:.8rem;color:var(--muted2)}}
/* NL */
.nl-section{{padding:clamp(40px,5vw,72px) 0;background:rgba(30,22,16,.5);border-top:1px solid var(--line)}}
.nl-inner{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:24px}}
.nl-text{{flex:1;min-width:200px}}
.nl-title{{font-family:"Cormorant Garamond",serif;font-size:clamp(1.2rem,2.5vw,1.6rem);font-weight:600;color:var(--ink);margin:0 0 6px}}
.nl-sub{{font-size:.85rem;color:var(--muted2);margin:0}}
.nl-form{{display:flex;gap:8px;flex-wrap:wrap;flex:1;min-width:260px;max-width:420px}}
.nl-input{{flex:1;min-width:0;padding:11px 14px;border:1px solid var(--line);border-radius:4px;font-size:.88rem;background:rgba(255,255,255,.04);color:var(--ink);outline:none;font-family:inherit}}
.nl-input:focus{{border-color:var(--gold)}}
.nl-btn{{padding:11px 22px;background:var(--gold);color:#1a130a;border:none;border-radius:4px;font-size:.85rem;font-weight:700;letter-spacing:.06em;cursor:pointer;font-family:inherit;transition:opacity .15s;white-space:nowrap}}
.nl-btn:hover{{opacity:.85}}.nl-btn:disabled{{opacity:.5;cursor:default}}
.nl-msg{{font-size:.83rem;margin:0}}
.nl-msg.ok{{color:#6db88a}}.nl-msg.err{{color:#e07070}}
/* FOOTER */
footer{{padding:clamp(28px,4vw,52px) 0;border-top:1px solid var(--line)}}
.footer-inner{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px}}
.footer-brand{{font-family:"Cormorant Garamond",serif;font-size:1.28rem;font-weight:600;color:var(--muted2);letter-spacing:.06em}}
.footer-links{{display:flex;gap:22px;flex-wrap:wrap}}
.footer-links a{{font-size:.8rem;color:var(--muted2);letter-spacing:.06em}}
.footer-copy{{font-size:.78rem;color:var(--muted2);opacity:.6}}
/* RESPONSIVE */
@media(max-width:900px){{
  .offer-grid,.why-grid{{grid-template-columns:1fr}}
  .offer-card,.why-card{{border-radius:var(--r)!important;border:1px solid var(--line)!important}}
  .contact-grid{{grid-template-columns:1fr}}
  .contact-copy{{border-right:1px solid var(--line);border-radius:var(--r) var(--r) 0 0!important}}
  .contact-form-wrap{{border-left:1px solid var(--line);border-radius:0 0 var(--r) var(--r)!important}}
  .nav-links{{display:none}}
  .nav-toggle{{display:flex}}
  .venues-grid{{grid-template-columns:1fr 1fr}}
  .venue-card{{border-radius:0!important}}
}}
@media(max-width:600px){{
  .venues-grid{{grid-template-columns:1fr}}
  .venue-card:first-child{{border-radius:var(--r) var(--r) 0 0!important}}
  .venue-card:last-child{{border-radius:0 0 var(--r) var(--r)!important}}
}}
</style>
</head>
<body>

<nav id="nav">
  <div class="nav-inner">
    <a href="../../" class="nav-brand">
      <span>Skrzypce · Organy · Fortepian</span>
      <strong>Più Mosso</strong>
    </a>
    <div class="nav-links">
      <a href="../../#oferta">Oferta</a>
      <a href="../../kalendarium/">Kalendarium</a>
      <a href="../../press/">Press kit</a>
      <a href="#kontakt" class="cta">Zapytaj o termin</a>
    </div>
    <button class="nav-toggle" id="navToggle" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</nav>

<!-- HERO -->
<header class="city-hero">
  <div class="wrap">
    <span class="eyebrow">{region} · Oprawa muzyczna ślubu</span>
    <h1>Muzyk na ślub<br>{name}</h1>
    <p class="hero-sub">Skrzypce i organy — elegancka oprawa ceremonii ślubnej {lok}. Gramy w {venues_short[0]}, {venues_short[1]} i wszędzie tam, gdzie muzyka ma znaczenie.</p>
    <div class="hero-actions">
      <a href="#kontakt" class="btn btn-gold">Zapytaj o termin</a>
      <a href="../../wedding-offer-pl.pdf" target="_blank" rel="noopener" class="btn btn-ghost">Oferta PDF</a>
    </div>
  </div>
</header>

<div class="rule"></div>

<!-- LOKALNA SEKCJA -->
<section>
  <div class="wrap">
    <div class="section-head">
      <div class="eyebrow">Oprawa ślubna {gen}</div>
      <h2>Gramy {lok}.</h2>
      <p>Duet Più Mosso regularnie gra na ślubach i wydarzeniach kulturalnych {lok} — {desc_extra}. Repertuar i skład dobieramy pod konkretną przestrzeń i akustykę.</p>
    </div>
    <div class="venues-grid">
{venues_cards}
    </div>
  </div>
</section>

<div class="rule"></div>

<!-- OFERTA -->
<section id="oferta">
  <div class="wrap">
    <div class="section-head">
      <div class="eyebrow">Oferta ślubna</div>
      <h2>Co gramy i dla kogo.</h2>
      <p>Gramy na uroczystościach kościelnych i cywilnych {lok}. W obu przypadkach: z pełnym przygotowaniem i bez szablonowych programów.</p>
    </div>
    <div class="offer-grid">
      <article class="offer-card">
        <div class="offer-tag">Kościoły</div>
        <h3>Skrzypce i organy</h3>
        <p>Klasyczny skład na uroczystości kościelne — bogata akustyka kościelnych organów i skrzypiec.</p>
        <ul class="offer-list">
          <li>uroczystości kościelne w {miej}</li>
          <li>muzyka liturgiczna i artystyczna</li>
          <li>od baroku po współczesność</li>
        </ul>
        <a class="offer-cta" href="../../wedding-offer-pl.pdf" target="_blank" rel="noopener">Oferta ślubna PDF →</a>
      </article>
      <article class="offer-card">
        <div class="offer-tag">Sale i plenery</div>
        <h3>Skrzypce i fortepian</h3>
        <p>Elegancki duet do sal recepcyjnych, pałaców i przestrzeni plenerowych {gen}.</p>
        <ul class="offer-list">
          <li>śluby cywilne i ceremonie plenerowe</li>
          <li>uczty weselne i przyjęcia</li>
          <li>muzyka tła i recitale</li>
        </ul>
        <a class="offer-cta" href="../../wedding-offer-pl.pdf" target="_blank" rel="noopener">Oferta ślubna PDF →</a>
      </article>
      <article class="offer-card">
        <div class="offer-tag">Z wokalem</div>
        <h3>Duet z solistką</h3>
        <p>Skrzypce, organy/fortepian i śpiew — dla par szukających pełniejszego brzmienia.</p>
        <ul class="offer-list">
          <li>większa paleta repertuarowa</li>
          <li>bardziej rozbudowana dramaturgia ceremonii</li>
          <li>spójna forma od początku do końca</li>
        </ul>
        <a class="offer-cta" href="../../guest-vocal-offer.pdf" target="_blank" rel="noopener">Zobacz PDF →</a>
      </article>
    </div>
  </div>
</section>

<div class="rule"></div>

<!-- DLACZEGO MY -->
<section>
  <div class="wrap">
    <div class="section-head">
      <div class="eyebrow">Dlaczego Più Mosso</div>
      <h2>Muzyka, która pracuje na ceremonię.</h2>
    </div>
    <div class="why-grid">
      <article class="why-card">
        <div class="why-icon">🎻</div>
        <h3>Doświadczenie sceniczne</h3>
        <p>Gramy na ślubach, festiwalach i w instytucjach kultury od lat. Znamy różne przestrzenie i akustyki.</p>
      </article>
      <article class="why-card">
        <div class="why-icon">🏆</div>
        <h3>Nagrody konkursowe</h3>
        <p>I miejsce Concorso Internazionale 2025, III miejsce Ogólnopolski Konkurs Muzyczny Rumia 2024.</p>
      </article>
      <article class="why-card">
        <div class="why-icon">🎼</div>
        <h3>Repertuar na miarę</h3>
        <p>Od baroku po jazz i film. Pomagamy w wyborze muzyki i dostosowujemy program do charakteru ceremonii.</p>
      </article>
      <article class="why-card">
        <div class="why-icon">📍</div>
        <h3>Dojeżdżamy {lok}</h3>
        <p>Punktualność i spokojna realizacja są dla nas standardem. Dojazd do {gen} wliczamy do wyceny.</p>
      </article>
    </div>
  </div>
</section>

<div class="rule"></div>

<!-- FAQ -->
<section itemscope itemtype="https://schema.org/FAQPage">
  <div class="wrap">
    <div class="section-head">
      <div class="eyebrow">Pytania i odpowiedzi</div>
      <h2>FAQ — muzyk na ślub {name}.</h2>
    </div>
    <div class="faq-list">
{faq_html}
    </div>
  </div>
</section>

<div class="rule"></div>

<!-- KONTAKT -->
<section id="kontakt">
  <div class="wrap">
    <div class="contact-grid">
      <div class="contact-copy">
        <div class="eyebrow">Kontakt</div>
        <h2>Zapytaj o wolny termin {lok}.</h2>
        <p>Napisz datę ślubu, miejscowość i typ ceremonii — odpowiemy jeszcze tego samego dnia z informacją o dostępności i orientacyjną wyceną.</p>
        <div class="contact-direct">
          <a href="mailto:kontakt@piumosso.pl">✉ kontakt@piumosso.pl</a>
          <a href="tel:+48781010229">☎ +48 781 010 229</a>
          <a href="../../press/">📄 Press kit</a>
        </div>
      </div>
      <div class="contact-form-wrap">
        <h3>Formularz kontaktowy</h3>
        <form id="contact-form">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
            <label>Imię i nazwisko *<input name="name" required placeholder="Anna Kowalska"></label>
            <label>Telefon *<input name="phone" type="tel" required placeholder="+48 600 000 000"></label>
          </div>
          <label>E-mail<input name="email" type="email" placeholder="anna@email.pl"></label>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
            <label>Data ślubu<input name="eventDate" type="date"></label>
            <label>Typ ceremonii
              <select name="eventType">
                <option value="">Wybierz…</option>
                <option value="kościelna">Uroczystość kościelna</option>
                <option value="cywilna">Uroczystość cywilna</option>
                <option value="plenerowa">Ceremonia plenerowa</option>
                <option value="inne">Inne</option>
              </select>
            </label>
          </div>
          <label>Kościół / miejsce<input name="city" placeholder="np. Katedra Świętego Jana, {name}"></label>
          <label>Wiadomość<textarea name="message" placeholder="Czego szukacie? Ile gości? Jakiego repertuaru?"></textarea></label>
          <button type="submit" class="btn btn-gold" style="width:100%">Wyślij zapytanie</button>
        </form>
        <p class="form-note">Zazwyczaj odpowiadamy jeszcze tego samego dnia.</p>
      </div>
    </div>
  </div>
</section>

<!-- NEWSLETTER -->
<section class="nl-section" id="newsletter">
  <div class="wrap">
    <div class="nl-inner">
      <div class="nl-text">
        <h2 class="nl-title">Bądź na bieżąco</h2>
        <p class="nl-sub">Koncerty, nagrania i kulisy — kilka razy w roku, bez spamu.</p>
      </div>
      <form class="nl-form" id="nlForm" novalidate>
        <input type="email" id="nlEmail" name="email" placeholder="twój@email.pl" autocomplete="email" required class="nl-input">
        <button type="submit" class="nl-btn">Zapisz się</button>
      </form>
      <p id="nlMsg" class="nl-msg" style="display:none"></p>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <div class="footer-inner">
      <div class="footer-brand">Più Mosso</div>
      <nav class="footer-links" aria-label="Stopka">
        <a href="../../">Strona główna</a>
        <a href="../../kalendarium/">Kalendarium</a>
        <a href="../../press/">Press kit</a>
        <a href="../../galeria/">Galeria</a>
        <a href="../../#kontakt">Kontakt</a>
      </nav>
      <span class="footer-copy">&copy; 2026 Più Mosso</span>
    </div>
  </div>
</footer>

<script>
// Nav scroll
window.addEventListener("scroll", () => {{
  document.getElementById("nav").classList.toggle("scrolled", scrollY > 40);
}}, {{passive:true}});

// Contact form
const FORM_WORKER_URL = "https://form-handler.pietrek517.workers.dev";
const form = document.getElementById("contact-form");
if (form) {{
  form.addEventListener("submit", async e => {{
    e.preventDefault();
    const fd = new FormData(form);
    const name  = fd.get("name")?.trim();
    const phone = fd.get("phone")?.trim();
    if (!name || !phone) {{ alert("Podaj imię i numer telefonu."); return; }}
    const submitBtn = form.querySelector("button[type='submit']");
    submitBtn.disabled = true;
    submitBtn.textContent = "Wysyłanie…";
    try {{
      const res = await fetch(FORM_WORKER_URL, {{
        method:"POST",
        headers:{{"Content-Type":"application/json"}},
        body: JSON.stringify({{
          name, phone,
          email:     (fd.get("email")||"").trim(),
          eventType: (fd.get("eventType")||"").trim(),
          city:      (fd.get("city")||"").trim(),
          eventDate: (fd.get("eventDate")||"").trim(),
          message:   (fd.get("message")||"").trim(),
          scope:     "ślub",
        }}),
      }});
      const data = await res.json().catch(() => ({{}}));
      if (res.ok && data.ok) {{
        form.innerHTML = `<div class="form-success"><strong>Wiadomość wysłana.</strong><br>Zazwyczaj odpowiadamy jeszcze tego samego dnia.</div>`;
      }} else throw new Error(data.error || res.status);
    }} catch (err) {{
      const body = encodeURIComponent(`Imię: ${{name}}\\nTelefon: ${{phone}}\\nMiejsce ślubu: {name}\\nData: ${{fd.get("eventDate")||"–"}}\\nTyp: ${{fd.get("eventType")||"–"}}\\nWiadomość: ${{fd.get("message")||"–"}}`);
      submitBtn.disabled = false;
      submitBtn.textContent = "Wyślij zapytanie";
      location.href = `mailto:kontakt@piumosso.pl?subject=Zapytanie%20o%20ślub%20{name}&body=${{body}}`;
    }}
  }});
}}

// Newsletter
const NL_TOKEN = {NL_TOKEN_JS};
const NL_DISPATCH = "https://api.github.com/repos/Piotr-piumosso/piumosso-engine/dispatches";
const nlForm = document.getElementById("nlForm");
const nlMsg  = document.getElementById("nlMsg");
if (nlForm) {{
  nlForm.addEventListener("submit", async e => {{
    e.preventDefault();
    const email = document.getElementById("nlEmail").value.trim();
    if (!email) return;
    const btn = nlForm.querySelector("button");
    btn.disabled = true; btn.textContent = "…";
    try {{
      const res = await fetch(NL_DISPATCH, {{
        method:"POST",
        headers:{{"Authorization":`Bearer ${{NL_TOKEN}}`,"Accept":"application/vnd.github+json","Content-Type":"application/json"}},
        body: JSON.stringify({{event_type:"newsletter-subscribe",client_payload:{{email,lang:"pl",source:"slub-{slug}"}}}}),
      }});
      if (res.status === 204) {{
        nlForm.style.display = "none";
        nlMsg.textContent = "Zapisano! Dziękujemy.";
        nlMsg.className = "nl-msg ok"; nlMsg.style.display = "block";
      }} else throw new Error();
    }} catch {{
      nlMsg.textContent = "Coś poszło nie tak. Napisz na kontakt@piumosso.pl.";
      nlMsg.className = "nl-msg err"; nlMsg.style.display = "block";
      btn.disabled = false; btn.textContent = "Zapisz się";
    }}
  }});
}}
</script>
</body>
</html>"""


def main():
    for c in CITIES:
        out_dir = SLUB / c["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        html = page(c)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"  ✓ slub/{c['slug']}/index.html ({len(html)//1024}KB)")

    # Index page for /slub/
    cities_links = "\n".join(
        f'      <li><a href="{c["slug"]}/" class="city-link">Muzyk na ślub {c["name"]} <span class="city-region">{c["region"]}</span></a></li>'
        for c in CITIES
    )
    index_html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Muzyk na ślub — Più Mosso | Polska</title>
<meta name="description" content="Duet Più Mosso — muzyk na ślub w całej Polsce. Skrzypce i organy lub fortepian. Wybierz swoje miasto.">
<link rel="canonical" href="https://piumosso.pl/slub/">
<link rel="icon" href="../favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0f0b08;--bg2:#18120d;--surf:rgba(30,22,16,.88);--ink:#f8f1e5;--muted:rgba(248,241,229,.76);--muted2:rgba(248,241,229,.58);--gold:#d7b472;--line:rgba(215,180,114,.18);--max:1200px;--r:26px}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:"Manrope",sans-serif;font-size:17px;line-height:1.72;color:var(--ink);background:linear-gradient(180deg,var(--bg2) 0%,var(--bg) 100%);min-height:100vh;-webkit-font-smoothing:antialiased}}
.wrap{{width:min(calc(100% - 48px),var(--max));margin:0 auto}}
h1,h2{{font-family:"Cormorant Garamond",serif;font-weight:600;color:var(--ink)}}
h1{{font-size:clamp(2.8rem,6vw,5rem);line-height:1.0;margin-bottom:18px}}
p{{color:var(--muted)}}
a{{color:inherit;text-decoration:none}}
nav{{padding:20px 24px;background:rgba(15,11,8,.8)}}
.nav-inner{{max-width:var(--max);margin:0 auto;display:flex;align-items:center;justify-content:space-between}}
.nav-brand strong{{font-family:"Cormorant Garamond",serif;font-size:1.4rem;font-weight:600;color:var(--ink)}}
.nav-back{{font-size:.82rem;color:var(--muted);font-weight:600}}
.hero{{padding:clamp(80px,12vw,140px) 0 clamp(40px,6vw,80px)}}
.eyebrow{{display:inline-flex;align-items:center;gap:14px;font-size:.72rem;letter-spacing:.28em;text-transform:uppercase;color:var(--muted2);font-family:"Manrope",sans-serif;font-weight:600;margin-bottom:20px}}
.eyebrow::before{{content:"";width:38px;height:1px;background:var(--gold);opacity:.6}}
.city-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:2px;margin-top:48px}}
.city-link{{display:flex;align-items:center;justify-content:space-between;background:var(--surf);border:1px solid var(--line);padding:22px 28px;transition:border-color .2s,background .2s;font-size:1.05rem;font-weight:600;color:var(--ink)}}
.city-link:hover{{border-color:var(--gold);background:rgba(215,180,114,.06);opacity:1}}
.city-region{{font-size:.75rem;color:var(--gold);font-weight:600;letter-spacing:.1em;text-transform:uppercase}}
footer{{padding:32px 0;border-top:1px solid var(--line);margin-top:80px;text-align:center;font-size:.8rem;color:var(--muted2)}}
</style>
</head>
<body>
<nav><div class="nav-inner"><a href="../" class="nav-brand"><strong>Più Mosso</strong></a><a href="../" class="nav-back">← Strona główna</a></div></nav>
<div class="hero wrap">
  <div class="eyebrow">Oprawa muzyczna ślubu</div>
  <h1>Muzyk na ślub<br>w Polsce.</h1>
  <p style="max-width:54ch;font-size:1.02rem">Duet Più Mosso — skrzypce i organy lub fortepian. Gramy na uroczystościach ślubnych w całej Polsce. Wybierz swoje miasto:</p>
  <ul class="city-grid" style="list-style:none">
{cities_links}
  </ul>
</div>
<footer>&copy; 2026 Più Mosso · <a href="../">piumosso.pl</a></footer>
</body>
</html>"""
    (SLUB / "index.html").write_text(index_html, encoding="utf-8")
    print(f"  ✓ slub/index.html")
    print(f"\nWygenerowano {len(CITIES)} stron + 1 index.")

if __name__ == "__main__":
    main()
