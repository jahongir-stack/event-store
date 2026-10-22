from datetime import date,timedelta
from django.contrib.auth import authenticate,get_user_model
from django.db import transaction,IntegrityError
from django.db.models import Count,Sum
from django.utils import timezone
from rest_framework import generics,viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,permission_classes,action
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from .models import RoomType,Room,Booking,PromoCode,RestaurantItem,HotelService,RoomImage,Review
from .services import available_rooms,calculate_price
from .serializers import RoomTypeSerializer,BookingSerializer,RestaurantSerializer,ServiceSerializer,ImageSerializer,ReviewSerializer,ContactSerializer
from .notifications import alert

def parse_dates(data):
    try:
        check_in=date.fromisoformat(str(data.get("check_in","")))
        check_out=date.fromisoformat(str(data.get("check_out","")))
    except ValueError: raise ValueError("Invalid dates: YYYY-MM-DD required.")
    if check_in<timezone.localdate() or check_out<=check_in:
        raise ValueError("Checkout must follow check-in and check-in must not be past.")
    if (check_out-check_in).days>120: raise ValueError("Maximum stay is 120 nights.")
    return check_in,check_out

class Register(generics.GenericAPIView):
    permission_classes=[AllowAny]
    def post(self,request):
        username=str(request.data.get("username","")).strip()
        password=request.data.get("password","")
        email=str(request.data.get("email","")).strip()
        if len(username)<3 or len(password)<8:return Response({"detail":"Username >=3 and password >=8 characters required."},status=400)
        if get_user_model().objects.filter(username=username).exists():return Response({"detail":"Username exists."},status=400)
        user=get_user_model().objects.create_user(username=username,email=email,password=password)
        token,_=Token.objects.get_or_create(user=user)
        return Response({"token":token.key,"username":user.username},status=201)

class Login(generics.GenericAPIView):
    permission_classes=[AllowAny]
    def post(self,request):
        user=authenticate(username=request.data.get("username"),password=request.data.get("password"))
        if not user:return Response({"detail":"Wrong username or password."},status=400)
        token,_=Token.objects.get_or_create(user=user)
        return Response({"token":token.key,"username":user.username,"is_staff":user.is_staff})

class Logout(generics.GenericAPIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=204)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):return Response({"username":request.user.username,"is_staff":request.user.is_staff})

class RoomTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=RoomType.objects.filter(active=True)
    serializer_class=RoomTypeSerializer
    permission_classes=[AllowAny]

class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=RestaurantItem.objects.all()
    serializer_class=RestaurantSerializer
    permission_classes=[AllowAny]

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=HotelService.objects.all()
    serializer_class=ServiceSerializer
    permission_classes=[AllowAny]

class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=RoomImage.objects.all()
    serializer_class=ImageSerializer
    permission_classes=[AllowAny]

class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Review.objects.filter(approved=True)
    serializer_class=ReviewSerializer
    permission_classes=[AllowAny]

@api_view(["GET"])
@permission_classes([AllowAny])
def availability(request):
    try:
        check_in,check_out=parse_dates(request.query_params)
        guests=int(request.query_params.get("guests","1"))
        if guests<1:return Response({"detail":"At least one guest required."},status=400)
    except (ValueError,TypeError) as e:return Response({"detail":str(e)},status=400)
    types=RoomType.objects.filter(active=True,capacity__gte=guests)
    return Response([{**RoomTypeSerializer(t).data,"available_units":available_rooms(t,check_in,check_out).count(),
                      "stay_price":str(calculate_price(t,check_in,check_out))} for t in types])

class BookingViewSet(viewsets.GenericViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=BookingSerializer
    def get_queryset(self):
        qs=Booking.objects.select_related("room","room__room_type")
        return qs if self.request.user.is_staff else qs.filter(user=self.request.user)
    def list(self,request):return Response(self.get_serializer(self.get_queryset(),many=True).data)
    def retrieve(self,request,pk=None):return Response(self.get_serializer(self.get_object()).data)
    def create(self,request):
        data=request.data
        try:
            check_in,check_out=parse_dates(data)
            room_type=RoomType.objects.get(pk=int(data.get("room_type")),active=True)
            guests=int(data.get("guests",1))
            if guests<1 or guests>room_type.capacity:raise ValueError("Guests exceed room capacity.")
            guest_name=str(data.get("guest_name","")).strip()
            phone=str(data.get("phone","")).strip()
            if not guest_name or not phone:raise ValueError("Guest name and phone are required.")
            promo=None
            if data.get("promo_code"):
                promo=PromoCode.objects.filter(code__iexact=str(data["promo_code"]).strip(),active=True,valid_until__gte=timezone.localdate()).first()
                if not promo:raise ValueError("Invalid or expired promo code.")
        except (ValueError,TypeError,RoomType.DoesNotExist) as exc:return Response({"detail":str(exc)},status=400)
        try:
            with transaction.atomic():
                # PostgreSQL serializes allocation per room type by locking its parent row.
                # This ensures two simultaneous requests cannot assign the same physical room.
                RoomType.objects.select_for_update().get(pk=room_type.pk)
                room=available_rooms(room_type,check_in,check_out).first()
                if not room:return Response({"detail":"No rooms available for these dates."},status=409)
                price=calculate_price(room_type,check_in,check_out,promo)
                booking=Booking.objects.create(user=request.user,room=room,check_in=check_in,check_out=check_out,
                                               guests=guests,guest_name=guest_name,phone=phone,promo=promo,total=price)
                transaction.on_commit(lambda:alert("Hotel booking "+booking.reference+" · "+str(booking.total)+" UZS"))
        except IntegrityError:return Response({"detail":"Room allocation conflict. Retry."},status=409)
        return Response(self.get_serializer(booking).data,status=201)
    @action(detail=True,methods=["post"])
    def cancel(self,request,pk=None):
        booking=self.get_object()
        if booking.status!="confirmed" or booking.check_in<=timezone.localdate()+timedelta(days=1):
            return Response({"detail":"Cancellation only possible more than 24h before check-in (calendar day policy)."},status=400)
        booking.status="cancelled"
        booking.save(update_fields=["status"])
        return Response({"status":"cancelled"})

@api_view(["GET"])
@permission_classes([IsAdminUser])
def stats(request):
    today=timezone.localdate()
    confirmed=Booking.objects.filter(status="confirmed")
    rooms=Room.objects.filter(active=True)
    return Response({"rooms":rooms.count(),"occupied_today":confirmed.filter(check_in__lte=today,check_out__gt=today).count(),
                     "check_ins_today":confirmed.filter(check_in=today).count(),
                     "check_outs_today":confirmed.filter(check_out=today).count(),
                     "bookings":confirmed.count(),
                     "recorded_booking_value":str(confirmed.aggregate(x=Sum("total"))["x"] or 0),
                     "dirty_rooms":rooms.filter(housekeeping="dirty").count()})

class Contact(generics.CreateAPIView):
    permission_classes=[AllowAny]
    serializer_class=ContactSerializer
