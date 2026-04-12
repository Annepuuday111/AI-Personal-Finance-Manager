from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from .models import (
    UserProfile, BankAccount, Transaction, Category, 
    Budget, FinancialGoal
)

# ==================== SIGNUP FORM ====================
class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'form-input'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'form-input'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number (Optional)',
            'class': 'form-input'
        })
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and UserProfile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        
        # Update user profile with phone number
        if self.cleaned_data.get('phone_number'):
            user.profile.phone_number = self.cleaned_data['phone_number']
            user.profile.save()
        
        return user


# ==================== USER FORMS ====================
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'phone_number', 'address', 'date_of_birth', 'profile_picture', 
            'bio', 'currency', 'monthly_budget', 'savings_goal',
            'email_notifications', 'budget_alerts', 'ai_insights'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'monthly_budget': forms.NumberInput(attrs={'class': 'form-input'}),
            'savings_goal': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }


# ==================== BANK ACCOUNT FORM ====================
class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['name', 'account_type', 'account_number', 'balance', 'currency']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Account Name'}),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
            'account_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Account Number'}),
            'balance': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
        }


# ==================== TRANSACTION FORM ====================
class TransactionForm(forms.ModelForm):
    RECURRING_CHOICES = [
        ('', 'Select frequency'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]
    
    recurring_frequency = forms.ChoiceField(
        choices=RECURRING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Transaction
        fields = [
            'account', 'category', 'transaction_type', 'amount', 
            'description', 'notes', 'date', 'is_recurring', 
            'recurring_frequency', 'tags', 'receipt'
        ]
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Transaction Description'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tags (comma separated)'}),
            'receipt': forms.FileInput(attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['account'].queryset = BankAccount.objects.filter(user=user)
            self.fields['category'].queryset = Category.objects.filter(user=user)


# ==================== CATEGORY FORM ====================
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'icon', 'color', 'budget_limit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'category_type': forms.Select(attrs={'class': 'form-select'}),
            'icon': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '💰'}),
            'color': forms.TextInput(attrs={'class': 'form-input', 'type': 'color'}),
            'budget_limit': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }


# ==================== BUDGET FORM ====================
class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'period', 'start_date', 'end_date', 'alert_threshold']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'alert_threshold': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'max': '100'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(BudgetForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user, category_type='EXPENSE')


# ==================== FINANCIAL GOAL FORM ====================
class FinancialGoalForm(forms.ModelForm):
    class Meta:
        model = FinancialGoal
        fields = ['name', 'description', 'target_amount', 'current_amount', 'deadline', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Goal Name'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'current_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'deadline': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'icon': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '🎯'}),
        }