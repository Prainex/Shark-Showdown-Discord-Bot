# 🦈 Shark Showdown Discord Bot

The **Shark Showdown Discord Bot** is a fully automated tournament management assistant built to streamline the registration and management process for competitive **Valorant** tournaments.  

It connects **Discord** with **Google Sheets** to monitor sign-ups, post team information, and deliver real-time updates — all powered by Google Cloud services.

---

## 🚀 Features

- **📋 Automated Sign-Up Tracking**
  - Fetches new team entries from a connected **Google Sheet** in real-time.
  - Posts signup information directly into a specified Discord channel.

- **🎮 Tournament Management**
  - Displays rosters with player and substitute details.
  - Tracks teams and entries seamlessly.

- **🔔 Notification System**
  - Sends alerts to admins or channels when new teams join.
  - Logs all activity with error handling for transparency.

- **☁️ Cloud Integration**
  - Uses **Google Cloud Console** for authentication and project management.
  - Secures credentials using environment variables and `.env` files.

---

## 🧩 Tech Stack

| Component | Technology |
|------------|-------------|
| **Language** | Python 3.10+ |
| **Discord Library** | [discord.py](https://github.com/Rapptz/discord.py) |
| **Data Storage** | [Google Sheets API](https://developers.google.com/sheets/api) |
| **Cloud Platform** | [Google Cloud Platform (GCP)](https://cloud.google.com/) |
| **Environment Management** | dotenv |
| **Logging** | Python `logging` module |
