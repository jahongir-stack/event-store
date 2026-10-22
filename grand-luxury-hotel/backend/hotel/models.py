import uuid
from django.conf import settings
from django.core.validators import MinValueValidator,MaxValueValidator
from django.db import models
from django.db.models import Q

class RoomType(models.Model):
    name=models.CharField(max_length=120,unique=True)
    description=models.TextField()
    image_url=models.URLField(blank=True)
    price_per_night=models.DecimalField(max_digits=12,decimal_places=2)
    capacity=models.PositiveIntegerField(validators=[MinValueValidator(1)])
    size_sqm=models.PositiveIntegerField(default=30)
    amenities=models.TextField(blank=True)
    active=models.BooleanField(default=True)
    def __str__(self): return self.name

class Room(models.Model):
    CLEAN="clean"
    DIRTY="dirty"
    SERVICE="maintenance"
    STATUSES=[(CLEAN,"Clean"),(DIRTY,"Dirty"),(SERVICE,"Maintenance")]
    number=models.CharField(max_length=12,unique=True)
    room_type=models.ForeignKey(RoomType,on_delete=models.PROTECT,related_name="rooms")
    floor=models.PositiveSmallIntegerField(default=1)
    housekeeping=models.CharField(max_length=12,choices=STATUSES,default=CLEAN)
    active=models.BooleanField(default=True)
    def __str__(self): return self.number

class SeasonRate(models.Model):
    room_type=models.ForeignKey(RoomType,on_delete=models.CASCADE,related_name="season_rates")
    start=models.DateField()
    end=models.DateField()
    multiplier=models.DecimalField(max_digits=4,decimal_places=2,validators=[MinValueValidator(0.1)])
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end<self.start: raise ValidationError("Invalid season date range.")

class PromoCode(models.Model):
    code=models.CharField(max_length=40,unique=True)
    percent=models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(100)])
    valid_until=models.DateField()
    active=models.BooleanField(default=True)
    def __str__(self): return self.code

class Booking(models.Model):
    HOLD="confirmed"
    CANCELLED="cancelled"
    STATUS=[(HOLD,"Confirmed"),(CANCELLED,"Cancelled")]
    reference=models.CharField(max_length=16,unique=True,editable=False,default=lambda_placeholder if False else "") # populated in save()
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="hotel_bookings")
    room=models.ForeignKey(Room,on_delete=models.PROTECT,related_name="bookings")
    check_in=models.DateField()
    check_out=models.DateField()
    guests=models.PositiveIntegerField(validators=[MinValueValidator(1)])
    guest_name=models.CharField(max_length=140)
    phone=models.CharField(max_length=50)
    total=models.DecimalField(max_digits=14,decimal_places=2)
    promo=models.ForeignKey(PromoCode,on_delete=models.SET_NULL,null=True,blank=True)
    status=models.CharField(max_length=12,choices=STATUS,default=HOLD)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-created_at"]
    def save(self,*args,**kwargs):
        if not self.reference: self.reference="GLH-"+uuid.uuid4().hex[:10].upper()
        super().save(*args,**kwargs)

class RestaurantItem(models.Model):
    name=models.CharField(max_length=120)
    category=models.CharField(max_length=50)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    def __str__(self):return self.name

class HotelService(models.Model):
    name=models.CharField(max_length=120)
    category=models.CharField(max_length=50)
    description=models.TextField()
    price=models.DecimalField(max_digits=12,decimal_places=2,default=0)

class RoomImage(models.Model):
    room_type=models.ForeignKey(RoomType,on_delete=models.CASCADE,related_name="images")
    url=models.URLField()
    caption=models.CharField(max_length=120,blank=True)

class Review(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    rating=models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment=models.TextField()
    approved=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

class ContactMessage(models.Model):
    name=models.CharField(max_length=120)
    email=models.EmailField()
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

class StaffProfile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    role=models.CharField(max_length=40,choices=[("frontdesk","Front desk"),("housekeeping","Housekeeping"),("manager","Manager")])
