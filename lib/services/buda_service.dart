import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:http/http.dart' as http;
// Make sure this import path is correct for your project structure
import 'package:visor_crypto/app/models/buda/balance_buda_model.dart'; 

class BudaService {
  final String _baseUrl = 'https://www.buda.com';

  Future<List<Balance>> getBalances(String apiKey, String apiSecret) async {
    final nonce = DateTime.now().millisecondsSinceEpoch.toString();
    const path = '/api/v2/balances';
    const method = 'GET';

    final secretBytes = utf8.encode(apiSecret);
    final hmacSha384 = Hmac(sha384, secretBytes);

    // Corrected dataToSign
    final dataToSign = '$method $path $nonce'; 
    final signatureBytes = utf8.encode(dataToSign);
    final signature = hmacSha384.convert(signatureBytes);

    // ---- TEMPORARY LOGGING START ----
    print('--- BUDA.COM AUTH DEBUG START ---');
    print('Timestamp: ${DateTime.now().toIso8601String()}');
    print('Nonce: $nonce');
    print('Method: $method');
    print('Path: $path');
    print('Data to Sign: "$dataToSign"'); // Enclose dataToSign in quotes to see spaces clearly
    print('Generated Signature (Hex): ${signature.toString()}');
    // Showing only the start of the API key for security, if it's ever accidentally fully logged.
    print('API Key (first 5 chars): ${apiKey.substring(0, apiKey.length > 5 ? 5 : apiKey.length)}...');
    print('--- BUDA.COM AUTH DEBUG END ---');
    // ---- TEMPORARY LOGGING END ----

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
      // Log the actual error response from Buda if the request fails
      print('BUDA DEBUG: Error Response Status Code: ${response.statusCode}');
      print('BUDA DEBUG: Error Response Body: ${response.body}'); 
      throw Exception('Error al obtener balances: ${response.body}');
    }
  }
}
