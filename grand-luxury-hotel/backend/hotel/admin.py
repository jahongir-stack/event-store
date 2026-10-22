from django.contrib import admin
from .models import RoomType,Room,SeasonRate,PromoCode,Booking,RestaurantItem,HotelService,RoomImage,Review,ContactMessage,StaffProfile

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display=["number","room_type","floor","housekeeping","active"]
    list_filter=["room_type","housekeeping","active"]
    search_fields=["number"]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display=["reference","guest_name","room","check_in","check_out","total","status"]
    list_filter=["status","check_in","room__room_type"]
    search_fields=["reference","guest_name","phone","user__username"]
    readonly_fields=["reference","total","created_at"]
    def has_add_permission(self,request):return False  # bookings created via validated service
    def has_change_permission(self,request,obj=None):return False # prevent unsafe date edits

admin.site.register(RoomType)
admin.site.register(SeasonRate)
admin.site.register(PromoCode)
admin.site.register(RestaurantItem)
admin.site.register(HotelService)
admin.site.register(RoomImage)
admin.site.register(Review)
admin.site.register(ContactMessage)
admin.site.register(StaffProfile)
admin.site.site_header="Grand Luxury Hotel | Operations"
