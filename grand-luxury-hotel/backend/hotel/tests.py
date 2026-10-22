from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from .models import RoomType,Room,Booking

class HotelTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username="hotelguest",password="secret12345")
        self.type=RoomType.objects.create(name="Test Suite",description="Test",price_per_night=500,capacity=2)
        Room.objects.create(room_type=self.type,number="501")
        self.client=APIClient();self.client.force_authenticate(user=self.user)
        self.start=timezone.localdate()+timedelta(days=7)
        self.data={"room_type":self.type.pk,"check_in":self.start.isoformat(),
                   "check_out":(self.start+timedelta(days=3)).isoformat(),
                   "guests":2,"guest_name":"A Guest","phone":"+998900000000"}
    def test_price_and_overlapping_bookings(self):
        result=self.client.post("/api/bookings/",self.data,format="json")
        self.assertEqual(result.status_code,201,result.data)
        self.assertEqual(result.data["total"],"1500.00")
        overlap={**self.data,"check_in":(self.start+timedelta(days=1)).isoformat()}
        self.assertEqual(self.client.post("/api/bookings/",overlap,format="json").status_code,409)
    def test_adjacent_stay_is_allowed(self):
        self.client.post("/api/bookings/",self.data,format="json")
        next_stay={**self.data,"check_in":(self.start+timedelta(days=3)).isoformat(),
                   "check_out":(self.start+timedelta(days=4)).isoformat()}
        self.assertEqual(self.client.post("/api/bookings/",next_stay,format="json").status_code,201)
    def test_cancel_releases_inventory(self):
        first=self.client.post("/api/bookings/",self.data,format="json")
        self.assertEqual(self.client.post("/api/bookings/"+str(first.data["id"])+"/cancel/").status_code,200)
        self.assertEqual(self.client.post("/api/bookings/",self.data,format="json").status_code,201)
    def test_guest_capacity(self):
        self.assertEqual(self.client.post("/api/bookings/",{**self.data,"guests":3},format="json").status_code,400)
    def test_staff_stats_not_public(self):
        self.assertEqual(self.client.get("/api/admin/stats/").status_code,403)
