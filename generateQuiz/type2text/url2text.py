# This script extracts text from Youtube video link and any other link that has content
# Currently supports Youtube and Websites

# base libs
import requests
import os
import re

# libs used to download Youtube audio file and convert to .mp3
from pytube import YouTube
from moviepy.editor import *

# libs used to scrape websites and extract specific text
from bs4 import BeautifulSoup
from langchain_text_splitters import HTMLHeaderTextSplitter

# OpenAI lib
from openai import OpenAI

# setting up OPENAI API client
client = OpenAI()

# Checks the url if it youtube link or not
def is_youtube_link(url):
    # Regular expression pattern to match YouTube video URLs
    youtube_pattern = r'(https?://)?(www\.)?(youtube\.com/|youtu\.be/)[\w-]+(&\S+)?'

    # Check if the URL matches the YouTube pattern
    if re.match(youtube_pattern, url):
        return True
    
    return False

# Function to download audio from a YouTube video
def yt2text(url):
    try:
        # download the audio file of the youtube video
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_file_path = audio_stream.download(output_path='quizGen/type2dbs/data/audios/',filename='audio', max_retries= 5)
        print("Audio downloaded successfully!")

        # Convert the downloaded audio to .mp3
        audio_clip = AudioFileClip(audio_file_path)
        audio_clip.write_audiofile("quizGen/type2dbs/data/audios/audio.mp3")
        audio_clip.close()

        print("Audio converted to .mp3 successfully!")

        audio_file= open("quizGen/type2dbs/data/audios/audio.mp3", "rb")
        transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
        )
        audio_file.close()
        
        os.remove("quizGen/type2dbs/data/audios/audio")
        print("Original file deleted successfully!")

        os.remove("quizGen/type2dbs/data/audios/audio.mp3")
        print("Audio clip deleted successfully!")

        return transcription.text

    except Exception as e:
        print("Error:", str(e))

def web2text(url):
    try:
        # Define headless browser agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Send a GET request to the URL with custom headers
        response = requests.get(url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Exclude specified tags from the parsing
            for tag in soup.find_all(['nav','footer', 'navbar','meta', 'head', 'script', 'iframe']):
                tag.decompose()

            # Get the modified HTML content after excluding specified tags
            html_content = soup.prettify() # Get HTML context of website

            headers_to_split_on = [
                ("div", ""),
            ]

            html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
            html_header_splits = html_splitter.split_text(html_content)
            context = [str(i.page_content) for i in html_header_splits]

            # Extract main content of bunch of text
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"""
                    extract text of main context without any alterations
                    {context[0]}
                    """}
                ]
            )
            

            return completion.choices[0].message.content
        else:
            print("Failed to fetch webpage. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None

def url2text(url):
    if is_youtube_link(url):
        context = yt2text(url)
        return context
    else:
        context = web2text(url)
        return context

