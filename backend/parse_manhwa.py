import json
from bs4 import BeautifulSoup

# Read the HTML file
with open('output.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Initialize the metadata dictionary
metadata = {}

# ============ Extract Title ============
title_tag = soup.find('h1')
metadata['title'] = title_tag.get_text(strip=True) if title_tag else "N/A"

# ============ Extract Poster/Cover Image ============
poster_img = soup.find('img', {'class': 'img-responsive', 'fifu-featured': '1'})
metadata['poster'] = poster_img.get('src') if poster_img else poster_img.get('data-default-src') if poster_img else "N/A"

# ============ Extract Alternative Names ============
alt_section = soup.find('div', {'class': 'post-content_item'})
alternative_names = "N/A"
for item in soup.find_all('div', {'class': 'post-content_item'}):
    heading = item.find('h5')
    if heading and 'Alternative' in heading.get_text():
        alternative_names = item.find('div', {'class': 'summary-content'}).get_text(strip=True)
        break
metadata['alternative_names'] = alternative_names

# ============ Extract Author(s) ============
authors = []
for item in soup.find_all('div', {'class': 'post-content_item'}):
    heading = item.find('h5')
    if heading and 'Author' in heading.get_text():
        author_links = item.find_all('a')
        authors = [link.get_text(strip=True) for link in author_links]
        break
metadata['authors'] = authors if authors else ["N/A"]

# ============ Extract Artist(s) ============
artists = []
for item in soup.find_all('div', {'class': 'post-content_item'}):
    heading = item.find('h5')
    if heading and 'Artist' in heading.get_text():
        artist_links = item.find_all('a')
        artists = [link.get_text(strip=True) for link in artist_links]
        break
metadata['artists'] = artists if artists else ["N/A"]

# ============ Extract Release Date / Year Published ============
release_year = "N/A"
for item in soup.find_all('div', {'class': 'post-content_item'}):
    heading = item.find('h5')
    if heading and 'Release' in heading.get_text():
        release_text = item.find('a')
        if release_text:
            release_year = release_text.get_text(strip=True)
        break
metadata['year_published'] = release_year

# ============ Extract Status (Ongoing/Finished) ============
status = "N/A"
for item in soup.find_all('div', {'class': 'post-content_item'}):
    heading = item.find('h5')
    if heading and 'Status' in heading.get_text():
        status_div = item.find('div', {'class': 'summary-content'})
        if status_div:
            status = status_div.get_text(strip=True)
        break
metadata['status'] = status

# ============ Extract Type ============
publication_type = "N/A"
for item in soup.find_all('div', {'class': 'post-content_item'}):
    heading = item.find('h5')
    if heading and 'Type' in heading.get_text():
        type_div = item.find('div', {'class': 'summary-content'})
        if type_div:
            publication_type = type_div.get_text(strip=True)
        break
metadata['publication_type'] = publication_type

# ============ Extract Genres ============
genres = []
for item in soup.find_all('div', {'class': 'post-content_item'}):
    heading = item.find('h5')
    if heading and 'Genre' in heading.get_text():
        genre_links = item.find_all('a')
        genres = [link.get_text(strip=True) for link in genre_links]
        break
metadata['genres'] = genres if genres else ["N/A"]

# ============ Extract Tags ============
tags = []
for item in soup.find_all('div', {'class': 'post-content_item'}):
    heading = item.find('h5')
    if heading and 'Tag' in heading.get_text():
        tag_links = item.find_all('a')
        tags = [link.get_text(strip=True) for link in tag_links]
        break
metadata['tags'] = tags if tags else ["N/A"]

# ============ Extract Description/Summary ============
summary = "N/A"
description_div = soup.find('div', {'class': 'description-summary'})
if description_div:
    summary_text = description_div.find('div', {'class': 'summary__content'})
    if summary_text:
        # Get all text and clean it
        paragraphs = summary_text.find_all('p')
        summary = ' '.join([p.get_text(strip=True) for p in paragraphs])
metadata['description'] = summary

# ============ Extract Rating ============
rating = "N/A"
rating_span = soup.find('span', {'id': 'averagerate'})
if rating_span:
    rating = rating_span.get_text(strip=True)
metadata['rating'] = rating

# ============ Extract Total Votes/Number of Ratings ============
total_votes = "N/A"
votes_span = soup.find('span', {'id': 'countrate'})
if votes_span:
    total_votes = votes_span.get_text(strip=True)
metadata['total_ratings'] = total_votes

# ============ Extract Number of Chapters ============
chapters_list = []
chapter_links = soup.find_all('a', href=True)
for link in chapter_links:
    href = link.get('href')
    chapter_text = link.get_text(strip=True)
    # Filter for chapter links
    if '/chapter-' in href and chapter_text.startswith('Chapter'):
        chapters_list.append({
            'title': chapter_text,
            'url': href
        })

# Count chapters - find the highest chapter number
max_chapter = 0
for chapter in chapters_list:
    try:
        # Extract chapter number from "Chapter X - Title" format
        chapter_num = int(chapter['title'].split('-')[0].replace('Chapter', '').strip())
        if chapter_num > max_chapter:
            max_chapter = chapter_num
    except:
        pass

metadata['number_of_chapters'] = max_chapter if max_chapter > 0 else len(chapters_list)

# ============ Extract Published By ============
# This info is often in the site name, if not explicitly mentioned
metadata['published_by'] = "Manga District"

# ============ Extract All Chapters with Links ============
metadata['all_chapters'] = chapters_list

# ============ Create Clean JSON Output ============
manhwa_json = {
    'title': metadata.get('title'),
    'alternative_names': metadata.get('alternative_names'),
    'poster_url': metadata.get('poster'),
    'rating': metadata.get('rating'),
    'total_ratings': metadata.get('total_ratings'),
    'description': metadata.get('description'),
    'authors': metadata.get('authors'),
    'artists': metadata.get('artists'),
    'publication_type': metadata.get('publication_type'),
    'genres': metadata.get('genres'),
    'tags': metadata.get('tags'),
    'status': metadata.get('status'),
    'year_published': metadata.get('year_published'),
    'published_by': metadata.get('published_by'),
    'number_of_chapters': metadata.get('number_of_chapters'),
    'all_chapters': metadata.get('all_chapters')
}

# ============ Save to JSON file ============
with open('manhwa_metadata.json', 'w', encoding='utf-8') as f:
    json.dump(manhwa_json, f, indent=2, ensure_ascii=False)

# ============ Print the JSON to console ============
print(json.dumps(manhwa_json, indent=2, ensure_ascii=False))
print("\n✅ Metadata extracted successfully!")
print("📄 JSON file saved as: manhwa_metadata.json")
