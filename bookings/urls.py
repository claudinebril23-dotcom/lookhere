from django.urls import path
from . import views
from .global_search import global_search_api

urlpatterns = [
    path('', views.home, name='home'),
    path('packages/', views.packages_view, name='packages'),
    path('gallery/', views.gallery, name='gallery'),
    path('about/', views.about, name='about'),
    path('book/', views.book, name='book'),
    path('payment/<str:ref_code>/', views.payment_upload, name='payment_upload'),
    path('booking/<str:ref_code>/', views.booking_detail, name='booking_detail'),
    path('receipt/<str:ref_code>/', views.receipt_view, name='receipt'),
    path('api/booked-times/', views.booked_times_api, name='booked_times_api'),
    path('api/book/', views.book_ajax, name='book_ajax'),
    path('api/notifications/', views.notifications_api, name='notifications_api'),
    path('api/notifications/mark-read/', views.notifications_mark_read, name='notifications_mark_read'),
    path('api/quick-settings/', views.quick_settings_api, name='quick_settings_api'),
    path('api/create-test-notification/', views.create_test_notification, name='create_test_notification'),
    path('api/package-prices/', views.package_prices_api, name='package_prices_api'),
    path('api/global-search/', global_search_api, name='global_search_api'),
    path('admin-reports/', views.admin_reports, name='admin_reports'),
    path('notification-debug/', views.notification_debug, name='notification_debug'),
]
