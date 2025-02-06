from playwright.sync_api import sync_playwright
import time
import os

# Mapping of subtitles to direct URLs
SUBTITLE_URLS = {
    "11-U": "https://www.dcregs.dc.gov/Common/DCMR/ChapterList.aspx?subtitleId=68",
    "11-W": "https://www.dcregs.dc.gov/Common/DCMR/ChapterList.aspx?subtitleId=69",
    "11-X": "https://www.dcregs.dc.gov/Common/DCMR/ChapterList.aspx?subtitleId=70",
    "11-Y": "https://www.dcregs.dc.gov/Common/DCMR/ChapterList.aspx?subtitleId=71",
    "11-Z": "https://www.dcregs.dc.gov/Common/DCMR/ChapterList.aspx?subtitleId=72"
}

DOWNLOAD_DIR = "dc_zoning_documents"

# Ensure the base directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


def scrape_zoning_documents():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to False for debugging
        context = browser.new_context(accept_downloads=True)  # Enable downloads
        page = context.new_page()

        for subtitle, url in SUBTITLE_URLS.items():
            try:
                print(f"Navigating to {subtitle} page: {url}")
                page.goto(url)
                page.wait_for_selector("a")

                # Create folder for subtitle
                section_folder = os.path.join(DOWNLOAD_DIR, subtitle)
                if not os.path.exists(section_folder):
                    os.makedirs(section_folder)

                # Find all chapter links and process each
                chapter_links = page.locator("table tr td a").all()
                for chapter_index in range(len(chapter_links)):
                    try:
                        # Refresh locator before clicking
                        chapter_links = page.locator("table tr td a").all()
                        chapter_link = chapter_links[chapter_index]
                        chapter_text = chapter_link.inner_text().strip()

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

                        # Go back to the subtitle section to continue with the next chapter
                        page.go_back()
                        page.wait_for_timeout(3000)
                    except Exception as e:
                        print(f"Skipping chapter {chapter_text} due to error: {e}")
            except Exception as e:
                print(f"Skipping subtitle {subtitle} due to error: {e}")

        print("Download complete.")
        browser.close()


# Run the scraper
if __name__ == "__main__":
    scrape_zoning_documents()
