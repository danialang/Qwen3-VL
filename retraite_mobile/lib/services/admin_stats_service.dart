import '../core/api_client.dart';

class AdminOverview {
  final int year;
  final int month;
  final int reservationsThisMonth;
  final double revenueThisMonthFcfa;
  final double revenueUpcomingFcfa;
  final double revenueYearFcfa;
  final List<double> revenueByMonth;
  final int pendingReservationsCount;
  final Map<String, double> occupancyRateThisMonthPercent;

  AdminOverview({
    required this.year,
    required this.month,
    required this.reservationsThisMonth,
    required this.revenueThisMonthFcfa,
    required this.revenueUpcomingFcfa,
    required this.revenueYearFcfa,
    required this.revenueByMonth,
    required this.pendingReservationsCount,
    required this.occupancyRateThisMonthPercent,
  });

  factory AdminOverview.fromJson(Map<String, dynamic> json) => AdminOverview(
        year: json['year'] as int,
        month: json['month'] as int,
        reservationsThisMonth: json['reservations_this_month'] as int,
        revenueThisMonthFcfa: double.parse(json['revenue_this_month_fcfa'].toString()),
        revenueUpcomingFcfa: double.parse(json['revenue_upcoming_fcfa'].toString()),
        revenueYearFcfa: double.parse(json['revenue_year_fcfa'].toString()),
        revenueByMonth: (json['revenue_by_month'] as List).map((v) => double.parse(v.toString())).toList(),
        pendingReservationsCount: json['pending_reservations_count'] as int,
        occupancyRateThisMonthPercent: (json['occupancy_rate_this_month_percent'] as Map<String, dynamic>)
            .map((key, value) => MapEntry(key, double.parse(value.toString()))),
      );
}

class AdminStatsService {
  final ApiClient api;
  AdminStatsService(this.api);

  Future<AdminOverview> getOverview() async {
    final json = await api.get('/admin/stats') as Map<String, dynamic>;
    return AdminOverview.fromJson(json);
  }
}
