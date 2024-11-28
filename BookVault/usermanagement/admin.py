from django.contrib import admin

from .models import User,Address,LibrarianProfile,MemberProfile,AdminProfile,Subscription,MemberSubscriptionLog

# Register your models here.
admin.site.register(Address)
admin.site.register(User)
admin.site.register(LibrarianProfile)
admin.site.register(MemberProfile)
admin.site.register(AdminProfile)
admin.site.register(Subscription)

admin.site.register(MemberSubscriptionLog)


