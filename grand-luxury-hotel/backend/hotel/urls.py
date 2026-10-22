from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views
router=DefaultRouter()
router.register("room-types",views.RoomTypeViewSet)
router.register("restaurant",views.RestaurantViewSet)
router.register("services",views.ServiceViewSet)
router.register("gallery",views.ImageViewSet)
router.register("reviews",views.ReviewViewSet)
router.register("bookings",views.BookingViewSet,basename="bookings")
urlpatterns=[path("",include(router.urls)),path("availability/",views.availability),
path("auth/register/",views.Register.as_view()),path("auth/login/",views.Login.as_view()),
path("auth/logout/",views.Logout.as_view()),path("auth/me/",views.me),
path("admin/stats/",views.stats),path("contact/",views.Contact.as_view())]
