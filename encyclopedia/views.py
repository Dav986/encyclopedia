from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from . import util
from django import forms
from random import randint
import re
from django.contrib import messages
from markdown2 import Markdown


class NewEntryForm(forms.Form):
    title = forms.CharField(
        required=True,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Title", "class": "mb-4"}
        ),
    )
    content = forms.CharField(
        required=True,
        label="",
        widget= forms.Textarea(
            attrs={
                "class": "form-control mb-4",
                "placeholder": "Content (markdown)",
                "id": "new_content",
            }
        ),
    )

def index(request):
    return render(
        request, "encyclopedia/index.html", {"entries": util.list_entries()}
    )

def wiki(request, entry):
    if entry not in util.list_entries():
        raise Http404
    content = util.get_entry(entry)
    return render(
        request,
        "encyclopedia/wiki.html",
        {"title": entry, "content": Markdown().convert(content)},
    )

def search(request):
    entries = util.list_entries()
    query = request.session['query']
    find_entries = list()

    search_box = request.POST.get("q", "").capitalize()

    if search_box in entries:
        return HttpResponseRedirect(f"wiki/{search_box}")

    for entry in entries:
        if re.search(query, entry):
            find_entries.append(entry)

    if find_entries:
        return render(request, "encyclopedia/search.html", {
            "search_result": find_entries,
            "search": search_box
        })

def new(request):
    if request.method == "GET":
        return render(
            request, "encyclopedia/new.html", {"form": NewEntryForm()}
        )

    form = NewEntryForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data.get("title")
        content = form.cleaned_data.get("content")

        if title.lower() in [entry.lower() for entry in util.list_entries()]:
            messages.add_message(
                request,
                messages.WARNING,
                message=f'Entry "{title}" already exists',
            )
        else:
            with open(f"entries/{title}.md", "w") as file:
                file.write(content)
            return redirect("encyclodepia:wiki", title)

    else:
        messages.add_message(
            request, messages.WARNING, message="Invalid request form"
        )

    return render(
        request,
        "encyclopedia/new.html",
        {"form": form},
    )

def random_entry(request):
    entries = util.list_entries()
    entry = entries[randint(0, len(entries) - 1)]
    return redirect("encyclopedia:wiki", entry)

def edit(request, entry):
    if request.method == "GET":
        title = entry
        content = util.get_entry(title)
        form = NewEntryForm({"title": title, "content": content})
        return render(
            request,
            "encyclopedia/edit.html",
            {"form": form, "title": title},
        )

    form = NewEntryForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data.get("title")
        content = form.cleaned_data.get("content")

        util.save_entry(title=title, content=content)
        return redirect("encyclopedia:wiki", title)