from django.core.management.base import BaseCommand
from hotel.models import RoomType,Room,HotelService,RestaurantItem,RoomImage
class Command(BaseCommand):
    help="Create sample hotel inventory"
    def handle(self,*args,**kwargs):
        specs=[
            ("Standard Room",650000,2,28,"King bed, Wi-Fi, smart TV","https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=1400"),
            ("Deluxe Room",1100000,2,39,"City view, rain shower, breakfast","https://images.unsplash.com/photo-1590490360182-c33d57733427?w=1400"),
            ("Executive Suite",1800000,3,62,"Separate lounge, espresso bar","https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=1400"),
            ("Family Suite",2400000,5,83,"Two bedrooms, family amenities","https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=1400"),
            ("Presidential Suite",7200000,4,210,"Private terrace, butler service, panoramic lounge","https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=1400")]
        for index,(name,price,capacity,size,amenities,image) in enumerate(specs):
            typ,_=RoomType.objects.update_or_create(name=name,defaults={"price_per_night":price,"capacity":capacity,"size_sqm":size,"amenities":amenities,"description":"Exceptional comfort, elevated hospitality and signature five-star service.","image_url":image})
            RoomImage.objects.get_or_create(room_type=typ,url=image,defaults={"caption":name})
            for i in range(1,5):Room.objects.get_or_create(number=str(index+1)+str(i).zfill(2),defaults={"room_type":typ,"floor":index+1})
        for name,category,desc,price in [("Signature massage","Spa","Professional full-body massage",350000),("Swimming pool","Wellness","Indoor heated pool",0),("Fitness studio","Fitness","Premium equipment and trainers",0)]:
            HotelService.objects.update_or_create(name=name,defaults={"category":category,"description":desc,"price":price})
        for name,category,price in [("Chef's tasting menu","Dinner",420000),("Breakfast buffet","Breakfast",145000),("Espresso","Drinks",45000)]:
            RestaurantItem.objects.update_or_create(name=name,defaults={"category":category,"price":price})
        self.stdout.write(self.style.SUCCESS("Demo inventory ready."))
