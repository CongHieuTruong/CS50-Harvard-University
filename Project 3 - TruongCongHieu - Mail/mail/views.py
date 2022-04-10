from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User, Email


def index(req):

    if req.method != 'POST' and req.user.is_authenticated:
        return render(req, "mail/inboxViewPage.html")

    else:
        return HttpResponseRedirect(reverse("account/login"))


@csrf_exempt
@login_required
def getMailData(req, typeMail):

    if typeMail == "inbox":
        emails = Email.objects.filter(
            user=req.user, recipients=req.user, archived=False
        )
    elif typeMail == "sent":
        emails = Email.objects.filter(
            user=req.user, sender=req.user
        )
    elif typeMail == "archive":
        emails = Email.objects.filter(
            user=req.user, recipients=req.user, archived=True
        )
    else:
        return JsonResponse({"error": "Invalid data."}, status=400)

    emails = emails.order_by("-timestamp").all()
    return JsonResponse([email.serializerData() for email in emails], safe=False)


@csrf_exempt
@login_required
def sendEmailForUser(req):
    userRequest = req.user
    if req.method != "POST":
        return JsonResponse({"error": "Server require POST method"}, status=400)

    bodyJsonObjectData = json.loads(req.body)
    arrayEmail = [email.strip()
                  for email in bodyJsonObjectData.get("recipients").split(",")]
    if arrayEmail == [""]:
        return JsonResponse({
            "error": "Recipient is required."
        }, status=400)

    arrayRecipient = []
    for email in arrayEmail:
        try:
            user = User.objects.get(email=email)
            arrayRecipient.append(user)
        except User.DoesNotExist:
            return JsonResponse({
                "error": "User does not exist."
            }, status=400)

    mailSubject = bodyJsonObjectData.get("subject", "")
    mailBodyContent = bodyJsonObjectData.get("body", "")

    setUsers = set()
    setUsers.add(userRequest)
    setUsers.update(arrayRecipient)
    for userEmailData in setUsers:
        email = Email(
            user=userEmailData,
            sender=userRequest,
            subject=mailSubject,
            body=mailBodyContent,
            read=False
        )
        email.save()
        for recipient in arrayRecipient:
            email.recipients.add(recipient)
        email.save()
        data = email.serializerData()
    return JsonResponse(data, status=200, safe=False)


def userLoginHandleLogic(req):
    if req.method == "POST":

        emailInput = req.POST["email"]
        passwordInput = req.POST["password"]
        authenticateForUser = authenticate(
            req, username=emailInput, password=passwordInput)

        if authenticateForUser is not None:
            login(req, authenticateForUser)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(req, "mail/loginViewPage.html", {
                "message": "Invalid input email and/or password. Please try again"
            })
    else:
        return render(req, "mail/loginViewPage.html")


@csrf_exempt
@login_required
def getEmailContentData(req, id):
    def validMethod(req):
        return req.method == "GET" or req.method == 'PUT'

    if not validMethod(req):
        return JsonResponse({
            "error": "Server require GET or PUT method"
        }, status=400)

    content = tryGetEmailObject(req, id)

    if content == 'email not found':
        return JsonResponse({"error": "Email not found."}, status=404)

    if req.method == "GET":
        return JsonResponse(content.serializerData(), status=200)

    if req.method == "PUT":
        jsonBodyData = json.loads(req.body)
        if jsonBodyData.get("read") is not None:
            content.read = jsonBodyData["read"]
        if jsonBodyData.get("archived") is not None:
            content.archived = jsonBodyData["archived"]
        content.save()
        return JsonResponse(content.serializerData(), status=200)


def tryGetEmailObject(req, id):
    try:
        email = Email.objects.get(user=req.user, pk=id)
    except Email.DoesNotExist:
        return 'email not found'
    return email


def userRegisterHandleLogic(req):
    if req.method == "POST":
        emailInput = req.POST["email"]

        passwordInput = req.POST["password"]
        confirmationInput = req.POST["confirmation"]
        if passwordInput != confirmationInput:
            return render(req, "mail/registerViewPage.html", {
                "message": "Passwords must match."
            })

        user = registerUser(emailInput, passwordInput)
        if user == 'already taken':
            return render(req, "mail/registerViewPage.html", {
                "message": "This email have already taken. Please try another one"
            })
        login(req, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(req, "mail/registerViewPage.html")


def userLogoutHandleLogic(req):
    logout(req)
    return HttpResponseRedirect(reverse("index"))


def registerUser(emailInput, passwordInput):
    try:
        user = User.objects.create_user(emailInput, emailInput, passwordInput)
        user.save()
    except IntegrityError as error:
        print(error)
        return 'already taken'
    return user
