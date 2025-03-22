
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import time

url = 'any_url_here'

# Configure browser with Chrome-like fingerprint
options = Options()
options.add_argument("-headless")
options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
options.set_preference("dom.webnotifications.enabled", False)

def get_data():
    try:
        # Initialize driver with enhanced options
        driver = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()),
            options=options
        )
        driver.set_page_load_timeout(60)
        driver.get(url)
        
        # Add cookie consent handling
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button#truste-consent-button"))
            ).click()
        except Exception:
            pass
        
        # Wait for main grid container from screenshot
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#_grid"))
        )
        
        # Smart scroll to load all data
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Wait for data cells to populate
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div._cell.symbol > set-class > a"))
        )
        
        # Get all visible rows
        rows = WebDriverWait(driver, 40).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "set-class.row-group"))
        )
        print(f"Found {len(rows)} commodities")
        
        for row in rows:
            try:
                # Get symbol with multiple fallback strategies
                symbol = WebDriverWait(row, 30).until(
                    EC.visibility_of_any_element_located([
                        (By.CSS_SELECTOR, "div[data-th='Contract'] a"),
                        (By.CSS_SELECTOR, "div._cell.symbol a"),
                        (By.XPATH, ".//a[contains(@href, '/futures/quotes')]")
                    ])
                ).text.strip()
                
                # Get values using data-th attributes for precise targeting
                headers = ['Last', 'Change', 'High', 'Low', 'Previous', 'Time', 'Volume', 'Month', 'Year']
                values = []
                for header in headers:
                    try:
                        cell = WebDriverWait(row, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, f"div[data-th='{header}'] div.value"))
                        )
                        values.append(cell.text.replace('\n', ' ').strip())
                    except Exception:
                        values.append("N/A")
                # Print formatted output
                print(f"\n{symbol} (Cash)")
                print('\n'.join(values[:9]))  # Ensure we only show first 9 values
                print("-" * 30)
                
            except Exception as row_error:
                print(f"Skipping row: {str(row_error)}")
                continue
                
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    get_data()
