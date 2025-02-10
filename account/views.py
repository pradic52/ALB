from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import LoginForm

from django.core.cache import cache
from django.utils.timezone import now
from datetime import timedelta


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        ip_address = request.META.get('REMOTE_ADDR', '')
        failed_attempts_key = f'failed_login_{ip_address}'
        failed_attempts = cache.get(failed_attempts_key, 0)

        # Check rate limiting
        if failed_attempts >= 5:
            form.add_error(None, 'Trop de tentatives échouées. Réessayez un peu plus tard.')
        else:
            # Validate form input
            if form.is_valid():

                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    cache.delete(failed_attempts_key)  # Reset failed attempts on successful login
                    return redirect('home')
                else:
                    # Increment failed login counter
                    cache.set(failed_attempts_key, failed_attempts + 1, timeout=int(timedelta(minutes=15).total_seconds()))
                    form.add_error(None, 'Le nom d\'utilisateur ou le mot de passe est incorrect.')
    else:
        form = LoginForm()

    return render(request, 'account/login.html', {'form': form})


def logout_view(request):
    try:
        logout(request)
        messages.success(request, f"Vous êtes bien déconnecté à {now().strftime('%Y-%m-%d %H:%M:%S')}...")
    except Exception as e:
        messages.error(request, 'Une erreur est survenue lors de la déconnexion. Veuillez réessayer.')
        # Optional: log the exception 'e' for debugging purposes.
        return redirect('error_page')  # Redirect to an error page if available.
    # Log the logout event (if logging is set up in your project)
    return redirect('home')
    