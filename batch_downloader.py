from playwright.sync_api import sync_playwright
import time
import os

# Base URL for DC Zoning Code
BASE_URL = "https://www.dcregs.dc.gov/Common/DCMR/SubTitleList.aspx?TitleId=32"
DOWNLOAD_DIR = "dc_zoning_documents"

# List of all subtitle sections (11-A to 11-K, 11-U to 11-Z)
SUBTITLES = [
    "11-A", "11-B", "11-C", "11-D", "11-E", "11-F", "11-G", "11-H", "11-I", "11-J", "11-K",
    "11-U", "11-V", "11-W", "11-X", "11-Y", "11-Z"
]

# Ensure the base directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


def scrape_zoning_documents():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to False for debugging
        context = browser.new_context(accept_downloads=True)  # Enable downloads
        page = context.new_page()
        page.goto(BASE_URL)

        # Wait for zoning page to load
        page.wait_for_selector("a")

        # Debugging step: Print all detected links
        all_links = page.locator("a").all()
        print("Detected links on the page:")
        for link in all_links:
            print(link.inner_text().strip())

        for subtitle in SUBTITLES:
            try:
                # Navigate back to the main URL to reset state
                page.goto(BASE_URL)
                page.wait_for_selector("a")

                # Locate and click the subtitle link dynamically
                section_link = page.locator(f"a", has_text=subtitle).first
                if not section_link.is_visible():
                    print(f"Skipping {subtitle}, link not found or not visible.")
                    continue

                print(f"Clicking into {subtitle}...")
                section_link.click()
                page.wait_for_timeout(3000)  # Wait for content to load

                # Create folder for subtitle
                section_folder = os.path.join(DOWNLOAD_DIR, subtitle)
                if not os.path.exists(section_folder):
                    os.makedirs(section_folder)

                # Find all chapter links
                chapter_links = page.locator("a").all()

                for chapter_link in chapter_links:
                    chapter_text = chapter_link.inner_text().strip()
                    if chapter_text.startswith(subtitle):  # Ensure it's a chapter number
                        print(f"Accessing chapter: {chapter_text}")
                        chapter_link.click()
                        page.wait_for_timeout(3000)  # Allow zoning text to load

                        # Create a subfolder for the chapter
                        chapter_folder = os.path.join(section_folder, chapter_text)
                        if not os.path.exists(chapter_folder):
                            os.makedirs(chapter_folder)

                        # Refresh page locator before finding "View text" links
                        page.wait_for_selector("table tr td a", timeout=5000)
                        view_text_links = page.locator("table tr td a", has_text="View text").all()

                        for i in range(len(view_text_links)):
                            try:
                                # Refresh locator before clicking
                                page.wait_for_selector("table tr td a", timeout=5000)
                                view_text_links = page.locator("table tr td a", has_text="View text").all()

                                print(f"Opening section text for {chapter_text} - Entry {i + 1}")

                                # Get the section heading for file naming
                                section_heading = page.locator("table tr td:nth-child(2)").nth(i).inner_text().strip()

                                # Ensure heading is not empty
                                if not section_heading:
                                    section_heading = chapter_text  # Fallback to chapter text if no heading found

                                with page.expect_download() as download_info:
                                    view_text_links[i].click()
                                download = download_info.value

                                # Define the new file path using the Section Heading
                                doc_filename = f"{section_heading}.doc".replace(" ", "_").replace("/", "-")
                                doc_file_path = os.path.join(chapter_folder, doc_filename)

                                # Save the downloaded file to the correct location
                                download.save_as(doc_file_path)

                                print(f"Saved {doc_file_path}")

                            except Exception as e:
                                print(f"Skipping entry {i + 1} due to error: {e}")

                        # Go back to the subtitle section
                        page.go_back()
                        page.wait_for_timeout(3000)

            except Exception as e:
                print(f"Skipping subtitle {subtitle} due to error: {e}")

        print("Download complete.")
        browser.close()


# Run the scraper
if __name__ == "__main__":
    scrape_zoning_documents()
