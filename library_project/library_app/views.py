from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date, timedelta
from .models import Profile, Book, Issue
from django.contrib.auth import authenticate, login, logout


def book_list(request):
    books = Book.objects.all()
    return render(request, "library_app/book_list.html", {"books": books})

def add_member(request):
    if request.method == "POST":
        name = request.POST.get("full_name")
        if not name:
            messages.error(request, "Enter member name.")
            return redirect("add_member")
        Profile.objects.create(full_name=name)
        messages.success(request, "Member added successfully!")
        return redirect("members_list")
    return render(request, "library_app/add_member.html")

def members_list(request):
    members = Profile.objects.all().order_by("full_name")
    for m in members:
        m.active_count = Issue.objects.filter(profile=m, returned=False).count()
    return render(request, "library_app/members_list.html", {"members": members})

def issue_book(request, id):
    book = get_object_or_404(Book, id=id)
    if request.method == "POST":
        card_number = request.POST.get("card_number")
        profile = Profile.objects.filter(card_number=card_number).first()
        if not profile:
            messages.error(request, "Invalid card number!")
            return redirect(f"/issue/{id}/")
        Issue.objects.create(book=book, profile=profile)
        book.available -= 1
        book.save()
        messages.success(request, "Book issued successfully!")
        return redirect("book_list")
    return render(request, "library_app/issue.html", {"book": book})

def return_book(request, id):
    issue = get_object_or_404(Issue, id=id)
    today = date.today()
    if not issue.due_date:
        issue.due_date = issue.issue_date + timedelta(days=14)
        issue.save()
    due = issue.due_date
    fine = 0
    if today > due:
        fine = (today - due).days * 5
    if request.method == "POST":
        issue.returned = True
        issue.return_date = today
        issue.fine_amount = fine
        issue.save()
        issue.book.available += 1
        issue.book.save()
        messages.success(request, f"Book returned! Fine: ₹{fine}")
        return redirect("book_list")
    return render(request, "library_app/return.html", {
        "issue": issue,
        "fine": fine,
        "today": today,
        "due": due,
    })

def search_card(request):
    profile = None
    active_issues = []
    history = []
    total_outstanding = 0.0
    card = ""
    if "card" in request.GET:
        card = request.GET.get("card", "").strip()
    if request.method == "POST":
        card = request.POST.get("card_number", "").strip()
    if card:
        try:
            profile = Profile.objects.get(card_number=card)
        except Profile.DoesNotExist:
            messages.error(request, "Card number not found.")
            profile = None
        if profile:
            active_issues = Issue.objects.filter(profile=profile, returned=False).order_by('-issue_date')
            history = Issue.objects.filter(profile=profile, returned=True).order_by('-return_date')
            total_outstanding = sum(float(i.current_fine) for i in active_issues)
    return render(request, "library_app/search.html", {
        "profile": profile,
        "active_issues": active_issues,
        "history": history,
        "total_outstanding": total_outstanding,
    })
    
def add_member(request):
    if request.method == "POST":
        name = request.POST.get("full_name")
        if not name:
            messages.error(request, "Please enter the member's name.")
            return redirect("add_member")
        new_member = Profile.objects.create(full_name=name)
        messages.success(request, f"Member added successfully! Card Number: {new_member.card_number}")
        return redirect("members_list")
    return render(request, "library_app/add_member.html")

def add_book(request):
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        quantity = int(request.POST.get("quantity"))
        Book.objects.create(
            title=title,
            author=author,
            quantity=quantity,
            available=quantity
        )
        messages.success(request, "Book added successfully!")
        return redirect("book_list")
    return render(request, "library_app/add_book.html")

def edit_book(request, id):
    book = get_object_or_404(Book, id=id)
    if request.method == "POST":
        book.title = request.POST.get("title")
        book.author = request.POST.get("author")
        new_quantity = int(request.POST.get("quantity"))
        difference = new_quantity - book.quantity
        book.quantity = new_quantity
        book.available += difference
        if book.available < 0:
            book.available = 0 
        book.save()
        messages.success(request, "Book updated successfully!")
        return redirect("book_list")
    return render(request, "library_app/edit_book.html", {"book": book})

def delete_book(request, id):
    book = get_object_or_404(Book, id=id)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect("book_list")
    return render(request, "library_app/delete_book.html", {"book": book})

def add_book(request):
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        quantity = int(request.POST.get("quantity"))
        Book.objects.create(
            title=title,
            author=author,
            quantity=quantity,
            available=quantity
        )
        messages.success(request, "Book added successfully!")
        return redirect("book_list")
    return render(request, "library_app/add_book.html")

def admin_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("book_list")
        messages.error(request, "Invalid admin credentials")
        return redirect("admin_login")
    return render(request, "library_app/admin_login.html")

def member_login_view(request):
    if request.method == "POST":
        card = request.POST.get("card_number").strip()
        try:
            profile = Profile.objects.get(card_number=card)
            request.session["member_card"] = card  # store login session
            return redirect("member_dashboard")
        except Profile.DoesNotExist:
            messages.error(request, "Invalid card number")
            return redirect("member_login")

    return render(request, "library_app/member_login.html")
def member_dashboard(request):
    card = request.session.get("member_card")

    if not card:
        return redirect("member_login")
    profile = Profile.objects.get(card_number=card)
    active = Issue.objects.filter(profile=profile, returned=False)
    history = Issue.objects.filter(profile=profile, returned=True)
    total_fine = sum(float(i.current_fine) for i in active)
    return render(request, "library_app/member_dashboard.html", {
        "profile": profile,
        "active": active,
        "history": history,
        "total_fine": total_fine
    })

def admin_logout_view(request):
    logout(request)
    return redirect("home")

def member_logout_view(request):
    request.session.pop("member_card", None)
    return redirect("home")
    return redirect("member_login")
def home_page(request):
    return render(request, "library_app/home.html")




def add_stock(request, id):
    book = get_object_or_404(Book, id=id)

    if request.method == "POST":
        add_qty = int(request.POST.get("quantity", 0))

        if add_qty <= 0:
            messages.error(request, "Quantity must be greater than 0")
            return redirect("add_stock", id=id)

        book.quantity += add_qty
        book.available += add_qty
        book.save()

        messages.success(request, f"{add_qty} copies added successfully")
        return redirect("book_list")

    return render(request, "library_app/add_stock.html", {"book": book})




