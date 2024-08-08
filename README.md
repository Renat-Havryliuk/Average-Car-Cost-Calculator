# Average Car Cost Calculator

This project is designed to scrape data from three popular car sales websites and calculate the average price for specific car models based on user input. The project uses Selenium for web scraping and PyTelegramBotAPI for interacting with users through a Telegram bot.

## Features
- **Web Scraping:** Automatically collects data from three car sales websites.
- **User Interaction:** Provides a Telegram bot interface for users to request car price information.
- **Average Price Calculation:** Computes the average price of cars based on the scraped data.
- **Data Storage:** Stores calculated data in an SQLite3 database for caching and quick access.

## Technology Stack
- **Selenium:** Used for automating the web scraping process.
- **PyTelegramBotAPI:** Facilitates communication between the Telegram bot and the users.
- **SQLite3:** Stores the average price calculations to reduce redundant computations.

## Usage
- **Telegram Bot:** Users can interact with the bot to request average car prices.
- **Scraping:** Data is fetched in real-time from multiple sources, ensuring up-to-date price information.
- **Caching:** Calculated prices are stored in the database for quicker access on subsequent requests within 24 hours.
