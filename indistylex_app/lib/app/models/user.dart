class User {
  final int id;
  final String firstName;
  final String lastName;
  final String email;
  final String? phone;
  final String? role;
  final String? oauthProvider;
  final DateTime? createdAt;

  User({
    required this.id,
    required this.firstName,
    required this.lastName,
    required this.email,
    this.phone,
    this.role,
    this.oauthProvider,
    this.createdAt,
    this.address,
    this.city,
    this.state,
    this.pincode,
  });

  String get fullName => '$firstName $lastName'.trim();
  String get name => fullName;

  // Address fields (filled from profile/address endpoint)
  String? address;
  String? city;
  String? state;
  String? pincode;

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? 0,
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'],
      role: json['role'],
      oauthProvider: json['oauth_provider'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
      address: json['address'],
      city: json['city'],
      state: json['state'],
      pincode: json['pincode'] ?? json['zip_code'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'first_name': firstName,
      'last_name': lastName,
      'email': email,
      'phone': phone,
    };
  }
}
