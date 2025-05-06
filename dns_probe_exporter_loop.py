import dns.resolver
import time
import requests

# InfluxDB-Ziel (lokale Instanz)
INFLUX_URL = "http://localhost:8086/write?db=dns_probes"

# Liste der zu überprüfenden Domains
DOMAINS = ["coop.ch", "google.com", "cloudflare.com"]

# DNS-Resolver konfigurieren (Timeout pro Anfrage = 5 Sekunden)
resolver = dns.resolver.Resolver()
resolver.lifetime = 5

# Intervall zwischen Messungen in Sekunden
INTERVAL_SECONDS = 3

print("[INFO] Starte DNS-Probing Loop. Beenden mit CTRL+C.")

try:
    # Endlosschleife für kontinuierliches Monitoring
    while True:
        # Iteration über alle definierten Domains
        for domain in DOMAINS:
            try:
                # Startzeit erfassen
                start = time.time()
                
                # DNS-Auflösung für A-Record durchführen
                answer = resolver.resolve(domain, "A")
                
                # Endzeit erfassen und Dauer berechnen
                end = time.time()
                duration = round(end - start, 4)

                # Erfolgreiche Auflösung
                success = 1
                ip = answer[0].to_text()

            except Exception as e:
                # Fehlerfall (z. B. Timeout, NXDOMAIN)
                duration = -1
                success = 0
                ip = "0.0.0.0"
                print(f"[ERROR] {domain}: {e}")

            # Aktueller Zeitstempel in Nanosekunden (für InfluxDB)
            timestamp = time.time_ns()

            # IPv6-Doppelpunkte ersetzen (Influx erlaubt kein ":" in Tags)
            ip_sanitized = ip.replace(":", "_")

            # Payload im Influx Line Protocol Format erstellen
            payload = f'dns_query,domain={domain},ip={ip_sanitized} success={success},duration={duration} {timestamp}'

            # Payload in Konsole ausgeben (Debug-Zwecke)
            print(f"[PAYLOAD] {payload}")

            # Daten an InfluxDB senden
            try:
                resp = requests.post(INFLUX_URL, data=payload)
                print(f"[InfluxDB] Status: {resp.status_code}, Response: {resp.text}")
            except Exception as e:
                print(f"[POST ERROR] {e}")
        
        # Warten bis zum nächsten Durchlauf
        print(f"[INFO] Warte {INTERVAL_SECONDS} Sekunden bis zum nächsten Durchlauf...\n")
        time.sleep(INTERVAL_SECONDS)

except KeyboardInterrupt:
    # Script sauber beenden bei Tastenkombination CTRL+C
    print("\n[INFO] Script manuell beendet.")
