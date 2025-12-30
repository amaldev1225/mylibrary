from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [

    path("", views.home_page, name="home"),
    path("admin-login/", views.admin_login_view, name="admin_login"),
    path("member-login/", views.member_login_view, name="member_login"),
    path("member-dashboard/", views.member_dashboard, name="member_dashboard"),
    path("books/", views.book_list, name="book_list"),
    path("books/add/", views.add_book, name="add_book"),
    path("books/edit/<int:id>/", views.edit_book, name="edit_book"),
    path("books/delete/<int:id>/", views.delete_book, name="delete_book"),
    path("issue/<int:id>/", views.issue_book, name="issue_book"),
    path("return/<int:id>/", views.return_book, name="return_book"),
    path("add-member/", views.add_member, name="add_member"),
    path("members/", views.members_list, name="members_list"),
    path("search/", views.search_card, name="search_card"),
    path("admin-logout/", views.admin_logout_view, name="admin_logout"),
    path("member-logout/", views.member_logout_view, name="member_logout"),
    path("books/stock/<int:id>/", views.add_stock, name="add_stock"),

]

