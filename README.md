# Business Tools: Google Places Scraper & WhatsApp Bulk Sender

This tool helps you gather business data from Google Places and send bulk WhatsApp messages. It's perfect for lead generation, market research, or promotional campaigns.

## Features

* **Google Places Scraper:**
    * Scrapes business data (name, category, address, website, phone number, social media) based on location and keywords.
    * Customizable search radius.
    * Saves data to an Excel file.
    * Cleans phone numbers and generates WhatsApp links.
    * Handles API errors gracefully.
* **WhatsApp Bulk Sender:**
    * Sends personalized messages to WhatsApp numbers from an Excel file.
    * Uses Selenium to automate WhatsApp Web.
    * Includes a customizable message template.
    * Handles login and QR code scanning.
    * Provides delivery reports (successful/failed).
    * Implements random delays to avoid being flagged as spam.
* **User-Friendly Menu:**
    * Easy navigation between different functionalities.
    * Clear instructions and prompts.
    * Error handling and informative messages.


## Installation

1. Clone the repository: `git clone https://github.com/your-username/maps_scapper.git`
2. Navigate to the project directory: `cd maps_scapper`
3. Install the required packages: `pip install -r requirements.txt`

## Usage

1. **Google Places Scraper:**
    * Run `main.py`.
    * Select option 1 from the menu.
    * Enter your Google Places API Key.
    * Enter the location you want to search.
    * The data will be saved to an Excel file (`google_places_data_[location].xlsx`).
    * You'll be prompted to send WhatsApp messages to the scraped numbers.
2. **WhatsApp Bulk Sender:**
    * Run `main.py`.
    * Select option 2 from the menu.
    * Enter the name of the Excel file containing the WhatsApp numbers and business names (must have columns named "WhatsApp Link" and "Nama").
    * Scan the QR code to log in to WhatsApp Web.
    * The tool will start sending messages.
3. **Exit:**
    * Select option 3 from the menu.

## Documentation

### `GooglePlacesScraper` Class

* **`__init__(self, api_key)`:** Initializes the scraper with your Google Maps API Key.
* **`search_places(self, lokasi, radius=5000)`:** Searches for places based on location and radius. Returns a list of dictionaries containing the scraped data.
* **`get_place_details(self, place_id)`:** Retrieves detailed information about a specific place using its place ID.
* **`clean_phone_number(self, phone)`:** Cleans phone numbers and converts them to the `wa.me` link format.
* **`extract_social_media(self, place_details)`:** Extracts social media links from place details.
* **`map_keyword_to_type(self, keyword)`:** Maps keywords to Google Places types for more accurate searches.
* **`save_to_excel(self, results, filename)`:** Saves the results to an Excel file.

### `WhatsAppSender` Class

* **`__init__(self)`:** Initializes the WhatsApp sender with the Chrome WebDriver.
* **`login(self)`:** Opens WhatsApp Web and waits for manual login via QR code.
* **`send_message(self, phone_number, business_name)`:** Sends a message to a specific phone number.
* **`send_bulk_messages(self, excel_file)`:** Sends messages to all numbers in a specified Excel file.
* **`quit(self)`:** Closes the WebDriver.


## Configuration

* **Google Places API Key:** You'll need a valid Google Places API Key. Get one from the [Google Cloud Console](https://console.cloud.google.com/).
* **Excel File Format for WhatsApp Sender:** The Excel file must contain a column named "WhatsApp Link" with the `wa.me` links and a column named "Nama" with the business names.


## Disclaimer

* Use this tool responsibly and ethically. Be mindful of WhatsApp's terms of service and avoid spamming.
* The tool relies on web scraping and API calls, which can be subject to changes.


## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.



## License

This project is licensed under the MIT License.
