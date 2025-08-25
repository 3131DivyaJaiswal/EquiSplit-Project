from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, GroupForm, ExpenseForm, UserProfileForm
from .models import Group, Expense
from django.contrib import messages
from django.contrib.auth.models import User 
from django.core.mail import send_mail
from .forms import GroupForm

def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'register.html', {'form': form})

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    print(form)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    groups = request.user.custom_groups.all()
    return render(request, 'dashboard.html', {'groups': groups})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    expenses = group.expenses.all()
    members = group.members.all()
    
    balances = {member: 0 for member in members}


    for exp in expenses:
        exp_participants = exp.participants.all()
        split_amt = exp.amount / exp_participants.count()
        for member in exp_participants:
            balances[member] -= split_amt
        balances[exp.paid_by] += exp.amount

    settlements = calculate_debts(balances)
    return render(request, 'group_detail.html', {
        'group': group,
        'expenses': expenses,
        'balances': balances,
        'settlements': settlements,
    })


@login_required
def create_group(request):
    form = GroupForm(request.POST or None,request.FILES )
    form.fields['members'].queryset = form.fields['members'].queryset.exclude(id=request.user.id) | User.objects.filter(id=request.user.id)
    if form.is_valid():
        group = form.save()
        group.members.add(request.user)
        return redirect('dashboard')
    return render(request, 'create_group.html', {'form': form})


@login_required
def add_expense(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    form = ExpenseForm(request.POST or None)
    # only show current group members for participants selection:
    form.fields['participants'].queryset = group.members.all()

    if form.is_valid():
        expense = form.save(commit=False)
        expense.group = group
        expense.save()
        form.save_m2m()
        return redirect('group_detail', group_id=group.id)
    return render(request, 'add_expense.html', {'form': form, 'group': group})

@login_required
def group_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user not in group.members.all():
        messages.error(request, "You are not authorized to delete this group.")
        return redirect('dashboard')

    if request.method == 'POST':   
        group.delete()
        messages.success(request, "Group deleted successfully!")
        return redirect('dashboard')

    return render(request, 'group_confirm_delete.html', {'group': group})


@login_required
def profile_update(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_update')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'profile_update.html', {'form': form, 'profile': profile})




@login_required
def send_reminder_email(request, group_id, user_id):
    debtor = get_object_or_404(User, id=user_id)
    group = get_object_or_404(Group, id=group_id)
    full_settlements = []
    expenses = group.expenses.all()
    members = group.members.all()
    
    balances = {member: 0 for member in members}


    for exp in expenses:
        exp_participants = exp.participants.all()
        split_amt = exp.amount / exp_participants.count()
        for member in exp_participants:
            balances[member] -= split_amt
        balances[exp.paid_by] += exp.amount

    # Only keep settlements where this user owes in this group
    for s in calculate_debts(balances):
            if s[0] == debtor and s[2] > 0:
                full_settlements.append({
                    'creditor': s[1],      # User object
                    'amount': s[2],
                    'creditor_upi': s[3], # UPI ID
                    'group': group.name,
                })

    if full_settlements:
        subject = "Payment Reminder from Splitwise"
        body = f"Hi {debtor.username},\n\nYou currently owe:\n"
        for s in full_settlements:
            body += (
                f"- ₹{s['amount']:.2f} to {s['creditor'].username} "
                f"in group \"{s['group']}\""
            )
            if s['creditor_upi']:
                body += f" (Creditor UPI: {s['creditor_upi']})"
            body += "\n"
        body += "\nPlease pay soon to keep your groups happy!"
        send_mail(
            subject,
            body,
            None,  
            [debtor.email],
            fail_silently=False,
        )
        messages.success(request, f"Reminder email sent to {debtor.username}.")
    else:
        subject = "Splitwise: No dues"
        body = f"Hi {debtor.username}, you are all settled up!"
        send_mail(subject, body, None, [debtor.email], fail_silently=False)
        messages.success(request, f"{debtor.username} is already settled up.")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
def calculate_debts(balances):
    settlement = []
    creditts = []
    debitt = []
    for user, amount in balances.items():
        if amount > 0:
            creditts.append([user, round(amount, 2)])
        elif amount < 0:
            debitt.append([user, round(-amount, 2)])  

    creditts.sort(key=lambda x: -x[1])
    debitt.sort(key=lambda x: -x[1])

    i, j = 0, 0
    while i < len(debitt) and j < len(creditts):
        debtor, debt_amt = debitt[i]
        creditt, cred_amt = creditts[j]
        paid = min(debt_amt, cred_amt)
        settlement.append((debtor, creditt, paid, getattr(debtor.profile, 'upi_id', ''),
        getattr(creditt.profile, 'upi_id', '')))
        debitt[i][1] -= paid
        creditts[j][1] -= paid
        if debitt[i][1] == 0:
            i += 1
        if creditts[j][1] == 0:
            j += 1
    return settlement