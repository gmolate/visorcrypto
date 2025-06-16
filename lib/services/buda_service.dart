import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:http/http.dart' as http;
import 'package:visor_crypto/app/models/buda/balance_buda_model.dart';

class BudaService {
  final String _baseUrl = 'https://www.buda.com';

  Future<List<Balance>> getBalances(String apiKey, String apiSecret) async {
    final nonce = DateTime.now().millisecondsSinceEpoch.toString();
    const path = '/api/v2/balances';
    const method = 'GET';
    const encodedBody = ''; // No body for GET request

    final secretBytes = utf8.encode(apiSecret);
    final hmacSha384 = Hmac(sha384, secretBytes);

    // This is the line that needs correction
    final dataToSign = '$method $path $nonce';
    final signatureBytes = utf8.encode(dataToSign);
    final signature = hmacSha384.convert(signatureBytes);

    final url = Uri.parse('$_baseUrl$path');
    final response = await http.get(
      url,
      headers: {
        'X-SBTC-APIKEY': apiKey,
        'X-SBTC-NONCE': nonce,
        'X-SBTC-SIGNATURE': signature.toString(),
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final balanceBuda = BalanceBuda.fromJson(json.decode(response.body));
      return balanceBuda.balances;
    } else {
      throw Exception('Error al obtener balances: ${response.body}');
    }
  }
}
