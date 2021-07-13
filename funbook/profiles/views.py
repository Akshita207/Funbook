from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Relationship
from .forms import ProfileModelForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from py_avataaars import PyAvataaar
import py_avataaars as pa
# Create your views here.

@login_required
def my_avatar_view(request):
    a=''
    if request.method == 'POST':
        form = request.POST
        f = form.dict()
        option_style = f['style']
        option_skin_color = f['skin_color']
        option_top_type =f['top_type']
        option_hair_color =f['hair_color']
        option_hat_color =f['hat_color']
        option_facial_hair_type =f['facial_hair_type']
        option_facial_hair_color =f['facial_hair_color']
        option_mouth_type =f['mouth_type']
        option_eye_type =f['eye_type']
        option_eyebrow_type =f['eyebrow_type']
        option_accessories_type =f['accessories_type']
        option_clothe_type =f['clothe_type']
        option_clothe_color =f['clothe_color']
        option_clothe_graphic_type =f['clothe_graphic_type']

        profile = Profile.objects.get(user=request.user)
        avatar = pa.PyAvataaar(
        style=eval('pa.AvatarStyle.%s' % option_style),
        skin_color=eval('pa.SkinColor.%s' % option_skin_color),
        top_type=eval('pa.TopType.SHORT_HAIR_SHORT_FLAT.%s' % option_top_type),
        hair_color=eval('pa.HairColor.%s' % option_hair_color),
        hat_color=eval('pa.Color.%s' % option_hat_color),
        facial_hair_type=eval('pa.FacialHairType.%s' % option_facial_hair_type),
        facial_hair_color=eval('pa.HairColor.%s' % option_facial_hair_color),
        mouth_type=eval('pa.MouthType.%s' % option_mouth_type),
        eye_type=eval('pa.EyesType.%s' % option_eye_type),
        eyebrow_type=eval('pa.EyebrowType.%s' % option_eyebrow_type),
        nose_type=pa.NoseType.DEFAULT,
        accessories_type=eval('pa.AccessoriesType.%s' % option_accessories_type),
        clothe_type=eval('pa.ClotheType.%s' % option_clothe_type),
        clothe_color=eval('pa.Color.%s' % option_clothe_color),
        clothe_graphic_type=eval('pa.ClotheGraphicType.%s' %option_clothe_graphic_type)
    )
        a=str(profile.slug)
        a+='.png'
        avatar.render_png_file(a)

        profile.avatar = a
        profile.save()

    return render(request, 'profiles/myprofileavatar.html', {'a':a})


@login_required
def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileModelForm(request.POST or None, request.FILES or None, instance=profile)
    confirm = False

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            confirm = True

    context = {
        'profile': profile,
        'form': form,
        'confirm': confirm,
    }

    return render(request, 'profiles/myprofile.html', context)

@login_required
def invites_received_view(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invatations_received(profile)
    results = list(map(lambda x: x.sender, qs))
    is_empty = False
    if len(results) == 0:
        is_empty = True

    context = {
        'qs': results,
        'is_empty': is_empty,
    }

    return render(request, 'profiles/my_invites.html', context)

@login_required
def accept_invatation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()
    return redirect('profiles:my-invites-view')

@login_required
def reject_invatation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        receiver = Profile.objects.get(user=request.user)
        sender = Profile.objects.get(pk=pk)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('profiles:my-invites-view')

@login_required
def profiles_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles(user)

    context = {'qs': qs}

    return render(request, 'profiles/profile_list.html', context)

@login_required
def search_profiles_list_view(request):
    if request.method == 'GET':
        search_query = request.GET.get('search_box', None)
        search_query = search_query.lower()
        user = request.user
        qs = Profile.objects.all()
        print(qs)
        profile = Profile.objects.get(user=request.user)
        nqs = Relationship.objects.invatations_received(profile)
        mqs = Relationship.objects.invatations_sent(profile)
        print(nqs)
        results = list(map(lambda x: x.sender, nqs))
        result = list(map(lambda x: x.receiver, mqs))
        print("yo")
        print(results)
        print(result)
        is_empty = False
        if len(results) == 0:
            is_empty = True
        fqs=[]
        for i in qs:
            print(i.first_name)
            if str(i.first_name).lower() == search_query or str(i.last_name).lower() == search_query or str(i.user).lower() == search_query:
                fqs.append(i)
                if i.user in nqs:
                    print(yo)

        context = {
                    'fqs': fqs,
                    'nqs': results,
                    'mqs': result,
                  }
        context['is_empty'] = False
        if len(fqs) == 0:
            context['is_empty'] = True
    return render(request, 'profiles/search_profile.html', context)



class InviteProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/to_invite_list.html'

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)
        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True

        return context

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)
        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['posts'] = self.get_object().get_all_authors_posts()
        context['len_posts'] = True if len(self.get_object().get_all_authors_posts()) > 0 else False
        return context

class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)
        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True

        return context

@login_required
def send_invatation(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')

@login_required
def remove_from_friends(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender))
        )
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')
