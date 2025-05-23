from .models import Profile

def user_data(request):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = None

        return {
            'user_data': {
                'username': request.user.username,
                'email': request.user.email,
                'name': profile.name if profile else None,
                'mobile_number': profile.mobile_number if profile else None,
                'profile_image': profile.profile_image.url if profile else None,
                'address': profile.address if profile else None,
            }
        }
    return {'user_data': None}  # If no user is logged in
