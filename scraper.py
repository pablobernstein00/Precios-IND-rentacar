#!/usr/bin/env python3
"""
Scraper de precios - Industria Arriendo de Autos Chile
Inteligencia competitiva para Econorent
Reserva: 1 semana de duración, fecha inicio = 1 mes desde hoy
Empresas: Econorent, Salfarent, Mitta, Gama, Avis, Sixt, Chilean
"""

import json, os, re, time, random
from datetime import datetime, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ── Fechas ────────────────────────────────────────────────────────
def get_dates():
    pickup  = datetime.now() + timedelta(days=30)
    dropoff = pickup + timedelta(days=7)
    return pickup, dropoff

# ── Ciudades ──────────────────────────────────────────────────────
CIUDADES = [
    {"nombre":"Arica",          "region":"Arica y Parinacota"},
    {"nombre":"Iquique",        "region":"Tarapacá"},
    {"nombre":"Calama",         "region":"Antofagasta"},
    {"nombre":"Antofagasta",    "region":"Antofagasta"},
    {"nombre":"Copiapó",        "region":"Atacama"},
    {"nombre":"La Serena",      "region":"Coquimbo"},
    {"nombre":"Viña del Mar",   "region":"Valparaíso"},
    {"nombre":"Santiago",       "region":"Metropolitana"},
    {"nombre":"Rancagua",       "region":"O'Higgins"},
    {"nombre":"Los Ángeles",    "region":"Biobío"},
    {"nombre":"Concepción",     "region":"Biobío"},
    {"nombre":"Temuco",         "region":"Araucanía"},
    {"nombre":"Valdivia",       "region":"Los Ríos"},
    {"nombre":"Puerto Montt",   "region":"Los Lagos"},
    {"nombre":"Coyhaique",      "region":"Aysén"},
    {"nombre":"Puerto Natales", "region":"Magallanes"},
    {"nombre":"Punta Arenas",   "region":"Magallanes"},
]

CATEGORIAS = ["Económico","Compacto","Intermedio","SUV","Premium","Pickup"]

CAT_KEYWORDS = {
    "Económico":  ["econom","mini","small","básic","basic","city"],
    "Compacto":   ["compact","compacto"],
    "Intermedio": ["intermedio","intermediate","medium","sedan","mediano","standard"],
    "SUV":        ["suv","4x4","crossover","todoterreno","todo terreno","jeep"],
    "Premium":    ["premium","luxury","lujo","ejecutivo","full","executive"],
    "Pickup":     ["pickup","pick-up","hilux","ranger","navara","l200","d-max","camioneta"],
}

def guess_category(text):
    t = text.lower()
    for cat, keywords in CAT_KEYWORDS.items():
        if any(k in t for k in keywords):
            return cat
    return "Intermedio"

def clean_price(text):
    """Extrae número entero de un string de precio en CLP"""
    nums = re.sub(r"[^\d]", "", str(text))
    val = int(nums) if nums else 0
    # Filtro: precios razonables para Chile (5.000 a 300.000 CLP/día)
    return val if 5000 < val < 300000 else 0

def pause():
    time.sleep(random.uniform(2.5, 5.0))

# ── Scrapers por empresa ──────────────────────────────────────────

def scrape_econorent(ciudad, pickup, dropoff, page):
    """econorent.cl — formulario de búsqueda"""
    results = []
    try:
        url = "https://www.econorent.cl/reservas"
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=20000)

        # Seleccionar ciudad pickup
        city_input = page.locator("input[placeholder*='ciudad'], input[placeholder*='Ciudad'], select[name*='ciudad'], select[name*='sucursal']").first
        city_input.click()
        page.wait_for_timeout(500)
        page.keyboard.type(ciudad)
        page.wait_for_timeout(1000)

        # Seleccionar opción del dropdown
        option = page.locator(f"text={ciudad}").first
        if option.is_visible():
            option.click()

        # Fechas
        pu_str = pickup.strftime("%d/%m/%Y")
        do_str = dropoff.strftime("%d/%m/%Y")
        date_inputs = page.locator("input[type='text'][placeholder*='fecha'], input[class*='date'], input[name*='fecha']")
        if date_inputs.count() >= 2:
            date_inputs.nth(0).fill(pu_str)
            date_inputs.nth(1).fill(do_str)

        # Buscar
        page.locator("button[type='submit'], button:has-text('Buscar'), button:has-text('Ver')").first.click()
        page.wait_for_load_state("networkidle", timeout=25000)
        page.wait_for_timeout(2000)

        html = page.content()
        results = parse_generic_results(html, "Econorent", ciudad)

    except Exception as e:
        print(f"  [Econorent/{ciudad}] Error: {e}")
    return results


