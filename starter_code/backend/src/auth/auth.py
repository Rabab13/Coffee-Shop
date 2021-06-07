import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import sys
from flask import Flask, abort


AUTH0_DOMAIN = 'vscode.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'

# AuthError Exception

# AuthError Exception
# A standardized way to communicate auth failure modes


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

# '''
# @TODO implement get_token_auth_header() method
#     it should attempt to get the header from the request
#         it should raise an AuthError if no header is present
#     it should attempt to split bearer and the token
#         it should raise an AuthError if the header is malformed
#     return the token part of the header
# '''
def get_token_auth_header():
    auth_head = request.headers.get('Authorization', None)
    if not auth_head:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    splitparts = auth_head.split()
    if splitparts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'The "Bearer" at Authorization header is invalid.'
        }, 401)

    elif len(splitparts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Not found.'
        }, 404)

    elif len(splitparts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = splitparts[1]
    return token

# '''
# @TODO implement check_permissions(permission, payload) method
#     @INPUTS
#         permission: string permission (i.e. 'post:drink')
#         payload: decoded jwt payload

#     it should raise an AuthError if permissions
#  are not included in the payload
#         !!NOTE check your RBAC settings in Auth0
#     it should raise an AuthError if the requested permission
#   string is not in the payload permissions array
#     return true otherwise
# '''


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True

# '''
# @TODO implement verify_decode_jwt(token) method
#     @INPUTS
#         token: a json web token (string)

#     it should be an Auth0 token with key id (kid)
#     it should verify the token using Auth0 /.well-known/jwks.json
#     it should decode the payload from the token
#     it should validate the claims
#     return the decoded payload

#     !!NOTE urlopen has a common certificate error described
#  here: https://stackoverflow.com/questions/50236117/
# scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
# '''


def verify_decode_jwt(token):
    Auth0url = "https://{}/.well-known/jwks.json".format(AUTH0_DOMAIN)
    getdata = urlopen(Auth0url)
    jsondata = json.loads(getdata.read())
    verfiyheader = jwt.get_unverified_header(token)
    if "kid" not in verfiyheader:
        raise AuthError({
            "code": "invalid_header",
            "description": "Header is not found"
        }, 401)

    rs_key = {}
    for key in jsondata['keys']:
        if key['kid'] == verfiyheader['kid']:
            rs_key = {
                "kty": key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if not rs_key:
        raise AuthError({
            "code": "invalid_header",
            "description": "This is not a valid header"
        }, 401)

    try:
        payload = jwt.decode(
            token, rs_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer="https://{}/".format(AUTH0_DOMAIN)
            )
      
        return payload

    # except jwt.ExpiredSignatureError:
    #     raise AuthError({
    #         'code': 'token_expired',
    #         'description': 'Token expired.'
    #         }, 402)

    except jwt.JWTClaimsError:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'invalid_claims'
        }, 401)

    except Exception as E:
        print(E)
# '''
# @TODO implement @requires_auth(permission) decorator method
#     @INPUTS
#         permission: string permission (i.e. 'post:drink')

#     it should use the get_token_auth_header method to get the token
#     it should use the verify_decode_jwt method to decode the jwt
#     it should use the check_permissions method validate
#  claims and check the requested permission
#     return the decorator which passes the decoded
# payload to the decorated method
# '''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except BaseException:
                abort(403)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
