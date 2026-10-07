from playwright.sync_api import sync_playwright

URL = "https://en.wikipedia.org/wiki/Artificial_intelligence"


def scrape():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,  # Change to True after testing
            slow_mo=100
        )

        page = browser.new_page(
            viewport={"width": 1920, "height": 1080}
        )

        print("Opening website...")

        page.goto(URL, wait_until="domcontentloaded", timeout=60000)

        page.wait_for_timeout(5000)

        page.wait_for_load_state("networkidle")

        print("Title:", page.title())

        body_text = page.locator("body").inner_text()

        links = page.locator("a")

        with open("output.txt", "w", encoding="utf-8") as file:

            file.write("=" * 80 + "\n")
            file.write("PAGE TITLE\n")
            file.write("=" * 80 + "\n")
            file.write(page.title())
            file.write("\n\n")

            file.write("=" * 80 + "\n")
            file.write("PAGE URL\n")
            file.write("=" * 80 + "\n")
            file.write(page.url)
            file.write("\n\n")

            file.write("=" * 80 + "\n")
            file.write("VISIBLE PAGE TEXT\n")
            file.write("=" * 80 + "\n\n")
            file.write(body_text)
            file.write("\n\n")

            file.write("=" * 80 + "\n")
            file.write("ALL LINKS\n")
            file.write("=" * 80 + "\n\n")

            for i in range(links.count()):

                href = links.nth(i).get_attribute("href")
                text = links.nth(i).inner_text().strip()

                file.write(f"{i+1}. {text}\n")
                file.write(f"URL : {href}\n")
                file.write("-" * 60 + "\n")

        print("Data saved successfully to output.txt")

        browser.close()


if __name__ == "__main__":
    scrape()