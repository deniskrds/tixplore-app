import 'package:flutter/material.dart';

class TicketAI {
  static String getMoodRecommendation(String mood) {
    switch (mood.toLowerCase()) {
      case 'enerjikkkk':
        return "🔋 Size enerjik etkinlikler gösteriliyor! Konserler ve hareketli etkinlikler...";
      case 'romantik':
        return "❤️ Romantik bir atmosfer için öneriler hazırlandı...";
      case 'eğlenceli':
        return "🎉 Eğlenceli vakit geçirmeniz için etkinlikler seçildi...";
      default:
        return "✨ Tüm etkinlikleri keşfedin...";
    }
  }
}

class AIStatusCard extends StatelessWidget {
  final String currentMood;

  const AIStatusCard({
    Key? key,
    required this.currentMood,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16.0),
      color: Colors.blue[50],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.psychology, color: Colors.blue, size: 24),
                SizedBox(width: 8),
                Text(
                  "AI Asistanı",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                  ),
                ),
              ],
            ),
            const Divider(),
            Text(
              TicketAI.getMoodRecommendation(currentMood),
              style: const TextStyle(
                fontSize: 16,
                color: Colors.black87,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class AIMoodSelector extends StatelessWidget {
  final Function(String) onMoodSelected;

  const AIMoodSelector({
    Key? key,
    required this.onMoodSelected,
  }) : super(key: key);

  void _showMoodDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Nasıl hissediyorsunuz?'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildMoodOption(context, 'enerjik', '🔋'),
            _buildMoodOption(context, 'romantik', '❤️'),
            _buildMoodOption(context, 'eğlenceli', '🎉'),
          ],
        ),
      ),
    );
  }

  ListTile _buildMoodOption(BuildContext context, String mood, String emoji) {
    return ListTile(
      leading: Text(emoji, style: const TextStyle(fontSize: 24)),
      title: Text(mood),
      onTap: () {
        Navigator.pop(context);
        onMoodSelected(mood);
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton(
      onPressed: () => _showMoodDialog(context),
      child: const Icon(Icons.psychology),
      tooltip: 'AI Asistanı',
    );
  }
}
