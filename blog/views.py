from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Post


def home_test(request):
    return HttpResponse("Hello World")


def post_list(request):
    posts = Post.objects.order_by("-created_at")
    return render(request, "blog/index.html", {"posts": posts})


def post_detail(request, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, "blog/index2.html", {"post": post})


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            return redirect("post_detail", post_id=post.id)
    else:
        form = PostForm()
    return render(request, "blog/edit.html", {"form": form, "is_edit": False})


def post_edit(request, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post_detail", post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(
        request,
        "blog/edit.html",
        {"form": form, "post": post, "is_edit": True},
    )


def post_delete(request, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        post.delete()
        return redirect("post_list")
    return render(request, "blog/delete.html", {"post": post})


# ----- Koszyk (session-based) -----

def cart_add(request, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    cart = request.session.get("cart", {})
    key = str(post_id)
    if post.stock > 0:
        cart[key] = cart.get(key, 0) + 1
        request.session["cart"] = cart
    return redirect(request.META.get("HTTP_REFERER", "post_list"))


def cart_remove(request, post_id: int):
    cart = request.session.get("cart", {})
    key = str(post_id)
    if key in cart:
        del cart[key]
        request.session["cart"] = cart
    return redirect("cart_view")


def cart_view(request):
    cart = request.session.get("cart", {})
    items = []
    total = 0
    for post_id, quantity in cart.items():
        post = get_object_or_404(Post, pk=int(post_id))
        subtotal = post.price * quantity
        total += subtotal
        items.append({"post": post, "quantity": quantity, "subtotal": subtotal})
    return render(request, "blog/cart.html", {"items": items, "total": total})
