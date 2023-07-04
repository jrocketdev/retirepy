from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from pathlib import Path

import tests
from tests.test_utils import TestComputeFutureValueSeries

output_dir = Path(tests.__file__).parent / "data"

capabilities = DesiredCapabilities().CHROME
capabilities["pageLoadStrategy"] = "eager"  #  interactive
service = ChromeService(ChromeDriverManager().install())
options = ChromeOptions()
options.add_argument("--headless")


def download_amortization_table(link: str, output_fpath: Path):
    print("Getting driver ready")
    driver = webdriver.Chrome(
        options=options, service=service, desired_capabilities=capabilities
    )

    print("Getting link data")
    driver.get(link)

    # Wait until we can click the "monthly" -- No need to actually click it.. but we need the wait.
    mark = (By.CSS_SELECTOR, "label[for=radio-months]")
    monthly_radio_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(mark)
    )

    print("Getting Table by id with wait...")
    mark = (By.CSS_SELECTOR, "#monthlyAmortization")
    table = driver.find_element(*mark)
    df = pd.read_html(table.get_attribute("outerHTML"))[0]

    print(f"Outputting data to {output_fpath}")
    df.to_csv(output_fpath, index=False)

    driver.quit()


for test_set in TestComputeFutureValueSeries.TESTS:
    link = test_set["link"]
    name = test_set["name"]
    print(f'Grabbing table for "{name}"')
    print(link)
    output_fname = "_".join(name.split()) + ".csv"
    output_fpath = output_dir / output_fname
    if output_fpath.exists():
        print(f"\tAlready exists. Skipping {output_fname}")
    else:
        download_amortization_table(link, output_fpath)
