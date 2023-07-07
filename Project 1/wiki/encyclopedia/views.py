from django.shortcuts import render
from django.shortcuts import redirect
from django import forms
from . import util
import markdown


class SearchForm(forms.Form):
    q = forms.CharField(label='')


class NewPageForm(forms.Form):
    title = forms.CharField(label='')
    markdown_text = forms.CharField(label='')


class EditPageForm(forms.Form):
    markdown_text = forms.CharField(label='')


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    """
    Creates a page with the content of the title if it exists. If it doesn't exist,
    an error page is rendered.
    """
    entry_content = util.get_entry(title)
    if entry_content:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "markdown":  markdown.markdown(entry_content)
        })
    else:
        return render(request, "encyclopedia/404.html", {
            "error": "Entry does not exist!"
        })


def search(request):
    """
    Retrieves the search query given by the user. If the title exists, the entry page is shown. If the entry page does
    not exist, a list of links with entries that contain the search query in its title.
    """
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            q = form.cleaned_data["q"]
            title = util.get_file(q)
            if title is not None:
                return redirect("entry", title=title)
            else:
                return render(request, "encyclopedia/search_results.html", {
                    "entries": util.get_files(q)
                })


def new_page(request):
    """
    Page for creating a new entry. If the entry exists, an error page is shown. Otherwise, the entry is saved to disk
    and the user is redirected to the new entry page.
    """
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            if title == "":
                return render(request, "encyclopedia/404.html", {
                    "error": "Entry title is not valid!"
                })
            elif title in util.list_entries():
                return render(request, "encyclopedia/404.html", {
                    "error": "Entry already exists!"
                })
            markdown_text = form.cleaned_data["markdown_text"]
            util.save_entry(title, markdown_text)
            return redirect("entry", title=title)
    else:
        return render(request, "encyclopedia/new_page.html")


def edit(request, title):
    """
    Displays a page with current entry information. If the user saves the edit, the entry is updated.
    """
    if request.method == "GET":
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "markdown": util.get_entry(title)
        })
    else:
        form = EditPageForm(request.POST)
        if form.is_valid():
            markdown_text = form.cleaned_data["markdown_text"]
            util.save_entry(title, markdown_text)
            return redirect("entry", title=title)


def random_page(request):
    """
    Redirects to a random entry page.
    """
    title = util.get_random()
    return redirect("entry", title=title)

