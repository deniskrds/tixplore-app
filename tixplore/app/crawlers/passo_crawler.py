import asyncio

import requests
from typing import Dict, List, Optional
import json
from datetime import datetime
from tortoise import Model, fields

from app import init_tortoise
from app.models import Events, TicketSites


class PassoCrawler:
    def __init__(self):
        self.base_url = "https://ticketingweb.passo.com.tr/api/passoweb"
        self.web_url = "https://www.passo.com.tr"
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'text/plain',
            'CurrentCulture': 'tr-TR',
            'Origin': 'https://www.passo.com.tr',
            'Referer': 'https://www.passo.com.tr/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }

    def get_venues(self) -> List[Dict]:
        """Get list of all venues"""
        # You would need to implement this based on how venues can be discovered
        # This could be from a sitemap, main page, or another API endpoint
        # For now, we'll return a list of discovered venues from the example data
        return [
            {
                'id': venue_id,
                'seo_url': f"{venue_seo_url}",
                'name': venue_name
            }
            for venue_id, venue_seo_url, venue_name in self._extract_venues_from_data()
        ]

    def _extract_venues_from_data(self) -> List[tuple]:
        """Extract venue information from the example data"""
        # This would normally come from an API endpoint or web page
        # For now, we'll extract it from the example response
        venue_data = {
            'venueID': 306216,
            'venueSeoUrl': 'volkswagen-arena-etkinlik-biletleri',
            'venueName': 'Volkswagen Arena'
        }
        return [(venue_data['venueID'], venue_data['venueSeoUrl'], venue_data['venueName'])]

    def get_venue_details(self, venue_seo_url: str, venue_id: str, culture_id: str = "118") -> Dict:
        """Get venue details including events"""
        url = f"{self.base_url}/getvenuedetails/{venue_seo_url}/{venue_id}/{culture_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_event_details(self, event_seo_url: str, event_id: str, culture_id: str = "118") -> Dict:
        """Get detailed information about a specific event"""
        url = f"{self.base_url}/geteventdetails/{event_seo_url}/{event_id}/{culture_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def parse_event(self, event_data: Dict) -> Dict:
        """Parse event data into the format matching our Events model"""
        value = event_data.get('value', {})

        # Extract ticket categories/prices
        ticket_sites_data = [
            {
                'name': category.get('name', ''),
                'price': category.get('price', 0.0),
                'url': f"{self.web_url}/tr/{value.get('seoUrl', '')}"
            }
            for category in value.get('categories', [])
        ]

        # Parse description and remove HTML tags
        description = value.get('detailPageDescription', '').replace('<p>', '').replace('</p>', '\n')

        # Create event data
        event_data = {
            'name': value.get('name', ''),
            'type': value.get('genreName', ''),
            'genre': value.get('subGenreName', ''),
            'location': value.get('venueName', ''),
            'time': value.get('date', ''),
            'image_url': value.get('detailPageImageName', ''),
            'description': description,
            'director': '',  # Not available in the API
            'cast': [],  # Not available in the API
            'duration': f"{value.get('endDate', '')} - {value.get('date', '')}" if value.get('endDate') else '',
            'rating': 0.0,  # Not available in the API
            'favorite': False,
            'ticket_sites_data': ticket_sites_data
        }

        return event_data

    async def save_event(self, event_data: Dict):
        """Save event and its ticket sites to database"""
        # Extract ticket sites data before removing it from event_data
        ticket_sites_data = event_data.pop('ticket_sites_data', [])

        # Create or update event
        try:

            event, created = await Events.get_or_create(
                defaults=event_data
            )
        except Exception as e:
            print(f"Error saving event {event_data['name']}: {str(e)}")
            return
        if not created:
            await event.update_from_dict(event_data).save()

        # Create or update ticket sites
        for ticket_data in ticket_sites_data:
            await TicketSites.get_or_create(
                event=event,
                name=ticket_data['name'],
                defaults={
                    'price': ticket_data['price'],
                    'url': ticket_data['url']
                }
            )

    async def crawl_venue(self, venue: Dict):
        """Crawl all events from a venue"""
        try:
            # Get venue details with all events
            venue_data = self.get_venue_details(venue['seo_url'], str(venue['id']))

            if venue_data.get('isError'):
                print(f"Error fetching venue data for {venue['name']}: {venue_data}")
                return

            # Process each event
            for event in venue_data.get('value', {}).get('venueEvents', []):
                try:
                    # Get detailed event information
                    event_details = self.get_event_details(
                        event['seoUrl'],
                        str(event['id'])
                    )

                    if event_details.get('isError'):
                        print(f"Error fetching event {event['id']}: {event_details}")
                        continue

                    # Parse and save event data
                    event_data = self.parse_event(event_details)
                    await self.save_event(event_data)
                    print(f"Successfully processed event: {event['name']}")

                except Exception as e:
                    print(f"Error processing event {event['id']}: {str(e)}")

        except Exception as e:
            print(f"Error processing venue {venue['name']}: {str(e)}")

    async def crawl_all(self):
        """Crawl all venues and their events"""
        venues = self.get_venues()
        for venue in venues:
            print(f"Crawling venue: {venue['name']}")
            await self.crawl_venue(venue)


async def main():
    await init_tortoise()
    crawler = PassoCrawler()
    await crawler.crawl_all()


if __name__ == '__main__':
    asyncio.run(main())