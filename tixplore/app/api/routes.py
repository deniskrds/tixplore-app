import json

from quart import Response, request
from tortoise.expressions import Q

from . import api_bp
from ..models import Users, TicketSites, Events


@api_bp.get('/login')
async def login() -> Response:
    query_params = request.args.to_dict()
    email = query_params.get('email')
    password = query_params.get('password')

    if email is not None and password is not None:
        user = await Users.get_or_none(email=email, password=password)

        if user:
            return Response(json.dumps({"is_success": True}), status=200, content_type='application/json')
        else:
            return Response(json.dumps({"is_success": False, 'message': 'Email or Password is wrong.'}), status=400,
                            content_type='application/json')

    else:
        return Response(json.dumps({"is_success": False, 'message': 'Unknown error occurred.'}), status=400,
                        content_type='application/json')


@api_bp.get('/get-events')
async def get_events() -> Response:
    query_params = request.args.to_dict()
    category = query_params.get('category')
    search_text = query_params.get('search_text')

    if category is not None:
        category_map = {
            'enerjik': ['macera'],
            'romantik': ['romantik', 'Tiyatro'],
            'eğlenceli': ['Stand Up'],
        }

        if category not in category_map and category != 'normal':
            return Response(json.dumps({"is_success": False, 'message': 'Invalid category.'}), status=400)

        try:
            filter_query = Q()
            if category != 'normal':
                for genre in category_map[category]:
                    filter_query |= Q(genre__icontains=genre)

            if search_text is not None:
                filter_query &= Q(name__icontains=search_text) | Q(description__icontains=search_text)

            movies = await Events.filter(filter_query)

            if len(movies) == 0:
                return Response(
                    json.dumps({"is_success": False, 'message': 'No movies found for this category.'}),
                    status=404, content_type='application/json'
                )

            movie_data = {}

            for movie in movies:
                # Initialize movie data if not already created
                if movie.id not in movie_data:
                    movie_data[movie.id] = {
                        "id": str(movie.id),  # Ensure the ID is a string
                        "name": movie.name,
                        "type": movie.type,
                        "genre": movie.genre.split(',') if movie.genre else [],
                        "location": movie.location,
                        "time": movie.time.split('T')[0],
                        "imageUrl": movie.image_url or '/api/placeholder/800/400',
                        "description": movie.description,
                        "director": movie.director,
                        "cast": movie.cast,
                        "duration": movie.duration,
                        "rating": movie.rating,
                        "ticket_sites": [],  # To store ticket sites
                        "isFavorite": movie.favorite
                    }

                # Fetch related ticket sites
                ticket_sites = await TicketSites.filter(event_id=movie.id).all()
                for ticket in ticket_sites:
                    movie_data[movie.id]["ticket_sites"].append({
                        "name": ticket.name,
                        "price": ticket.price,
                        "url": ticket.url
                    })

            # Return response with joined movie data
            return Response(
                json.dumps({"is_success": True, "data": list(movie_data.values())}),
                status=200, content_type='application/json'
            )
        except Exception as e:
            return Response(
                json.dumps({"is_success": False, 'message': 'An error occurred while fetching movies.'}),
                status=500, content_type='application/json'
            )
    else:
        return Response(
            json.dumps({"is_success": False, 'message': 'Category is not specified.'}),
            status=400, content_type='application/json'
        )


@api_bp.get('/favorites')
async def get_favorites() -> Response:
    query_params = request.args.to_dict()
    category = query_params.get('category')

    if True:
        try:
            favorite_events = await Events.filter(favorite=True).all()
            movie_data = {}

            for movie in favorite_events:
                if movie.id not in movie_data:
                    movie_data[movie.id] = {
                        "id": str(movie.id),
                        "name": movie.name,
                        "type": movie.type,
                        "location": movie.location,
                        "time": movie.time,
                        "imageUrl": movie.image_url or '/api/placeholder/800/400',
                        "description": movie.description,
                        "director": movie.director,
                        "cast": movie.cast,
                        "duration": movie.duration,
                        "rating": movie.rating,
                        "ticket_sites": [],
                        "isFavorite": movie.favorite
                    }

                # Fetch related ticket sites
                ticket_sites = await TicketSites.filter(event_id=movie.id).all()
                for ticket in ticket_sites:
                    movie_data[movie.id]["ticket_sites"].append({
                        "name": ticket.name,
                        "price": ticket.price,
                        "url": ticket.url
                    })

            # Return response with joined movie data
            return Response(
                json.dumps({"is_success": True, "data": list(movie_data.values())}),
                status=200, content_type='application/json'
            )
        except Exception as e:
            return Response(
                json.dumps({"is_success": False, 'message': 'An error occurred while fetching movies.'}),
                status=500, content_type='application/json'
            )


@api_bp.post('/set-favorite')
async def set_favorite() -> Response:
    query_params = request.args.to_dict()
    event_id = query_params.get('event_id')
    is_favorite = query_params.get('favorite')

    if event_id is not None and is_favorite is not None:
        try:
            event = await Events.get(id=event_id)
            if is_favorite.lower() == 'true':
                is_favorite = True
            else:
                is_favorite = False
            event.favorite = is_favorite
            await event.save()

            return Response(
                json.dumps({"is_success": True}),
                status=200, content_type='application/json'
            )
        except Exception as e:
            return Response(
                json.dumps({"is_success": False, 'message': 'An error occurred while setting favorite.'}),
                status=500, content_type='application/json'
            )
    else:
        return Response(
            json.dumps({"is_success": False, 'message': 'Event ID or is_favorite is not provided.'}),
            status=400, content_type='application/json'
        )

@api_bp.get('/register')
async def register_user():
    query_params = request.args.to_dict()
    email = query_params.get('email')
    password = query_params.get('password')
    name = query_params.get('name')

    if email is not None and password is not None:
        try:
            user = await Users.get_or_none(email=email)
            if user:
                return Response(
                    json.dumps({"is_success": False, 'message': 'User already exists.'}),
                    status=400, content_type='application/json'
                )

            await Users.create(email=email, password=password, name=name)
            return Response(
                json.dumps({"is_success": True}),
                status=200, content_type='application/json'
            )
        except Exception as e:
            return Response(
                json.dumps({"is_success": False, 'message': 'An error occurred while registering user.'}),
                status=500, content_type='application/json'
            )
    else:
        return Response(
            json.dumps({"is_success": False, 'message': 'Email or Password is not provided.'}),
            status=400, content_type='application/json'
        )

@api_bp.get('/ping')
async def health_check() -> Response:
    return Response("PONG", status=200)