def scrape_salfarent(ciudad, pickup, dropoff, page):
    """salfarent.cl"""
    results = []
    try:
        pu = pickup.strftime("%Y-%m-%d")
        do = dropoff.strftime("%Y-%m-%d")
        url = f"https://www.salfarent.cl/reserva?ciudad={ciudad}&fechaInicio={pu}&fechaFin={do}"
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=25000)
        page.wait_for_timeout(2000)
        html = page.content()
        results = parse_generic_results(html, "Salfarent", ciudad)
    except Exception as e:
        print(f"  [Salfarent/{ciudad}] Error: {e}")
    return results


def scrape_mitta(ciudad, pickup, dropoff, page):
    """mitta.cl"""
    results = []
    try:
        pu = pickup.strftime("%d-%m-%Y")
        do = dropoff.strftime("%d-%m-%Y")
        url = f"https://www.mitta.cl/arriendo?ciudad={ciudad}&desde={pu}&hasta={do}"
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=25000)
        page.wait_for_timeout(3000)
        html = page.content()
        results = parse_generic_results(html, "Mitta", ciudad)
    except Exception as e:
        print(f"  [Mitta/{ciudad}] Error: {e}")
    return results


def scrape_gama(ciudad, pickup, dropoff, page):
    """gamarent.cl"""
    results = []
    try:
        pu = pickup.strftime("%d/%m/%Y")
        do = dropoff.strftime("%d/%m/%Y")
        url = "https://www.gamarent.cl/reservar"
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=20000)

        # Intentar llenar formulario
        try:
            page.select_option("select[name*='ciudad'], select[name*='oficina']", label=ciudad)
            page.fill("input[name*='inicio'], input[placeholder*='retiro']", pu)
            page.fill("input[name*='fin'], input[placeholder*='devolucion']", do)
            page.locator("button[type='submit'], input[type='submit']").first.click()
            page.wait_for_load_state("networkidle", timeout=25000)
            page.wait_for_timeout(2000)
        except:
            pass

        html = page.content()
        results = parse_generic_results(html, "Gama", ciudad)
    except Exception as e:
        print(f"  [Gama/{ciudad}] Error: {e}")
    return results


def scrape_avis(ciudad, pickup, dropoff, page):
    """avis.cl — usa API de Avis latinoamérica"""
    results = []
    try:
        pu = pickup.strftime("%m/%d/%Y")
        do = dropoff.strftime("%m/%d/%Y")
        city_codes = {
            "Santiago":"SCL","Antofagasta":"ANF","Punta Arenas":"PUQ",
            "Puerto Montt":"PMC","Concepción":"CCP","Iquique":"IQQ",
            "Arica":"ARI","La Serena":"LSC","Temuco":"ZCO","Calama":"CJC",
        }
        code = city_codes.get(ciudad)
        if not code:
            return results
        url = f"https://www.avis.cl/en/car-hire/results?PD={code}&DD={code}&PDT={pu}T10%3A00&DDT={do}T10%3A00&ACRISS=&SEL=S"
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        html = page.content()
        results = parse_generic_results(html, "Avis", ciudad)
    except Exception as e:
        print(f"  [Avis/{ciudad}] Error: {e}")
    return results


