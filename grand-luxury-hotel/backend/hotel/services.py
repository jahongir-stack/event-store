from datetime import timedelta
from decimal import Decimal
from django.db.models import Q
from .models import Room,Booking,SeasonRate,PromoCode

def available_rooms(room_type,check_in,check_out):
    overlapping=Booking.objects.filter(status="confirmed",check_in__lt=check_out,check_out__gt=check_in).values("room_id")
    return Room.objects.filter(room_type=room_type,active=True).exclude(housekeeping="maintenance").exclude(id__in=overlapping).order_by("id")

def calculate_price(room_type,check_in,check_out,promo=None):
    total=Decimal("0")
    day=check_in
    while day<check_out:
        rates=SeasonRate.objects.filter(room_type=room_type,start__lte=day,end__gte=day).order_by("-multiplier")
        rate=rates.first()
        total+=room_type.price_per_night*(rate.multiplier if rate else Decimal("1"))
        day+=timedelta(days=1)
    if promo:
        total=total*(Decimal("100")-Decimal(promo.percent))/Decimal("100")
    return total.quantize(Decimal("0.01"))
