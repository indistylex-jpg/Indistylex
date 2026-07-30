/// Basic input sanitization to reduce injection/XSS in user inputs.
class InputSanitizer {
  static final _unsafe = RegExp(r'''[<>"';\\]''');

  static String clean(String input, {int maxLength = 200}) {
    var value = input.trim();
    if (value.length > maxLength) {
      value = value.substring(0, maxLength);
    }
    return value.replaceAll(_unsafe, '');
  }

  static bool isValidEmail(String email) {
    return RegExp(r'^[\w\.\-]+@([\w\-]+\.)+[a-zA-Z]{2,}$').hasMatch(email);
  }

  static bool isValidPhone(String phone) {
    return RegExp(r'^[6-9]\d{9}$').hasMatch(phone.replaceAll(RegExp(r'\s'), ''));
  }

  static bool isValidPincode(String pincode) {
    return RegExp(r'^\d{6}$').hasMatch(pincode);
  }
}
