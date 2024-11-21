from django.contrib import admin

from .models import User,Address,LibrarianProfile,MemberProfile

# Register your models here.
admin.site.register(Address)
admin.site.register(User)

admin.site.register(LibrarianProfile)
admin.site.register(MemberProfile)