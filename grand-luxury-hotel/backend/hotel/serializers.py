from rest_framework import serializers
from .models import RoomType,Room,Booking,RestaurantItem,HotelService,RoomImage,Review,ContactMessage

class RoomTypeSerializer(serializers.ModelSerializer):
    available_units=serializers.IntegerField(read_only=True,required=False)
    class Meta:
        model=RoomType
        fields=["id","name","description","image_url","price_per_night","capacity","size_sqm","amenities","available_units"]

class RoomSerializer(serializers.ModelSerializer):
    class Meta: model=Room;fields=["id","number","room_type","floor","housekeeping"]

class BookingSerializer(serializers.ModelSerializer):
    room_type=serializers.CharField(source="room.room_type.name",read_only=True)
    class Meta:
        model=Booking
        fields=["id","reference","room","room_type","check_in","check_out","guests","guest_name","phone","promo","total","status","created_at"]
        read_only_fields=["id","reference","room","room_type","total","status","created_at"]
        extra_kwargs={"promo":{"required":False}}

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:model=RestaurantItem;fields="__all__"
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:model=HotelService;fields="__all__"
class ImageSerializer(serializers.ModelSerializer):
    class Meta:model=RoomImage;fields="__all__"
class ReviewSerializer(serializers.ModelSerializer):
    guest=serializers.CharField(source="user.username",read_only=True)
    class Meta:model=Review;fields=["id","rating","comment","guest","created_at"]
class ContactSerializer(serializers.ModelSerializer):
    class Meta:model=ContactMessage;fields=["name","email","message"]
