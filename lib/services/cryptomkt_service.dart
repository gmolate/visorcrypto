import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:visor_crypto/app/models/crypto_mkt/balance_cryptomkt_model.dart';

class CryptoMktService {
  final String _baseUrl = 'api.exchange.cryptomkt.com';

  Future<List<BalanceCryptoMkt>> getBalances(
      String apiKey, String apiSecret) async {
    // This is the line that needs correction
    final url = Uri.https(_baseUrl, '/v3/spot/balance');

    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $apiKey',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => BalanceCryptoMkt.fromJson(json)).toList();
    } else {
      throw Exception('Error al obtener balances de CryptoMKT: ${response.body}');
    }
  }
}
