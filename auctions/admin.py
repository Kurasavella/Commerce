from django.contrib import admin

from . models import Auction, User, Comment, Rate

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("auctions", )

admin.site.register(Auction)
admin.site.register(User, UserAdmin)
admin.site.register(Comment)
admin.site.register(Rate)