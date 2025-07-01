#!/usr/bin/env python3
"""
Automatisiertes Website-Testing mit Tor Browser
Für autorisierte Cybersicherheitstests
"""

import time
import logging
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys
import os

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TorBotTester:
    def __init__(self, tor_path="/path/to/tor-browser", geckodriver_path="/path/to/geckodriver"):
        self.tor_path = tor_path
        self.geckodriver_path = geckodriver_path
        self.driver = None
        self.successful_attempts = 0
        self.failed_attempts = 0
        self.total_attempts = 0
        
    def setup_tor_browser(self):
        """Tor Browser mit deutschen Exit-Knoten konfigurieren"""
        try:
            self.configure_tor_for_german_exits()
            options = Options()
            options.add_argument("--headless")  # Headless Modus
            profile = webdriver.FirefoxProfile()
            
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.socks", "127.0.0.1")
            profile.set_preference("network.proxy.socks_port", 9050)
            profile.set_preference("network.proxy.socks_version", 5)
            profile.set_preference("network.proxy.socks_remote_dns", True)
            profile.set_preference("general.useragent.override", 
                                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            profile.set_preference("javascript.enabled", True)
            profile.set_preference("dom.webdriver.enabled", False)
            profile.set_preference("useAutomationExtension", False)
            options.profile = profile
            service = Service(self.geckodriver_path)
            self.driver = webdriver.Firefox(
                service=service,
                options=options
            )

            self.driver.install_addon("addon.xpi", temporary=True)

            self.driver.set_page_load_timeout(10)
            time.sleep(1)
            self.driver.execute_script("document.body.style.zoom='30%'")
            profile.set_preference("zoom.minPercent", 30)
            profile.set_preference("zoom.maxPercent", 50)
            profile.set_preference("browser.zoom.siteSpecific", False)

            logger.info("Zoom-Faktor auf 30% gesetzt, um vollständige Sichtbarkeit zu gewährleisten")
            logger.info("Tor Browser erfolgreich gestartet")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Starten des Tor Browsers: {e}")
            return False
    
    def configure_tor_for_german_exits(self):
        """Tor für deutsche Exit-Knoten konfigurieren und neue IP anzeigen"""
        try:
            # IP-Abfrage und Prüfung, ob sie aus Deutschland kommt
            self.renew_ip_until_germany()
            logger.info("Tor IP aus Deutschland bestätigt.")
        except Exception as e:
            logger.warning(f"Konnte Tor-Identität nicht erneuern: {e}")

    def get_country_from_ip(self, ip):
        """Holt das Land aus der IP-Adresse mithilfe der ip-api.com API."""
        try:
            url = f'http://ip-api.com/json/{ip}?fields=country'
            response = requests.get(url)
            data = response.json()

            # Ausgabe der gesamten API-Antwort zum Debuggen
            print(f"API Antwort: {data}")

            if data.get('status') == 'fail':
                print(f"Fehler beim Abrufen der IP-Daten: {data.get('message', 'Unbekannter Fehler')}")
                return None

            # Das Land direkt aus der Antwort extrahieren
            country = data.get('country')
            if country:
                return country
            else:
                print("Kein Land in der Antwort gefunden.")
                return None
        except Exception as e:
            print(f"Fehler beim Abrufen der Geolokalisierung: {e}")
            return None


    def renew_ip_until_germany(self):
        """Erneuert die IP solange, bis Deutschland als Land erkannt wird"""
        while True:
            time.sleep(2)
            ip = subprocess.check_output(
                "curl --socks5 127.0.0.1:9050 http://checkip.amazonaws.com/", shell=True
            ).decode().strip()

            # Geolocation-Abfrage über ip-api
            country = self.get_country_from_ip(ip)
            
            if country is None:
                print("Konnte das Land der IP nicht ermitteln, versuche es erneut...")
                continue  # Wenn keine Antwort von der API kommt, versuche es nochmal

            print(f"Aktuelle IP: {ip}, Land: {country}")

            if country == "Germany":
                print("IP ist aus Deutschland!")
                break  # Wenn Deutschland, beende die Schleife
            else:
                print("IP ist nicht aus Deutschland, Tor wird erneuert...")
                subprocess.run("(echo 'authenticate \"\"'; echo 'signal newnym'; echo 'quit';) | nc localhost 9051", shell=True)

    def create_custom_torrc(self):
        try:
            torrc_content = """
# Nur deutsche Exit-Knoten verwenden
ExitNodes {de}
StrictNodes 1

# Control Port aktivieren
ControlPort 9051

# SOCKS Port
SocksPort 9050

# CookieAuthentication 1

# Logging reduzieren
Log notice stdout
"""
            
            torrc_path = "/tmp/torrc_german_exits"
            with open(torrc_path, 'w') as f:
                f.write(torrc_content)
            
            logger.info(f"Temporäre torrc erstellt: {torrc_path}")
            logger.info("HINWEIS: Tor muss mit dieser Konfiguration neu gestartet werden:")
            logger.info(f"tor -f {torrc_path}")
            
        except Exception as e:
            logger.error(f"Konnte torrc nicht erstellen: {e}")
    
    def new_tor_circuit(self):
        """Neuen Tor-Kanal erstellen mit deutschen Exit-Knoten"""
        try:
            subprocess.run(["(   echo 'authenticate ""';   echo 'signal newnym';   echo 'quit'; ) | nc localhost 9051"], shell=True)
            self.restart_browser()
                
        except Exception as e:
            logger.warning(f"Konnte keinen neuen Tor-Kanal erstellen: {e}")
            self.restart_browser()
    
    def restart_browser(self):
        """Browser neu starten"""
        if self.driver:
            self.driver.quit()
        time.sleep(0.5)
        self.setup_tor_browser()

    # WORKING HOPEFULLY
    def dismiss_cookie_banner(self):
        """Cookie-Banner wegklicken, wenn vorhanden - ohne Wartezeiten"""
        xpaths = [
            "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'akzeptieren')]",
            "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ablehnen')]",
            "/html/body/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/button[3]",
            "/html/body/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/button[2]",
            "//*[contains(text(), 'Alle akzeptieren')]",
            "//*[contains(text(), 'Akzeptieren')]",
            "//*[contains(text(), 'Einverstanden')]",
            "//*[contains(text(), 'Zustimmen')]",
            "//button[contains(@id, 'accept')]",
            "//button[contains(@class, 'cookie')]",
            "//div[contains(@class, 'cookie')]//button",
            "//a[contains(text(), 'Akzeptieren')]"
        ]
        for path in xpaths:
            try:
                btn = self.driver.find_element(By.XPATH, path)
                if btn and btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    logger.info("Cookie-Banner geschlossen mit XPath: %s", path)
                    time.sleep(0.25)
                    return
            except NoSuchElementException:
                continue
        logger.info("Kein Cookie-Banner gefunden oder Klick fehlgeschlagen.")

    def wait_for_element(self, locator_type, locator_value, timeout=10):
        """Auf Element warten"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            by = By.XPATH if locator_type == 'xpath' else By.ID
            return wait.until(EC.element_to_be_clickable((by, locator_value)))
        except TimeoutException:
            logger.warning(f"Element nicht gefunden: {locator_value} (Timeout: {timeout}s)")
            return None

    def click_element(self, locator_type, locator_value, timeout=10):
        """Element klicken"""
        element = self.wait_for_element(locator_type, locator_value, timeout)
        if element:
            element.click()
            logger.info(f"Element geklickt: {locator_value}")
            time.sleep(0.25)
            return True
        return False

    
    def check_error_message(self):
        """Prüfen ob Fehlermeldung angezeigt wird"""
        try:
            error_element = self.driver.find_element(
                By.XPATH, 
                "/html/body/div[1]/div[2]/main/div[2]/div/div[1]/form/fieldset/div[1]/div/div[2]/h3"
            )
            if error_element.text == "Fehler":
                logger.warning("Fehler-Meldung erkannt")
                return True
        except NoSuchElementException:
            pass
        return False

    def evade_bot_detection(self):
        try:
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                navigator.plugins = [1, 2, 3];
                Object.defineProperty(navigator, 'languages', {get: () => ['de-DE', 'de']});
                Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            """)
            logger.info("Anti-Bot-Erkennung: navigator.webdriver & Plugins gefälscht")
        except Exception as e:
            logger.warning(f"Anti-Bot-Vermeidung fehlgeschlagen: {e}")
    
    def perform_test_sequence(self):
        """Führt die komplette Testsequenz aus"""
        try:
            self.total_attempts += 1
            logger.info(f"Versuch #{self.total_attempts} gestartet")
            self.driver.delete_all_cookies()

            
            # 1. Zur Website navigieren
            url = "https://www.antenne.de/programm/aktionen/die-antenne-bayern-schulhof-gigs/schulen/13248-gymnasium-markt-indersdorf"
            self.driver.get(url)
            self.driver.execute_script("document.body.style.zoom='30%'")
            logger.info("Zoom auf 30% gesetzt")
            self.evade_bot_detection()

            logger.info(f"Website geladen: {url}")
            
            self.dismiss_cookie_banner()
            
            # Seite vollständig laden lassen
            time.sleep(1)

            self.dismiss_cookie_banner()
            
            # 2. Ersten Button klicken (voteIntendButton)
            if not self.click_element("id", "voteIntendButton", 4):
                logger.error("Schritt 1 fehlgeschlagen: voteIntendButton nicht gefunden")
                return False
            

            self.dismiss_cookie_banner()
            # Warten bis geladen
            time.sleep(2)

            self.dismiss_cookie_banner()
            
            # 3. Zweiten Button klicken
            if not self.click_element("xpath", "/html/body/div[1]/div[2]/main/div[2]/div/div[1]/form/fieldset/div/aside/button", 2):
                logger.error("Schritt 2 fehlgeschlagen: Zweiter Button nicht gefunden")
                # return False

            self.dismiss_cookie_banner()
            
            # Warten bis Button erscheint
            time.sleep(2)

            self.dismiss_cookie_banner()
            
            # 4. Dritten Button klicken
            if not self.click_element("xpath", "/html/body/div[1]/div[2]/main/div[2]/div/div[1]/form/fieldset/div/div/div/div[1]/div/div/div/button", 7):
                logger.error("Schritt 3 fehlgeschlagen: Dritter Button nicht gefunden")
                return False

            self.dismiss_cookie_banner()
            
            # Warten bis Button erscheint (max 10 Sekunden)
            time.sleep(2)

            self.dismiss_cookie_banner()
            
            # 5. Voting Button klicken
            if not self.click_element("id", "votingButton", 4):
                logger.error("Schritt 4 fehlgeschlagen: votingButton nicht gefunden")
                return False

            self.dismiss_cookie_banner()
            
            # Warten auf Antwort
            time.sleep(1.5)

            # 6. Auf Fehler prüfen
            if self.check_error_message():
                logger.warning("Fehler-Meldung erkannt - Versuch nicht gezählt")
                self.failed_attempts += 1
                return False

            self.dismiss_cookie_banner()
            
            # Erfolg
            self.successful_attempts += 1
            logger.info("Versuch erfolgreich abgeschlossen!")
            return True
            
        except Exception as e:
            logger.error(f"Fehler in Testsequenz: {e}")
            self.failed_attempts += 1
            return False
    
    def run_test_loop(self, max_attempts=None, delay_between_attempts=5):
        """Haupttest-Loop"""
        start_time = time.time()

        if max_attempts is None:
            logger.info("Starte unbegrenzten Test-Loop")
        else:
            logger.info(f"Starte Test-Loop mit maximal {max_attempts} Versuchen")
        
        if not self.setup_tor_browser():
            logger.error("Konnte Tor Browser nicht starten")
            return
        
        try:
            attempt = 0
            while max_attempts is None or attempt < max_attempts:
                attempt += 1
                
                if max_attempts is None:
                    logger.info(f"\n--- Durchlauf {attempt} (unbegrenzt) ---")
                else:
                    logger.info(f"\n--- Durchlauf {attempt}/{max_attempts} ---")
                
                # Neuen Tor-Kanal erstellen
                if attempt > 1:  # Nicht beim ersten Durchlauf
                    self.new_tor_circuit()
                
                # Testsequenz ausführen
                success = self.perform_test_sequence()
                
                # Statistiken ausgeben
                elapsed_minutes = (time.time() - start_time) / 60
                if elapsed_minutes > 0:
                    success_per_minute = self.successful_attempts / elapsed_minutes
                    logger.info(f"Erfolgsrate pro Minute: {success_per_minute:.2f}")

                success_rate = (self.successful_attempts / self.total_attempts) * 100
                logger.info(f"Erfolgreiche Versuche: {self.successful_attempts}")
                logger.info(f"Fehlgeschlagene Versuche: {self.failed_attempts}")
                logger.info(f"Erfolgsrate: {success_rate:.1f}%")
                
        except KeyboardInterrupt:
            logger.info("Test durch Benutzer abgebrochen")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Aufräumen"""
        if self.driver:
            self.driver.quit()
        logger.info("Browser geschlossen")
        
        # Finale Statistiken
        logger.info("\n=== FINALE STATISTIKEN ===")
        logger.info(f"Gesamte Versuche: {self.total_attempts}")
        logger.info(f"Erfolgreiche Versuche: {self.successful_attempts}")
        logger.info(f"Fehlgeschlagene Versuche: {self.failed_attempts}")
        if self.total_attempts > 0:
            success_rate = (self.successful_attempts / self.total_attempts) * 100
            logger.info(f"Erfolgsrate: {success_rate:.1f}%")

def main():
    """Hauptfunktion"""
    # macOS-spezifische Pfade
    tor_path = "~/antenne-bot-2/tor"
    geckodriver_path = "/usr/local/bin/geckodriver"  # Anpassen falls anders installiert
    
    # Prüfen ob Geckodriver existiert
    # if not os.path.exists(geckodriver_path):
    #    print("FEHLER: Geckodriver nicht gefunden.")
    #    print("Installation für macOS:")
    #    print("1. brew install geckodriver")
    #    print("2. Oder manuell von https://github.com/mozilla/geckodriver/releases")
    #    print(f"3. Geckodriver nach {geckodriver_path} kopieren")
    #    sys.exit(1)
    
    # Prüfen ob Tor Browser existiert
        #if not os.path.exists(tor_path):
        #print("FEHLER: Tor Browser nicht gefunden.")
        #print("Installation:")
        #print("1. Download von https://www.torproject.org/download/")
        #print("2. Tor Browser.app in den Applications-Ordner ziehen")
    #sys.exit(1)
    
    print("WICHTIG: Stelle sicher, dass Tor läuft:")
    print("Entweder:")
    print("1. Tor Browser einmal normal starten (verbindet automatisch)")
    print("2. Oder separaten Tor-Service starten:")
    print("   brew install tor")
    print("   tor -f /tmp/torrc_german_exits")
    print()
    
    tester = TorBotTester(tor_path, geckodriver_path)
    
    try:
        # max_input = input("Maximale Anzahl Versuche (leer für unbegrenzt, Standard: 50): ").strip()
        max_input = ""
        
        if max_input == "":
            max_attempts = None  # Unbegrenzt
        elif max_input.lower() in ['unbegrenzt', 'unlimited', 'infinite', '0']:
            max_attempts = None  # Unbegrenzt
        else:
            try:
                max_attempts = int(max_input)
                if max_attempts <= 0:
                    max_attempts = None  # Unbegrenzt bei 0 oder negativ
            except ValueError:
                max_attempts = 50  # Fallback
                
        # delay = int(input("Pause zwischen Versuchen in Sekunden (Standard: 10): ") or "10")
        delay = 10
        
        tester.run_test_loop(max_attempts, delay)
        
    except ValueError:
        print("Ungültige Eingabe. Verwende Standardwerte.")
        tester.run_test_loop(50, 10)

if __name__ == "__main__":
    print("=== TOR BROWSER BOT TESTER ===")
    print("Für autorisierte Cybersicherheitstests")
    print("Drücke Ctrl+C zum Beenden")
    print("Gib 'unbegrenzt' oder leer ein für unbegrenzte Versuche\n")
    main()
