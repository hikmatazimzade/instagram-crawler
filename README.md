# Instagram Crawler

## Overview
This Instagram Crawler is designed to systematically scrape posts from famous Instagram accounts, focusing on capturing both textual and visual content. It starts with an initial set of profile URLs, collects their posts along with metadata, and downloads images for further analysis. The crawler is particularly effective at gathering **post descriptions and content types** from popular accounts, making it an ideal tool for **building image and video datasets, training vision models, and generating multimedia content**.

By structuring the collected data in an organized manner, the crawler ensures that it can be seamlessly integrated into **machine learning pipelines, AI-based captioning systems, and multimodal applications**. Furthermore, the crawler continuously expands its dataset by discovering high-profile accounts with the most followers and scraping their connections, ensuring a growing and diverse repository of Instagram data.

## Features
- Scrapes Instagram posts including:
  - Post descriptions
  - Content type (Image or Video)
  - Follower count of the account owner
  - Download path of images
- Dynamically discovers new accounts based on high-follower connections
- Stores all data in a PostgreSQL database
- Can be easily exported to CSV or other formats
- Optimized for computer vision dataset collection
- **Currently only downloads images** (Videos are identified but not downloaded)

## Data Structure
The crawler collects and stores the following data fields:

### `posts` Table
| Field Name      | Description                          |
|----------------|----------------------------------|
| `post_url`      | URL of the Instagram post |
| `unique_id`     | Unique identifier for the post |
| `content_type`  | `TRUE` for images, `FALSE` for videos |
| `download_path` | Local path of the downloaded image |
| `description`   | Caption/description of the post |

### `accounts` Table
| Field Name         | Description                          |
|-------------------|----------------------------------|
| `id`              | Unique identifier for the account |
| `account_name`    | The Instagram username of the account |
| `account_url`     | Profile URL of the account |
| `follower_number` | Number of followers the user has  |
| `following_scraped` | Whether the following list has been scraped (`TRUE` or `FALSE`) |
| `posts_scraped`   | Whether posts have been scraped (`TRUE` or `FALSE`) |

## How It Works
1. **Start with Initial URLs**: The crawler begins with a predefined set of Instagram accounts.
2. **Scrape Account Data**: Collects metadata such as follower count and account details.
3. **Scrape Posts**: Gathers post-related metadata, including descriptions and content type.
4. **Download Images**: Saves images to a local directory.
5. **Expand Network**: Identifies the most followed user and scrapes the accounts they follow.
6. **Repeat Process**: The cycle continues, ensuring data growth.

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- PostgreSQL
- Docker (if using the Docker method)
- Required dependencies from `requirements.txt`

### Manual Setup (Using Virtual Environment)
```bash
# Clone the repository
git clone https://github.com/hikmatazimzade/instagram-crawler.git
cd instagram-crawler

# Create a virtual environment
python -m venv venv

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Activate the virtual environment (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure PostgreSQL settings in config file
```

### Docker Setup
Alternatively, you can run the crawler using Docker.
```bash
# Clone the repository
git clone https://github.com/yourusername/instagram-crawler.git
cd instagram-crawler

# Build the Docker container
docker build -t instagram-crawler .

# Run the crawler container
docker run -d instagram-crawler
```

## Usage
Before running the crawler, ensure you have set up your Instagram account credentials in the `.account_env` file located inside the `cookies` folder.

Run the crawler manually with:
```bash
# On Windows
py -m crawler.main

# On Mac/Linux
python3 -m crawler.main
```

Or if using Docker:
```bash
docker start instagram-crawler
```

### Docker Database Configuration
If running the crawler in Docker, ensure that `DB_HOST` is set to `postgres` in the environment settings.

## Database Configuration
The crawler writes data to a PostgreSQL database. Ensure your database is set up correctly by modifying .database_env file inside the `db` folder before running the script.

## Potential Use Cases
- Training computer vision models
- Social media trend analysis
- Large-scale dataset collection
- NLP applications on Instagram captions

## Notes
- **This project is for educational and research purposes only.**
- Scraping Instagram without permission may violate their Terms of Service.
- Ensure compliance with local laws and regulations when using this tool.

## License
This project is licensed under the [MIT License](LICENSE).