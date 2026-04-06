from django.urls import path
from .views import LogMoodView, TodayMoodView, MoodHistoryView, WeeklyStatsView, MonthlyStatsView

urlpatterns = [
    path('log/', LogMoodView.as_view(), name='log-mood'),
    path('today/', TodayMoodView.as_view(), name='today-mood'),
    path('history/', MoodHistoryView.as_view(), name='mood-history'),
    path('stats/weekly/', WeeklyStatsView.as_view(), name='weekly-stats'),
    path('stats/monthly/', MonthlyStatsView.as_view(), name='monthly-stats'),
]
