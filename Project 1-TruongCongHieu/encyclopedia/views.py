import random
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from markdown2 import Markdown
from . import utils
from .forms import FormData, Search
from .models import FormModel


def index(req):
    allFormData = FormModel.objects.all()
    listTitle = []
    for item in allFormData:
      listTitle.append(item.title)
    return render(req, "encyclopedia/indexPage.html", {
        "entries": listTitle,
        "search_form": Search(),
    })

def entry(req, title):
    data = FormModel.objects.all()
    for item in data:
      if title == item.title:
        entry_converted = Markdown().convert(item.text)
        context = {
          "title": title,
          "entry": entry_converted,
          "search_form": Search(),
          "data": item
        } 
        return render(req, "encyclopedia/entryEdit.html", context)

    return render(req, "encyclopedia/errorPageMessage.html", {
      "title": title,
      "search_form": Search(),
      })

def search(req):
    if req.method == "POST":
        formData = Search(req.POST)
        if formData.is_valid():
            title = formData.cleaned_data["title"]
            data =  FormModel.objects.all()
            listTitle = []
            for item in data:
              if title == item.title:
                return redirect(reverse('entry', args=[title]))
              elif title.lower() in item.title.lower():
                listTitle.append(item.title)

            return render(req, "encyclopedia/searchPage.html", {
            "title": title,
            "find_entry_by_titles": listTitle,
            "search_form": Search()
            })

    return redirect(reverse('index'))

def create(req):
    if req.method == "GET":
        return render(req, "encyclopedia/createForm.html", {
          "create_form": FormData(),
          "search_form": Search()
        })

    elif req.method == "POST":
        form = FormData(req.POST,req.FILES)

        if form.is_valid():
          title = form.cleaned_data['title']
          text = form.cleaned_data['text']
        obj = FormModel.objects.all()
        for item in obj:
          if title == item.title:
            messages.error(req, 'Page title already exist! Please go to that title page and edit it')
            return render(req, "encyclopedia/createForm.html", {
              "create_form": form,
              "search_form": Search()
            })
        utils.save_req_entry(None, title, text)
        form.save()
        messages.success(req, f'New page "{title}" created successfully!')
        return redirect(reverse('entry', args=[title]))

def edit(req, title):
    data = FormModel.objects.get(title = title)
    if req.method == "GET":
        text = data.text
        image = data.image
        if text == None:
            messages.error(req, f'"{title}"" page doesn\'t exist & can\'t be edited, create the new page')

        return render(req, "encyclopedia/editForm.html", {
          "title": title,
          "edit_form": FormData(initial={'text':text, 'title': title, 'image':image}),
          "search_form": Search()
        })

    elif req.method == "POST":
        formData = FormData(req.POST, req.FILES)

        if formData.is_valid():
          text = formData.cleaned_data['text']
          titleSubmit = formData.cleaned_data['title']
          data.text = text
          data.title = titleSubmit
          if req.POST.get('image-clear', False) == 'on':
            data.image = None
          if formData.cleaned_data['image']:
            data.image = formData.cleaned_data['image']
          utils.save_req_entry(title, titleSubmit, text)
          data.save()
          messages.success(req, f'Page "{titleSubmit}" updated successfully')
          return redirect(reverse('entry', args=[titleSubmit]))

        else:
          messages.error(req, f'Form is invalid, try again later')
          return render(req, "encyclopedia/editForm.html", {
            "title": title,
            "edit_form": formData,
            "search_form": Search()
          })

def random_title(req):
    titles = FormModel.objects.all()
    title = random.choice(titles)
    return redirect(reverse('entry', args=[title]))



