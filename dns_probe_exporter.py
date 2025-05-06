import dns.resolver
import time
import requests

# InfluxDB-Ziel
INFLUX_URL = "http://localhost:8086/write?db=dns_probes"

# Liste der zu überprüfenden Domains
DOMAINS = ["coop.ch", "google.com", "cloudflare.com"]

# DNS-Resolver konfigurieren
resolver = dns.resolver.Resolver()
resolver.lifetime = 5  # Timeout pro Anfrage

# Durchlauf für jede Domain
for domain in DOMAINS:
    try:
        start = time.time()
        answer = resolver.resolve(domain, "A")
        end = time.time()

        duration = round(end - start, 4)
        success = 1
        ip = answer[0].to_text()

    except Exception as e:
        duration = -1
        success = 0
        ip = "0.0.0.0"
        print(f"[ERROR] {domain}: {e}")

    # Zeitstempel in Nanosekunden (garantiert eindeutig)
    timestamp = time.time_ns()

    # Influx Line Protocol (Tag: domain, ip | Felder: success, duration | Timestamp)
    # IPv6-Doppelpunkte ersetzen (Influx erlaubt keine ":" in Tags ohne Escape)
    ip_sanitized = ip.replace(":", "_")
    payload = f'dns_query,domain={domain},ip={ip_sanitized} success={success},duration={duration} {timestamp}'

    print(f"[PAYLOAD] {payload}")

    # POST an InfluxDB
    try:
        resp = requests.post(INFLUX_URL, data=payload)
        print(f"[InfluxDB] Status: {resp.status_code}, Response: {resp.text}")
    except Exception as e:
        print(f"[POST ERROR] {e}")