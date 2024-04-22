import binascii
from datetime import datetime, timedelta

from django.db import OperationalError, IntegrityError, DataError
from django.http import response, HttpRequest, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.core import exceptions
from django.contrib.auth import hashers

import ourJWT.OUR_exception

from . import crypto
from login.models import User
import base64
import os

import json

import pyotp

duration = int(os.getenv("AUTH_LIFETIME", "10"))


def return_auth_cookie(user: User, full_response: response.HttpResponse):
    user_dict = model_to_dict(user)
    expdate = datetime.now() + timedelta(minutes=duration)
    user_dict["exp"] = expdate
    payload = crypto.encoder.encode(user_dict, "auth")
    full_response.set_cookie(key="auth_token",
                             value=payload,
                             httponly=True,
                             samesite="Strict")
    return full_response


def return_refresh_token(user: User):
    full_response = response.HttpResponse()
    full_response.set_cookie(key='refresh_token',
                             value=user.generate_refresh_token(),
                             httponly=True,
                             samesite="Strict"
                             )
    return return_auth_cookie(user, full_response)


# Create your views here.

#TODO: ne pas envoyer le refresh token en body, mais en cookie http only : https://dev.to/bcerati/les-cookies-httponly-une-securite-pour-vos-tokens-2p8n
#TODO: get info in Authorization request header https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization
@csrf_exempt  # TODO: DO NOT USE IN PRODUCTION
@require_GET
def login_endpoint(request: HttpRequest):
    auth: str = request.headers.get("Authorization", None)
    if auth is None:
        return response.HttpResponseBadRequest(reason="No Authorization header found in request")
    auth_type: str = auth.split(" ", 1)[0]
    if auth_type != "Basic":
        return response.HttpResponseBadRequest(reason="invalid Authorization type")
    auth_data_encoded: str = auth.split(" ")[1]
    try:
        auth_data = base64.b64decode(auth_data_encoded).decode()
    except binascii.Error:
        return response.HttpResponseBadRequest(reason="invalid encoding")
    login = auth_data.split(":")[0]
    try:
        password = auth_data.split(":", 1)[1]
    except IndexError:
        return response.HttpResponse(status=401, reason='Invalid credential')
    try:
        user: User = User.objects.get(login=login)
    except exceptions.ObjectDoesNotExist:
        return response.HttpResponse(status=401, reason='Invalid credential')

    if request.body:
            # User has sent an otp code and the password has been checked.
        user_code = json.loads(request.body).get("otp_code")
        if (user_code is not None) & (user.login_attempt is not None):
            if (user.login_attempt + timedelta(minutes=1)) < datetime.now():
                if user.totp_item.verify(user_code):
                    user.login_attempt = None
                    return return_refresh_token(user=user)
                return response.HttpResponseBadRequest(reason="BAD OTP")
            return response.HttpResponseForbidden(reason="OTP validation timed out")

    if hashers.check_password(password, user.password):
        if user.totp_enabled:
            user.login_attempt = datetime.now()
            return response.HttpResponse(status=202, reason="Expecting OTP")
        return return_refresh_token(user=user)
    else:
        return response.HttpResponse(status=401, reason='Invalid credential')


@csrf_exempt  # TODO: DO NOT USE IN PRODUCTION
@require_POST
def register_endpoint(request: HttpRequest):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return response.HttpResponseBadRequest(reason="JSON Decode Error")

    expected_keys = {"login", "password", "display_name"}
    if set(data.keys()) != expected_keys:
        return response.HttpResponseBadRequest(reason="Bad Keys")

    login = data["login"]
    display_name = data["display_name"]
    password = data["password"]

    if password.__len__() < 5:
        return response.HttpResponseBadRequest(reason="Invalid credential")

    if User.objects.filter(login=login).exists():
        return response.HttpResponse(status=401, reason="User with this login already exists")

    try:
        new_user = User(login=login, password=password, displayName=display_name)
        new_user.clean_fields()
        new_user.save()
    except (IntegrityError, OperationalError) as e:
        print(f"DATABASE FAILURE {e}")
        return response.HttpResponse(status=500, reason="Database Failure")
    except (exceptions.ValidationError, DataError) as e:
        print(e)
        return response.HttpResponseBadRequest(reason="Invalid credential")
    new_user.password = hashers.make_password(password)
    new_user.save()
    return return_refresh_token(new_user)


#Can't use the decorator as the auth token may be expired
@csrf_exempt  # TODO: DO NOT USE IN PRODUCTION
@require_GET
def refresh_auth_token(request: HttpRequest, *args):
    try:
        request.COOKIES["auth_token"]
    except KeyError:
        return response.HttpResponseBadRequest(reason="no auth token")
    try:
        auth = ourJWT.Decoder.decode(request.COOKIES.get("auth_token"), check_date=False)
    except (ourJWT.ExpiredToken, ourJWT.BadSubject, ourJWT.RefusedToken):
        return response.HttpResponseBadRequest(reason='bad auth token')
    auth_login = auth.get("login")

    try:
        request.COOKIES["refresh_token"]
    except:
        return response.HttpResponseBadRequest(reason="no refresh token")
    try:
        refresh = ourJWT.Decoder.decode(request.COOKIES.get("refresh_token"))
    except:
        return response.HttpResponseBadRequest("decode error")

    refresh_pk = refresh.get("pk")
    try:
        user = get_object_or_404(User, pk=refresh_pk)
    except Http404:
        return response.Http404()
    if user.login != auth_login:
        return response.HttpResponseForbidden("token error")

    jwt_id = refresh["jti"]
    if jwt_id != user.jwt_emitted:
        return response.HttpResponseBadRequest(reason="token error")

    return return_auth_cookie(user, response.HttpResponse(status=200))


@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods("PATCH")
def set_totp(request: HttpRequest, **kwargs):
    auth = kwargs["token"]
    key = auth["id"]
    try:
        user = get_object_or_404(User, pk=key)
    except Http404:
        return response.Http404()
    if user.totp_enabled is True:
        return response.HttpResponseForbidden(reason="2FA already enabled for the account")

    if request.body:
        # the request has also sent in an otp code, user already have the otp key saved somewhere
        user_code = json.loads(request.body).get("otp_code")
        if user_code is not None:
            if user.totp_item.verify(user_code):
                user.totp_enabled = True
                return response.HttpResponse(status=200)
            else:
                return response.HttpResponseBadRequest("BAD OTP")

    user.totp_key = pyotp.random_base32()
    user.totp_item = pyotp.totp.TOTP(user.totp_key)
    response_content = {"totp_key": user.totp_key}
    return response.JsonResponse(response_content, status=202, reason="Expecting OTP")


@ourJWT.Decoder.check_auth()
def test_decorator(request, **kwargs):
    auth = kwargs["token"]
    print(auth)
    return response.HttpResponse()


@require_GET
def pubkey_retrival():
    return response.HttpResponse(crypto.PUBKEY)