def scrape_sixt(ciudad, pickup, dropoff, page):
    """sixt.cl"""
    results = []
    city_map = {
        "Santiago":"santiago-aeropuerto","Antofagasta":"antofagasta",
        "Punta Arenas":"punta-arenas","Puerto Montt":"puerto-montt",
        "Concepción":"concepcion","Iquique":"iquique",
    }
    city_slug = city_map.get(ciudad)
    if not city_slug:
        return results
    try:
        pu = pickup.strftime("%Y-%m-%dT10:00:00")
        do = dropoff.strftime("%Y-%m-%dT10:00:00")
        url = f"https://www.sixt.cl/rent-a-car/chile/{city_slug}?dateFrom={pu}&dateTo={do}"
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)
        page.wait_for_timeout(4000)
        html = page.content()
        results = parse_generic_results(html, "Sixt", ciudad)
    except Exception as e:
        print(f"  [Sixt/{ciudad}] Error: {e}")
    return results


def scrape_chilean(ciudad, pickup, dropoff, page):
    """chileanrent.cl"""
    results = []
    try:
        pu = pickup.strftime("%d/%m/%Y")
        do = dropoff.strftime("%d/%m/%Y")
        url = "https://www.chileanrent.cl/reservas"
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=25000)
        page.wait_for_timeout(2000)
        html = page.content()
        results = parse_generic_results(html, "Chilean", ciudad)
    except Exception as e:
        print(f"  [Chilean/{ciudad}] Error: {e}")
    return results


# ── Parser genérico de HTML ───────────────────────────────────────

def parse_generic_results(html, empresa, ciudad):
    """
    Intenta extraer precios de cualquier HTML de rentadora chilena.
    Usa múltiples estrategias: selectores semánticos + regex fallback.
    """
    results = []
    soup = BeautifulSoup(html, "html.parser")

    # Estrategia 1: buscar elementos con clase que contenga "precio", "price", "tarifa", "valor"
    price_selectors = [
        "[class*='precio']","[class*='price']","[class*='tarifa']","[class*='valor']",
        "[class*='rate']","[class*='costo']","[class*='amount']","[class*='monto']",
        "[data-price]","[data-precio]",
    ]
    car_containers = []
    for sel in price_selectors:
        containers = soup.select(sel)
        if len(containers) > 2:
            car_containers = containers
            break

    if car_containers:
        for el in car_containers[:30]:
            # Buscar precio en el elemento y sus padres/hijos
            price_text = el.get_text(" ", strip=True)
            price = clean_price(price_text)
            if not price:
                # Buscar en el contenedor padre
                parent = el.find_parent()
                if parent:
                    price = clean_price(parent.get_text(" ", strip=True))
            if not price:
                continue

            # Buscar nombre del auto / categoría
            parent = el.find_parent() or el
            name_el = parent.find(["h2","h3","h4","p","span","div"], class_=re.compile("nombre|name|modelo|model|car|vehiculo|vehicle|categoria|category", re.I))
            name = name_el.get_text(strip=True) if name_el else parent.get_text(" ", strip=True)[:60]
            categoria = guess_category(name)

            results.append({
                "empresa":    empresa,
                "ciudad":     ciudad,
                "categoria":  categoria,
                "modelo":     name[:50],
                "precio_dia": price,
                "precio_semana": price * 7,
                "transmision": "Automático" if any(w in name.lower() for w in ["auto","automatic","automát"]) else "Manual",
            })

    # Estrategia 2: regex directo sobre el HTML si no encontramos nada
    if not results:
        # Busca patrones como $25.900, $ 25.900, CLP 25900, etc.
        price_pattern = re.compile(r'\$\s*([\d]{1,3}(?:[.,][\d]{3})*)|CLP\s*([\d]{4,6})', re.IGNORECASE)
        matches = price_pattern.findall(html)
        prices = []
        for m in matches:
            raw = m[0] or m[1]
            val = clean_price(raw)
            if val:
                prices.append(val)

        # Deduplicar y tomar los más representativos
        prices = sorted(set(prices))[:12]

        for i, price in enumerate(prices):
            cat = CATEGORIAS[i % len(CATEGORIAS)]
            results.append({
                "empresa":    empresa,
                "ciudad":     ciudad,
                "categoria":  cat,
                "modelo":     f"Extraído de {empresa}",
                "precio_dia": price,
                "precio_semana": price * 7,
                "transmision": "Manual",
            })

    print(f"  [{empresa}/{ciudad}] {len(results)} precios encontrados")
    return results


