import asyncio
import base64
import html
import json
import requests
from bs4 import BeautifulSoup
from app import init_tortoise
from app.models import Events, TicketSites


class Bubilet_Crawler:

    def get_latest_tickets(self, ilid = None):
        headers = {}
        if ilid is not None:
            headers['ilid'] = ilid

        r = requests.get('https://apiv2.bubilet.com.tr/api/Anasayfa/6/Etkinlikler', headers=headers)
        return r.json()
    
    def get_ticket_cities_and_counts(self):
        r = requests.get('https://apiv2.bubilet.com.tr/api/etkinlik/EtkinlikSehirleri')
        return r.json()

    def get_places_of_ticket(self, ticketId, ilid = None):
        headers = {}
        if ilid is not None:
            headers['ilid'] = ilid

        r = requests.get('https://apiv2.bubilet.com.tr/api/Etkinlik/'+str(ticketId)+'/Mekanlar', headers=headers)
        return r.json()
    

    def get_details_of_ticket(self, ticketSlug, ilid = None):
        headers = {}
        if ilid is not None:
            headers['ilid'] = ilid

        r = requests.get('https://apiv2.bubilet.com.tr/api/Etkinlik/Slug/'+ticketSlug, headers=headers)
        return r.json()
    
    
    def get_prices_of_ticket(self, ticketId, ilid = None):
        headers = {}
        if ilid is not None:
            headers['ilid'] = ilid

        r = requests.get('https://apiv2.bubilet.com.tr/api/Etkinlik/'+str(ticketId)+'/sessions/all', headers=headers)
        encrypted_res = r.json() 
        return decyrpt_price(encrypted_res)['data']
    
    def get_genres_of_ticket(self, ticketId, ilid = None):
        headers = {}
        if ilid is not None:
            headers['ilid'] = ilid

        r = requests.get('https://apiv2.bubilet.com.tr/api/Etkinlik/'+str(ticketId)+'/Etiket', headers=headers)
        return r.json()


# js decrypt function
# decrypt(g) {
#     const V = g._d
#       , de = g._v / 7;
#     if (V.length === de)
#         return {};
#     const at = V.slice(de, V.length)
#       , E = atob(at)
#       , te = new Uint8Array(E.length);
#     for (let Ne = 0; Ne < E.length; Ne++)
#         te[Ne] = E.charCodeAt(Ne);
#     const H = new TextDecoder("utf-8").decode(te);
#     return JSON.parse(H)
# }


def decyrpt_price(g):
    # Access properties
    V = g["_d"]
    de = g["_v"] / 7

    # Check for valid encoding
    if len(V) == de:
        return {}

    # Extract the encoded part
    at = V[int(de):]
    # Decode the Base64 string
    E = base64.b64decode(at).decode("utf-8")

    # Convert to byte array
    te = bytearray(E, "utf-8")

    # Decode the UTF-8 string
    H = te.decode("utf-8")

    # Parse JSON and return
    return json.loads(H)


async def main():
    await  init_tortoise()

    async def save_database(movie):
        name = movie['etkinlikAdi']

        event = await Events.filter(name=name).first()

        if event is None:
            typevar = movie['genres'][0]['adi']
            location = movie['places'][0]['baslik']
            genre = ','.join([genre['adi'] for genre in movie['genres']])
            time = movie['prices'][0]['sessions'][0]['tarih'].split('T')[0]
            image_url= next((('https://cdn.bubilet.com.tr' + e['url']) for e in (movie['details']['dosyalar']) if e['gosterimYeri'] == 'dikeyResim'), '')
            description = BeautifulSoup(html.unescape(html.unescape(movie['details']['ozet'])), "html.parser").get_text()
            director = ''
            cast = []
            duration = movie['details']['sure']
            rating = 0
            favorite = False

            event = await Events.create(
                name=name,
                type=typevar,
                location=location,
                time=time,
                image_url=image_url,
                description=description,
                director=director,
                cast=cast,
                duration=duration,
                rating=rating,
                genre=genre,
                favorite=favorite
            )

        source = 'bubilet.com'
        price = movie['prices'][0]['sessions'][0]['indirimliFiyat']
        url = 'https://www.bubilet.com.tr/istanbul/etkinlik/' + movie['slug']
        event_id = event.id

        await TicketSites.create(
            name=source,
            price=price,
            url=url,
            event_id=event_id
        )

    crawler = Bubilet_Crawler()

    latest = crawler.get_latest_tickets(str(34))

    result = []

    print(len(latest))

    for index, ticket in enumerate(latest):
        print(index, ticket['slug'])
        ticket['places'] = crawler.get_places_of_ticket(ticket['etkinlikId'], str(34))
        # time.sleep(5 * random.random())
        ticket['details'] = crawler.get_details_of_ticket(ticket['slug'])
        # time.sleep(5 * random.random())
        ticket['prices'] = crawler.get_prices_of_ticket(ticket['etkinlikId'], str(34))
        # time.sleep(5 * random.random())
        ticket['genres'] = crawler.get_genres_of_ticket(ticket['etkinlikId'], str(34))
        # time.sleep(5 * random.random())
        await save_database(ticket)

        result.append(ticket)

    #
    # with open("bubilet_result.json", "w") as file:
    #     json.dump(result, file, indent=4)


if __name__ == '__main__':
    asyncio.run(main())




