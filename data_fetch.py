import json
import aiohttp
import asyncio
from tqdm import tqdm

# Define the cities and their coordinates
cities = {
    "Berlin": [(52.5200, 13.4050), (52.5400, 13.4050)],
    "Stockholm": [(59.3293, 18.0686), (59.3493, 18.0686)],
    "Klaipeda": [(55.7033, 21.1443)],
    "Tokyo": [(35.6895, 139.6917), (35.7095, 139.7317)]
}

# Function to fetch places of interest for a given city
async def fetch_places_of_interest(session, city, coordinates):
    places = []
    for lat, lon in coordinates:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=geosearch&gsradius=10000&gscoord={lat}|{lon}&gslimit=500"
        async with session.get(url) as response:
            data = await response.json()
            if 'query' in data and 'geosearch' in data['query']:
                for item in data['query']['geosearch']:
                    place = {
                        'city': city,
                        'title': item.get('title', 'Unknown'),
                        'lat': item.get('lat', 0.0),
                        'lon': item.get('lon', 0.0),
                        'type': 'Unknown',  # Placeholder for POI type
                        'description': 'Unknown'  # Placeholder for description
                    }
                    places.append(place)
    return places

# Function to fetch additional details of a POI
async def fetch_poi_details(session, place):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={place['title']}&prop=pageimages|extracts&exintro&explaintext&format=json&pithumbsize=500"
    try:
        async with session.get(url) as response:
            data = await response.json()
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_info in pages.items():
                if 'extract' in page_info:
                    place['description'] = page_info['extract'].split('.')[0] + '.'  # Take the first sentence
                if 'pageprops' in page_info and 'wikibase-shortdesc' in page_info['pageprops']:
                    place['type'] = page_info['pageprops']['wikibase-shortdesc']
                if 'thumbnail' in page_info:
                    place['image_url'] = page_info['thumbnail']['source']
            return place
    except Exception as e:
        print(f"Error fetching details for {place['title']}: {e}")
        return place

# Main function
async def main():
    async with aiohttp.ClientSession() as session:
        images_data = {}
        # Iterate through each city
        for city, coordinates in cities.items():
            print(f"Fetching images for {city}...")
            places = await fetch_places_of_interest(session, city, coordinates)
            # Fetch additional details for each place
            tasks = [fetch_poi_details(session, place) for place in places]
            places_with_details = await asyncio.gather(*tasks)
            images_data[city] = []
            # Initialize progress bar for the current city
            progress_bar = tqdm(total=len(places_with_details), unit="place")
            for place in places_with_details:
                if place.get('image_url'):
                    images_data[city].append({
                        'title': place['title'],
                        'image_url': place['image_url'],
                        'description': place['description'],
                        'colours_RGB': []
                    })
                # Update progress bar
                progress_bar.update(1)
            # Close progress bar for the current city
            progress_bar.close()
            print(f"Completed fetching images for {city}")
        # Save images data to a JSON file
        with open('images_data.json', 'w') as file:
            json.dump(images_data, file)
        print("Images data saved to images_data.json")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
