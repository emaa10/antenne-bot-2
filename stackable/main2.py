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
import random
from tempfile import mkdtemp
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 Version/16.3 Safari/605.1.15",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 Version/16.0 Mobile Safari/604.1",
#     "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 Chrome/58.0 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/110.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/100.0 Safari/537.36"
# ]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 Version/16.0 Mobile Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 Chrome/58.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/110.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/100.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 Chrome/59.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 Chrome/108.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 15_2 like Mac OS X) AppleWebKit/605.1.15 Version/15.0 Mobile Safari/604.1",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/18.18362",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 Chrome/97.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6_1 like Mac OS X) AppleWebKit/605.1.15 Version/15.6 Mobile Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 Chrome/49.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/103.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; ARM; Surface Pro X) AppleWebKit/537.36 Chrome/87.0 Safari/537.36 Edge/87.0",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile Safari/604.1",
    "Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-A505F) AppleWebKit/537.36 Chrome/88.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/105.0 Safari/537.36 OPR/91.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:112.0) Gecko/20100101 Firefox/112.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 Chrome/67.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 Chrome/49.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/90.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Redmi Note 8T) AppleWebKit/537.36 Chrome/83.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 Chrome/41.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Mozilla/5.0 (Linux; Android 8.0.0; SM-G950F) AppleWebKit/537.36 Chrome/86.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 Version/13.0 Mobile Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 Chrome/91.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 Chrome/92.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 Version/13.0 Mobile Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/605.1.15 Version/14.0.1 Safari/605.1.15"
]


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

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class TorBotTester:
    def __init__(self, tor_path="C:/Path/to/Tor", geckodriver_path="C:/Path/To/Gecko", addon_path=""):
        self.tor_path = tor_path
        self.geckodriver_path = geckodriver_path
        self.addon_path = addon_path
        self.driver = None
        self.successful_attempts = 0
        self.failed_attempts = 0
        self.total_attempts = 0
        self.user_agent_last_used = {ua: datetime.min for ua in USER_AGENTS}

    def get_available_user_agent(self):
        now = datetime.now()

        # Liste aller, die in den letzten 60 Sekunden nicht verwendet wurden
        eligible = [
            ua for ua, last_used in self.user_agent_last_used.items()
            if now - last_used >= timedelta(seconds=60)
        ]

        if not eligible:
            # Wenn keiner frei, dann Liste zurücksetzen (alle freigeben)
            logger.info("Alle User-Agents wurden kürzlich verwendet – Zyklus wird zurückgesetzt")
            for ua in USER_AGENTS:
                self.user_agent_last_used[ua] = datetime.min
            eligible = USER_AGENTS

        selected = random.choice(eligible)
        self.user_agent_last_used[selected] = now
        return selected
        
    def setup_tor_browser(self):
        """Firefox mit zufälligem Profil und User-Agent starten"""
        try:
            options = Options()
            options.add_argument("--headless")  # Optional für versteckten Modus

            # Neuen temporären Profilordner erzeugen
            profile_dir = mkdtemp()
            profile = webdriver.FirefoxProfile(profile_dir)

            # Zufälligen User-Agent wählen
            user_agent = self.get_available_user_agent()
            profile.set_preference("general.useragent.override", user_agent)
            profile.set_preference("intl.accept_languages", "de-DE, de")


            # Weitere Anti-Fingerprinting Einstellungen
            profile.set_preference("dom.webdriver.enabled", False)
            profile.set_preference("useAutomationExtension", False)
            profile.set_preference("privacy.resistFingerprinting", False)
            profile.set_preference("webgl.disabled", True)
            profile.set_preference("canvas.poisondata", True)
            profile.set_preference("media.peerconnection.enabled", False)
            profile.set_preference("network.http.referer.spoofSource", True)
            profile.set_preference("privacy.spoof_english", 0)


            options.profile = profile
            options.binary_location = self.tor_path
            service = Service(self.geckodriver_path)
            self.driver = webdriver.Firefox(service=service, options=options)
            #self.driver.install_addon("addon.xpi", temporary=True)
            self.driver.install_addon(self.addon_path, temporary=True)

            self.driver.set_page_load_timeout(10)
            logger.info(f"Neues Browserprofil mit User-Agent: {user_agent}")
            return True

        except Exception as e:
            logger.error(f"Fehler beim Starten des Browsers: {e}")
            return False

    # def setup_tor_browser(self):
    #     """Tor Browser mit deutschen Exit-Knoten konfigurieren"""
    #     try:
    #         options = Options()
    #         options.add_argument("--headless")  # Headless Modus
    #         profile = webdriver.FirefoxProfile()
            
    #         profile.set_preference("general.useragent.override", 
    #                              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    #         profile.set_preference("javascript.enabled", True)
    #         profile.set_preference("dom.webdriver.enabled", False)
    #         profile.set_preference("useAutomationExtension", False)
    #         options.profile = profile
    #         service = Service(self.geckodriver_path)
    #         options.binary_location = self.tor_path
    #         self.driver = webdriver.Firefox(
    #             service=service,
    #             options=options
    #         )

    #         self.driver.install_addon(self.addon_path, temporary=True)

    #         self.driver.set_page_load_timeout(10)
    #         time.sleep(1)
    #         self.driver.execute_script("document.body.style.zoom='30%'")
    #         profile.set_preference("zoom.minPercent", 30)
    #         profile.set_preference("zoom.maxPercent", 50)
    #         profile.set_preference("browser.zoom.siteSpecific", False)

    #         logger.info("Zoom-Faktor auf 30% gesetzt, um vollständige Sichtbarkeit zu gewährleisten")
    #         logger.info("Tor Browser erfolgreich gestartet")
    #         return True
            
    #     except Exception as e:
    #         logger.error(f"Fehler beim Starten des Tor Browsers: {e}")
    #         return False

    def new_tor_circuit(self):
        self.driver.refresh()
        time.sleep(2)

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
            
            # Seite vollständig laden lassen
            time.sleep(1)
            
            # 2. Ersten Button klicken (voteIntendButton)
            if not self.click_element("id", "voteIntendButton", 7):
                logger.error("Schritt 1 fehlgeschlagen: voteIntendButton nicht gefunden")
                return False
            
            # Warten bis geladen
            time.sleep(2)

            # 3. Zweiten Button klicken
            if not self.click_element("xpath", "/html/body/div[1]/div[2]/main/div[2]/div/div[1]/form/fieldset/div/aside/button", 5):
                logger.error("Schritt 2 fehlgeschlagen: Zweiter Button nicht gefunden")
                # return False
            
            # Warten bis Button erscheint
            time.sleep(2)

            # 4. Dritten Button klicken
            if not self.click_element("xpath", "/html/body/div[1]/div[2]/main/div[2]/div/div[1]/form/fieldset/div/div/div/div[1]/div/div/div/button", 30):
                logger.error("Schritt 3 fehlgeschlagen: Dritter Button nicht gefunden")
                return False
            
            # Warten bis Button erscheint (max 10 Sekunden)
            time.sleep(2)

            # 5. Voting Button klicken
            if not self.click_element("id", "votingButton", 30):
                logger.error("Schritt 4 fehlgeschlagen: votingButton nicht gefunden")
                return False
            
            # Warten auf Antwort
            time.sleep(1.5)

            # 6. Auf Fehler prüfen
            if self.check_error_message():
                logger.warning("Fehler-Meldung erkannt - Versuch nicht gezählt")
                self.failed_attempts += 1
                return False
            
            # Erfolg
            self.successful_attempts += 1
            logger.info("Versuch erfolgreich abgeschlossen!")
            response = requests.get("https://counterantenne.bergerhq.de/api/increment", allow_redirects=True)
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
                    self.cleanup()
                    self.setup_tor_browser()
                
                # Testsequenz ausführen
                success = self.perform_test_sequence()

                #logger.info("Warte 1 min bis zum nächsten Vote")

                #time.sleep(58)
                
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
    #tor_path = "FirefoxPortable/App/Firefox64/firefox.exe"
    #tor_path = os.path.join(BASE_DIR, "FirefoxPortable", "App", "Firefox64", "firefox.exe")
    tor_path = resource_path(os.path.join("FirefoxPortable", "App", "Firefox64", "firefox.exe"))
    #geckodriver_path = "geckodriver.exe"
    #geckodriver_path = os.path.join(BASE_DIR, "geckodriver.exe")
    geckodriver_path = resource_path("geckodriver.exe")
    #addon_path = os.path.join(BASE_DIR, "addon.xpi")
    addon_path = resource_path("addon.xpi")
    torrc_path = os.path.join(BASE_DIR, "torrc")
    
    tester = TorBotTester(tor_path, geckodriver_path, addon_path)
    
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
                
        tester.run_test_loop(max_attempts, 10)
        
    except ValueError:
        print("Ungültige Eingabe. Verwende Standardwerte.")
        tester.run_test_loop(50, 10)

if __name__ == "__main__":
    print("=== ANTENNE BAYERN BOT - simple Version, maxxed Version ===")
    print("Drücke Ctrl+C zum Beenden")
    main()