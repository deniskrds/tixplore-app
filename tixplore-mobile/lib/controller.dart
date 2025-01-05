import 'dart:convert';
import 'dart:developer';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// const BaseURL = 'http://10.0.2.2:5000';
const BaseURL = 'http://127.0.0.1:5000';


class TicketSite {
  final String name;
  final double price;
  final String url;

  TicketSite({
    required this.name,
    required this.price,
    required this.url,
  });

  factory TicketSite.fromJson(Map<String, dynamic> json) {
    return TicketSite(
      name: json['name'],
      price: json['price'].toDouble(),
      url: json['url'],
    );
  }
}

class Event {
  final String id;
  final String name;
  final String type;
  final List<String> genre;
  final String location;
  final String time;
  final String imageUrl;
  final String description;
  final String director;
  final List<String> cast;
  final String duration;
  final double rating;
  final List<TicketSite> ticketSites;
  bool isFavorite;

  Event({
    required this.id,
    required this.name,
    required this.type,
    required this.genre,
    required this.location,
    required this.time,
    required this.imageUrl,
    required this.description,
    required this.director,
    required this.cast,
    required this.duration,
    required this.rating,
    required this.ticketSites,
    required this.isFavorite,
  });

  factory Event.fromJson(Map<String, dynamic> json) {

    return Event(
      id: json['id'],
      name: json['name'],
      type: json['type'],
      genre: List<String>.from(json['genre']),
      location: json['location'],
      time: json['time'],
      imageUrl: json['imageUrl'],
      description: json['description'],
      director: json['director'],
      cast: List<String>.from(json['cast']),
      duration: json['duration'],
      rating: json['rating'].toDouble(),
      isFavorite: json['isFavorite'],
      ticketSites: (json['ticket_sites'] as List)
          .map((site) => TicketSite.fromJson(site))
          .toList(),
    );
  }
}

class AppController extends ChangeNotifier {
  List<Event> _events = [];
  List<Event> _favorites = [];
  String _currentMood = 'normal';

  List<Event> get events => _events;
  List<Event> get favorites => _favorites;
  String get currentMood => _currentMood;

  Future<bool> login(String email, String password) async {
    try {
      const endpoint = '/login';
      final uri = Uri.parse('$BaseURL$endpoint').replace(
      queryParameters: {'email': email, 'password': password},
      );
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return true;
      }else{
        return false;
      }
    } catch (e) {
      print('Login error: $e');
      return false;
    }
  }
  Future<bool> register({required String name, required String email, required String password}) async {
    try {
      const endpoint = '/register';
      final uri = Uri.parse('$BaseURL$endpoint').replace(
      queryParameters: {'email': email, 'password': password, 'name': name},
      );
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return true;
      }else{
        return false;
      }
    } catch (e) {
      print('Login error: $e');
      return false;
    }
  }

  void logout() {
    notifyListeners();
  }

  // Event Methods
  Future<void> loadEvents(String category, String searchText) async {
    try {
      const endpoint = '/get-events';
      var queryParameters = {'category': category};

      if(searchText.trim().length > 0){
        queryParameters['search_text'] = searchText;
      }
      final uri = Uri.parse('$BaseURL$endpoint').replace(
        queryParameters: queryParameters,
      );
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        Map<String, dynamic> responseJson = json.decode(response.body);

        List<dynamic> eventsJson = responseJson["data"];

        log(eventsJson.toString());

        _events = eventsJson.map((eventJson) => Event.fromJson(eventJson)).toList();

        notifyListeners();
      } else {
        throw Exception('Failed to load events');
      }
    } catch (e) {
      print('Error loading events: $e');
    }
  }

  Future<void> setFavorite(event) async {
    try {
      final endpoint = '/set-favorite';
      final uri = Uri.parse('$BaseURL$endpoint').replace(
        queryParameters: {'event_id': event.id, "favorite" : event.isFavorite.toString()},
      );
      final response = await http.post(uri);

      if (response.statusCode == 200) {
        Map<String, dynamic> responseJson = json.decode(response.body);

        if (responseJson["success"]) {
          toggleFavorite(event.id);
        }
      } else {
        throw Exception('Failed to set favorite');
      }
    } catch (e) {
      print('Error setting favorite: $e');
    }
  }


  Future<void> loadFavorites() async {
    try {
      final endpoint = '/favorites';
      final uri = Uri.parse('$BaseURL$endpoint');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        Map<String, dynamic> responseJson = json.decode(response.body);

        List<dynamic> eventsJson = responseJson["data"];
        _favorites = eventsJson.map((eventJson) => Event.fromJson(eventJson)).toList();
        notifyListeners();
      } else {
        throw Exception('Failed to load favorites');
      }
    } catch (e) {
      print('Error loading events: $e');
    }
  }

  // Favorites Methods
  void toggleFavorite(String eventId) {
    final eventIndex = _events.indexWhere((e) => e.id == eventId);
    if (eventIndex != -1) {
      _events[eventIndex].isFavorite = !_events[eventIndex].isFavorite;

      if (_events[eventIndex].isFavorite) {
        _favorites.add(_events[eventIndex]);
      } else {
        _favorites.removeWhere((e) => e.id == eventId);
      }

      notifyListeners();
    }
  }

  List<Event> getFavorites() {
    return _favorites;
  }

  // Mood Methods
  void setMood(String mood) {
    _currentMood = mood;
    notifyListeners();
  }

  List<Event> getEventsByMood(String mood) {
    return _events.where((event) {
      switch (mood.toLowerCase()) {
        case 'happy':
          return ['Komedi', 'Müzikal', 'Konser'].contains(event.type);
        case 'sad':
          return ['Drama', 'Romantik'].contains(event.type);
        case 'excited':
          return ['Aksiyon', 'Macera', 'Konser'].contains(event.type);
        default:
          return true;
      }
    }).toList();
  }

  // Search Methods
  List<Event> searchEvents(String query) {
    if (query.isEmpty) return _events;

    return _events.where((event) {
      final nameMatch = event.name.toLowerCase().contains(query.toLowerCase());
      final typeMatch = event.type.toLowerCase().contains(query.toLowerCase());
      return nameMatch || typeMatch;
    }).toList();
  }
}