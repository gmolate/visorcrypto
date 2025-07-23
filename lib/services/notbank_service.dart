import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:visor_crypto/app/models/notbank/balance_notbank_model.dart';

class NotBankService {
  final String _baseUrl = 'api.notbank.exchange';

  Future<List<BalanceNotBank>> getBalances(
      String apiKey, String apiSecret) async {
    // This is the line that needs correction
    final url = Uri.https(_baseUrl, '/AP/GetAccountPositions');

    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/json',
        // NotBank authentication headers will be added here
      },
      body: json.encode({
        // NotBank authentication parameters will be added here
      }),
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => BalanceNotBank.fromJson(json)).toList();
    } else {
      throw Exception('Error al obtener balances de NotBank: ${response.body}');
    }
  }
}
