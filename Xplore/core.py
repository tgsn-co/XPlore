

import requests
import csv
import pandas as pd
import re
import time
import urllib
import datetime
import os
import matplotlib.pyplot as plt

from langdetect import detect

date = datetime.datetime.now().date()

def create_headers(bearer_token):
    """
    Create the headers for the request.
    
    Args:
        bearer_token (str): Bearer token for Twitter API authentication.
    
    Returns:
        dict: Headers for the request.
    """
    return {"Authorization": f"Bearer {bearer_token}"}


def create_url(query, granularity, start_time, end_time):
    """
    Create the URL for the request.
    
    Args:
        query (str): The search query.
        granularity (str): The granularity of the time buckets (e.g., 'day').
        start_time (str): The start time for the search query in ISO format.
        end_time (str): The end time for the search query in ISO format.
    
    Returns:
        str: The complete URL for the request.
    """
    endpoint_url = 'https://api.twitter.com/2/tweets/counts/all'
    query_params = {
        'query': query,
        'granularity': granularity,
        'start_time': start_time,
        'end_time': end_time,
    }
    return endpoint_url + '?' + urllib.parse.urlencode(query_params)


def send_request(url, headers):
    """
    Send the request to the Twitter API.
    
    Args:
        url (str): The request URL.
        headers (dict): The request headers.
    
    Returns:
        dict: The JSON response from the API.
    
    Raises:
        Exception: If the request was not successful.
    """
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def keyword2csv(tweets, users, keyword):
    """
    Create a CSV file to store all of the data.
    
    Args:
        tweets (list): List of tweets mentioning the keyword.
        users (dict): Dictionary of user data.
        keyword (str): The keyword used for searching.
    """
    nodes = set()

    for tweet in tweets:
        tweet_id = tweet['id']
        author_id = tweet['author_id']
        tweet_content = tweet['text']  # Extracting tweet content
        target = users[author_id]['username'] if author_id in users else 'unknown'
        created_at = tweet["created_at"]
        location = users[author_id].get('location', 'unknown') if author_id in users else 'unknown'
        tag = ""
        source = ""
        mention = re.search(r'@([^\s]+)', tweet_content)
        if mention:
            tag = "mention"
            source = mention.group(1)
        retweet = re.search(r'RT @([^:\s]+):', tweet_content)  # Improved retweet detection
        if retweet:
            tag = "retweet"
            source = retweet.group(1)
        nodes.add((tweet_id, target, source, author_id, tag, keyword, created_at, location, tweet_content))  # returned fields

    with open(f'TweetsWith_{keyword}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['tweet_Id', 'Author_Username', "Source_of_Tweet", "Author_id", "Tag", "Keyword", "Created_at", "Location", "Tweet_Content"])  # Header row
        writer.writerows(nodes)


def get_users(user_ids, bearer_token):
    """
    Retrieve information for a list of user IDs.
    
    Args:
        user_ids (list of str): List of user IDs to retrieve information for.
        bearer_token (str): Bearer token for Twitter API authentication.
    
    Returns:
        list: List of user data dictionaries.
    
    Raises:
        Exception: If the request to the Twitter API fails.
    """
    users_endpoint = "https://api.twitter.com/2/users/by"
    headers = create_headers(bearer_token)
    batch_size = 100  # Max number of user IDs allowed per request
    all_users_data = []

    for i in range(0, len(user_ids), batch_size):
        batch_ids = user_ids[i:i+batch_size]
        params = {
            'ids': ','.join(batch_ids),
            'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,public_metrics,url,username,verified'
        }
        
        response = requests.get(users_endpoint, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"API error: {response.text}")
        
        all_users_data.extend(response.json()['data'])

    return all_users_data


def userdata2csv(users_data, filename="output.csv"):
    """
    Write user data to a CSV file.
    
    Args:
        users_data (list of dict): List of user data dictionaries.
        filename (str): Name of the CSV file to write the data to.
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header = ['id', 'username', 'name', 'created_at', 'location', 'verified', 'description', 'followers_count', 'following_count', 'tweet_count', 'listed_count']
        writer.writerow(header)
        
        for user in users_data:
            public_metrics = user['public_metrics']
            row = [
                user['id'],
                user['username'],
                user['name'],
                user['created_at'],
                user['location'],
                user['verified'],
                user['description'],
                public_metrics['followers_count'],
                public_metrics['following_count'],
                public_metrics['tweet_count'],
                public_metrics['listed_count']
            ]
            writer.writerow(row)


def get_mentions(keyword, bearer_token, max_results=100, max_pages=100):
    """
    Retrieve all mentions of a keyword in tweets from the last 7 days.
    
    Args:
        keyword (str): The keyword to search for.
        bearer_token (str): Bearer token for Twitter API authentication.
        max_results (int): Maximum results per page.
        max_pages (int): Maximum number of pages to retrieve.
    
    Returns:
        list: List of tweets mentioning the keyword.
        dict: Dictionary of user data.
    """
    search_url = "https://api.twitter.com/2/tweets/search/recent"  # Can only search for tweets from the last 7 days.
    headers = create_headers(bearer_token)
    params = {
        'query': keyword,
        'max_results': max_results,
        'tweet.fields': 'created_at,author_id,text',
        'expansions': 'author_id',
        'user.fields': 'username, location'  # You can change the returned fields, check the Twitter API documentation for more information.
    }

    all_tweets = []
    all_users = {}
    for _ in range(max_pages):
        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code == 429:
            print("Too many requests. Sleeping for 15 minutes...")  # Wait for the rate limit to reset.
            time.sleep(901)
            response = requests.get(search_url, headers=headers, params=params)
        elif response.status_code != 200:
            raise Exception(f"Cannot fetch mentions: {response.text}")

        json_response = response.json()
        tweets = json_response.get('data', [])
        all_tweets.extend(tweets)
        users = {u['id']: u for u in json_response.get('includes', {}).get('users', [])}
        all_users.update(users)

        if 'next_token' in json_response.get('meta', {}):
            params['next_token'] = json_response['meta']['next_token']
        else:
            break

    return all_tweets, all_users




class gatherdata:
    """Functions to gather data using the X api."""


    def usersdata(bearer_token, filepath, output_filename="output.csv"):
        """
        Main function to retrieve user data from a list of usernames in an excel and write it to a CSV file.
        The column must be named 'id'.
        
        Args:
            bearer_token (str): Bearer token for Twitter API authentication.
            filepath (str): Path to the Excel file containing user IDs.
            output_filename (str): Name of the output CSV file.
        """
        usernames = pd.read_excel(filepath)
        user_ids = usernames['id'].astype(str).tolist()
        
        try:
            # Get user information
            users_info = get_users(user_ids, bearer_token)
            # Write user information to CSV
            userdata2csv(users_info, output_filename)
            print("User data retrieved and written to CSV successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def keywordsearch(bearer_token, keyword, max_results=100, max_pages=100):
        """
        Main function to retrieve mentions and create CSV files.
        
        Args:
            bearer_token (str): Bearer token for Twitter API authentication.
            keyword (str): The keyword to search for.
            max_results (int): Maximum results per page.
            max_pages (int): Maximum number of pages to retrieve.
        """
        try:
            mentions, users = get_mentions(keyword, bearer_token, max_results, max_pages)
            keyword2csv(mentions, users, keyword)
            print("User data retrieved and written to CSV successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")



    def get_tweet_counts(bearer_token, query, granularity, start_time, end_time, plot=False):
        """
        Get the tweet counts for a given query in the specified time range.
        
        Args:
            bearer_token (str): Bearer token for Twitter API authentication.
            query (str): The search query.
            granularity (str): The granularity of the time buckets (e.g., 'day').
            start_time (str): The start time for the search query in ISO format.
            end_time (str): The end time for the search query in ISO format.
        
        Returns:
            dict: The JSON response from the API.
        """
        headers = create_headers(bearer_token)
        url = create_url(query, granularity, start_time, end_time)


        tweet_volumes = send_request(url, headers)

        if plot == True:
            time = []
            volume = []
            for data in tweet_volumes['data']:
                if granularity == 'hour':
                    time.append(data['start'][11:16])
                    volume.append(data['tweet_count'])

                elif granularity == 'day':
                    time.append(data['start'][:10])
                    volume.append(data['tweet_count'])

                else:
                    time.append(data['start'][-10:-5])
                    volume.append(data['tweet_count'])
                    
            fig, ax = plt.subplots(figsize=(10, 6))
            plt.bar(time, volume, width=0.8, color='#FFCC00', edgecolor='black')

            # Set graph properties
            ax.set_facecolor('#191A19')  # Set the background color of the axes (plot area)
            fig.patch.set_facecolor('#191A19')  # Set the background color around the plot area

            # Set the title and labels with the specified colors and font sizes
            ax.set_title(f"Volume of Tweets Per {granularity}", color='#FFCC00', fontsize=12, fontname='Sans-serif', weight='bold')
            ax.set_xlabel('Date', color='#CCCCCC', fontsize=12, fontname='Sans-serif')
            ax.set_ylabel('Number of Posts', color='#CCCCCC', fontsize=12, fontname='Sans-serif')
            
            # Set the colors for the horizontal grid only, tick labels, and remove top and right spines
            ax.grid(True, color='#737373', linestyle='-', linewidth=1, axis='y')
            ax.tick_params(colors='#CCCCCC', labelsize=10)

            # Change the tick label font to sans-serif (Universal Sans may not be available)
            for label in ax.get_xticklabels():
                label.set_fontname('Sans-serif')
            for label in ax.get_yticklabels():
                label.set_fontname('Sans-serif')

            plt.xticks(rotation=45)
            plt.tight_layout()  
            plt.show()





        return tweet_volumes


class analysis:
    """Functions that can be used to analyse the data collected."""

    def splitbylanguage(filepath, Tweet_Content_column, plot=False):
        """
        Detect the a language of content from an excel file which contains a column with the content.

        Args:
            filepath (str): the path to the excel file to be analysed.
            Tweet_Content_column (str): The name of the column which contains the content to be analysed.
            plot (boloean) : If True, plots a graph of the number of Tweets in each language.
        
        Returns:
            tweet_volume_df (pd.DataFrame): A DataFrame with the language and the number of posts in each language.
    
        """

        # Reading the Excel file.
        tweets_df = pd.read_excel(filepath)

        # Adding a 'language' column based on the 'Tweet_Content' column.
        def detect_language(text):
            try:
                return detect(text)
            except:
                return 'Unknown'
        
        tweets_df['language'] = tweets_df[Tweet_Content_column].apply(lambda x: detect_language(x) if pd.notnull(x) else 'Unknown')


        # Grouping by 'language', counting the occurrences, and sorting in descending order.
        language_counts = tweets_df.groupby('language')[Tweet_Content_column].count().sort_values(ascending=False)

        # Converting the Series to DataFrame for better visualization or further processing.
        language_counts_df = language_counts.reset_index(name='count')

        # Create a new DataFrame with the provided data
        tweet_volume_df = pd.DataFrame({'Language': language_counts_df['language'], 'Number of Posts': language_counts_df['count']})
        tweet_volume_df.set_index('Language', inplace=True)

        if plot == True:
                # Plotting
                fig, ax = plt.subplots(figsize=(10, 6))
                tweet_volume_df['Number of Posts'].plot(kind='bar', color='#FFCC00', ax=ax)

                # Set graph properties
                ax.set_facecolor('#191A19')
                fig.patch.set_facecolor('#191A19')

                # Set the title and labels
                ax.set_title('Posts by Language ', color='#FFCC00', fontsize=12, fontname='Sans-serif', weight='bold')
                ax.set_xlabel('Language', color='#CCCCCC', fontsize=12, fontname='Sans-serif')
                ax.set_ylabel('Number of Posts', color='#CCCCCC', fontsize=12, fontname='Sans-serif')

                ax.grid(True, color='#737373', linestyle='-', linewidth=1, axis='y')
                ax.tick_params(colors='#CCCCCC', labelsize=10)

                plt.xticks(rotation=0)
                plt.tight_layout()
                plt.savefig("Filtered_Post_Vol.svg") #Change the file type as needed
                plt.show()
        return tweet_volume_df
    