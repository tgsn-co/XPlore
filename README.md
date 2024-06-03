# Xplore

## Overview

**Xplore** is a Python module designed to facilitate data collection and analysis from Twitter. The module provides functions to retrieve tweets, analyze tweet contents, and visualize tweet data, leveraging the Twitter API and various Python libraries. It aims to simplify the process of gathering and analyzing social media data for research, business intelligence, and personal projects.

## Features

- **Twitter API Integration**: Authenticate and interact with the Twitter API to fetch tweets and user data.
- **Data Storage**: Save tweets and user data to CSV files for further analysis.
- **Language Detection**: Analyze tweet content to determine the language of the tweets.
- **Visualization**: Generate visualizations of tweet volumes and language distributions.

## Installation

To use Xplore, you need to have Python installed on your system along with the required libraries. You can install the required libraries using pip:

```bash
pip install requests pandas langdetect matplotlib
```

## Usage

### 1. Authentication

First, create headers for Twitter API authentication using your Bearer token:

```python
from xplore import create_headers

bearer_token = 'YOUR_BEARER_TOKEN'
headers = create_headers(bearer_token)
```

### 2. Fetching Tweet Counts

Retrieve the tweet counts for a given query within a specified time range:

```python
from xplore import gatherdata

query = 'your_search_query'
granularity = 'day'  # or 'hour'
start_time = '2022-01-01T00:00:00Z'
end_time = '2022-01-31T23:59:59Z'
tweet_counts = gatherdata.get_tweet_counts(bearer_token, query, granularity, start_time, end_time, plot=True)
```

### 3. Fetching User Data

Retrieve user data from a list of usernames in an Excel file and write it to a CSV file:

```python
from xplore import gatherdata

filepath = 'path_to_your_excel_file.xlsx'
output_filename = 'user_data.csv'
gatherdata.usersdata(bearer_token, filepath, output_filename)
```

### 4. Fetching Mentions of a Keyword

Retrieve all mentions of a keyword in tweets from the last 7 days:

```python
from xplore import gatherdata

keyword = 'your_keyword'
max_results = 100
max_pages = 10
mentions, users = gatherdata.keywordsearch(bearer_token, keyword, max_results, max_pages)
```

### 5. Analyzing Tweet Languages

Analyze the languages of tweets in an Excel file and optionally plot the distribution:

```python
from xplore import analysis

filepath = 'path_to_your_excel_file.xlsx'
Tweet_Content_column = 'Tweet_Content'
language_analysis = analysis.splitbylanguage(filepath, Tweet_Content_column, plot=True)
```

## Functions

### Authentication

#### `create_headers(bearer_token)`

Create headers for Twitter API authentication.

- **Args**: `bearer_token (str)`: Bearer token for Twitter API authentication.
- **Returns**: `dict`: Headers for the request.

### URL Creation

#### `create_url(query, granularity, start_time, end_time)`

Create the URL for the request.

- **Args**: 
  - `query (str)`: The search query.
  - `granularity (str)`: The granularity of the time buckets (e.g., 'day').
  - `start_time (str)`: The start time for the search query in ISO format.
  - `end_time (str)`: The end time for the search query in ISO format.
- **Returns**: `str`: The complete URL for the request.

### Sending Requests

#### `send_request(url, headers)`

Send the request to the Twitter API.

- **Args**: 
  - `url (str)`: The request URL.
  - `headers (dict)`: The request headers.
- **Returns**: `dict`: The JSON response from the API.
- **Raises**: Exception if the request was not successful.

### Data Storage

#### `keyword2csv(tweets, users, keyword)`

Create a CSV file to store all of the data.

- **Args**: 
  - `tweets (list)`: List of tweets mentioning the keyword.
  - `users (dict)`: Dictionary of user data.
  - `keyword (str)`: The keyword used for searching.

#### `userdata2csv(users_data, filename="output.csv")`

Write user data to a CSV file.

- **Args**: 
  - `users_data (list of dict)`: List of user data dictionaries.
  - `filename (str)`: Name of the CSV file to write the data to.

### Data Retrieval

#### `get_users(user_ids, bearer_token)`

Retrieve information for a list of user IDs.

- **Args**: 
  - `user_ids (list of str)`: List of user IDs to retrieve information for.
  - `bearer_token (str)`: Bearer token for Twitter API authentication.
- **Returns**: `list`: List of user data dictionaries.
- **Raises**: Exception if the request to the Twitter API fails.

#### `get_mentions(keyword, bearer_token, max_results=100, max_pages=100)`

Retrieve all mentions of a keyword in tweets from the last 7 days.

- **Args**: 
  - `keyword (str)`: The keyword to search for.
  - `bearer_token (str)`: Bearer token for Twitter API authentication.
  - `max_results (int)`: Maximum results per page.
  - `max_pages (int)`: Maximum number of pages to retrieve.
- **Returns**: 
  - `list`: List of tweets mentioning the keyword.
  - `dict`: Dictionary of user data.

### Data Analysis

#### `splitbylanguage(filepath, Tweet_Content_column, plot=False)`

Detect the language of content from an Excel file which contains a column with the content.

- **Args**: 
  - `filepath (str)`: The path to the Excel file to be analyzed.
  - `Tweet_Content_column (str)`: The name of the column which contains the content to be analyzed.
  - `plot (boolean)`: If True, plots a graph of the number of Tweets in each language.
- **Returns**: `pd.DataFrame`: A DataFrame with the language and the number of posts in each language.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The [Twitter API](https://developer.twitter.com/en/docs/twitter-api) for providing the data.
- The developers of [pandas](https://pandas.pydata.org/), [requests](https://docs.python-requests.org/en/latest/), [langdetect](https://pypi.org/project/langdetect/), and [matplotlib](https://matplotlib.org/) for their excellent libraries.

---
