# Project Title

Telegram Reporting Bot

## Description

This project consists of two Python scripts that work together to send reports in XLSX format to a Telegram channel. The first script connects to a database, retrieves data, and generates an XLSX report file. The second script runs a Telegram bot that listens for manual report requests and sends the report file to the specified channel. It also sends scheduled reports at specific times.

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/py310/telegram-reporting-bot.git
  
2. Install the required dependencies:
   ```shell
   pip install -r requirements.txt

3. Set up the [configuration file](#configuration):
   - Fill in the necessary configuration details in the config.ini file, such as Telegram bot token, channel ID, database connection details, etc.

## Usage

1. Run the  script (telegram_bot.py) to start the Telegram bot:

   ```shell
   python telegram_bot.py

The bot listens for manual report requests in the specified Telegram channel and sends the report file upon request.  
It also sends scheduled reports at specific times (Tuesday to Saturday at 11:00).  
To manually request a report, send the command '/report' in the authorized Telegram channel or chat.  

## Configuration

The configuration file (config.ini) contains the following sections and options:

- [telegram]  
  - bot_token: Telegram bot token.  
  - channel: ID of the Telegram channel where the reports will be sent.  
  - user: ID of the authorized user who can request the report.  
- [database]  
  - host: Database host.  
  - name: Database name.  
  - port: Database port.  
  - user: Database user.  
  - password: Database password.  
- [folders]  
  - result_folder: Folder path where the generated report files will be saved.  

## License
MIT
