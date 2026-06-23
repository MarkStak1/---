from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Count
from .models import Category, Event, Registration
from .forms import SignUpForm, LoginForm, PaymentForm


def event_list(request, category_slug=None):
    categories = (
        Category.objects
        .annotate(event_count=Count('events'))
        .order_by('name')
    )
    events = Event.objects.select_related('category').order_by('date')
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        events = events.filter(category=active_category)
    return render(request, 'event/list.html', {
        'events': events,
        'categories': categories,
        'active_category': active_category,
        'events_count': Event.objects.count(),
        'categories_count': categories.count(),
    })


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = Registration.objects.filter(
            user=request.user, event=event
        ).exists()
    return render(request, 'event/detail.html', {
        'event': event,
        'is_registered': is_registered,
    })


@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if Registration.objects.filter(user=request.user, event=event).exists():
        messages.info(request, 'Вы уже записаны на это событие')
        return redirect('event_detail', pk=event.id)
    if event.price > 0:
        return redirect('event_payment', event_id=event.id)
    Registration.objects.create(user=request.user, event=event, amount_paid=0)
    messages.success(request, f'Вы записаны на «{event.title}»')
    return redirect('event_detail', pk=event.id)


@login_required
def event_payment(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if event.price <= 0:
        return redirect('register_event', event_id=event.id)
    if Registration.objects.filter(user=request.user, event=event).exists():
        messages.info(request, 'Вы уже записаны на это событие')
        return redirect('event_detail', pk=event.id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            Registration.objects.create(
                user=request.user,
                event=event,
                amount_paid=event.price,
            )
            messages.success(
                request,
                f'Оплата {event.price} ₽ прошла успешно. Вы записаны на «{event.title}»',
            )
            return redirect('event_detail', pk=event.id)
    else:
        form = PaymentForm()
    return render(request, 'event/payment.html', {
        'form': form,
        'event': event,
    })


def signup(request):
    if request.user.is_authenticated:
        return redirect('event_list')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно. Добро пожаловать!')
            return redirect('event_list')
    else:
        form = SignUpForm()
    return render(request, 'event/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('event_list')
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f'Добро пожаловать, {form.get_user().username}!')
            redirect_to = request.POST.get('next') or reverse('event_list')
            if not url_has_allowed_host_and_scheme(
                redirect_to, allowed_hosts={request.get_host()}
            ):
                redirect_to = reverse('event_list')
            return redirect(redirect_to)
    else:
        form = LoginForm()
    return render(request, 'event/login.html', {'form': form, 'next': next_url})


@login_required
def profile(request):
    registrations = (
        Registration.objects
        .filter(user=request.user)
        .select_related('event', 'event__category')
        .order_by('event__date')
    )
    return render(request, 'event/profile.html', {
        'registrations': registrations,
    })


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта')
    return redirect('event_list')