# ── Orchestrator principal ────────────────────────────────────────

SCRAPERS = [
    ("Econorent", scrape_econorent),
    ("Salfarent", scrape_salfarent),
    ("Mitta",     scrape_mitta),
    ("Gama",      scrape_gama),
    ("Avis",      scrape_avis),
    ("Sixt",      scrape_sixt),
    ("Chilean",   scrape_chilean),
]

def run():
    pickup, dropoff = get_dates()
    print(f"\n{'='*60}")
    print(f"Scraper Arriendo Autos Chile — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Período: {pickup.strftime('%d/%m/%Y')} → {dropoff.strftime('%d/%m/%Y')} (7 días)")
    print(f"{'='*60}\n")

    all_results = []
    errors = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox","--disable-setuid-sandbox","--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="es-CL",
        )
        page = context.new_page()

        for empresa_nombre, scraper_fn in SCRAPERS:
            print(f"\n▶ {empresa_nombre}")
            for ciudad_data in CIUDADES:
                ciudad = ciudad_data["nombre"]
                region = ciudad_data["region"]
                try:
                    results = scraper_fn(ciudad, pickup, dropoff, page)
                    for r in results:
                        r["region"] = region
                        r["fecha"]  = datetime.now().isoformat()
                        r["id"]     = f"{r['empresa']}_{ciudad}_{r['categoria']}"
                    all_results.extend(results)
                    pause()
                except Exception as e:
                    msg = f"{empresa_nombre}/{ciudad}: {e}"
                    errors.append(msg)
                    print(f"  ✗ {msg}")

        context.close()
        browser.close()

    # ── Guardar resultados ────────────────────────────────────────
    output = {
        "generado":   datetime.now().isoformat(),
        "periodo":    {"desde": pickup.strftime("%Y-%m-%d"), "hasta": dropoff.strftime("%Y-%m-%d")},
        "total":      len(all_results),
        "errores":    len(errors),
        "datos":      all_results,
    }

    out_path = Path("precios.json")
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ {len(all_results)} precios guardados en precios.json")
    print(f"⚠  {len(errors)} errores\n")

    # ── Telegram ─────────────────────────────────────────────────
    tg_token  = os.environ.get("TELEGRAM_TOKEN")
    tg_chat   = os.environ.get("TELEGRAM_CHAT_ID")
    if tg_token and tg_chat:
        ciudades_ok = len(set(r["ciudad"] for r in all_results))
        empresas_ok = len(set(r["empresa"] for r in all_results))
        msg = (
            f"🚗 *Precios actualizados — Econorent Intel*\n\n"
            f"📅 Período: {pickup.strftime('%d/%m/%Y')} → {dropoff.strftime('%d/%m/%Y')}\n"
            f"✅ {len(all_results)} precios extraídos\n"
            f"🏙 {ciudades_ok} ciudades · 🏢 {empresas_ok} empresas\n"
            f"⚠ {len(errors)} errores\n"
            f"🕐 {datetime.now().strftime('%H:%M')} hrs"
        )
        try:
            requests.post(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                json={"chat_id": tg_chat, "text": msg, "parse_mode": "Markdown"},
                timeout=10,
            )
            print("📨 Telegram notificado")
        except Exception as e:
            print(f"✗ Telegram error: {e}")

    return len(errors)


if __name__ == "__main__":
    exit_code = run()
    exit(0 if exit_code < 5 else 1)
