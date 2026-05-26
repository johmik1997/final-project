import hashlib
import json

from django.conf import settings
from django.core.cache import cache
from rest_framework.response import Response


VERSION_TIMEOUT = 60 * 60 * 24 * 30


def _normalize_part(value):
    if isinstance(value, (dict, list, tuple, set)):
        return json.dumps(value, sort_keys=True, default=str)
    return str(value)


def get_namespace_version(namespace: str) -> int:
    key = f"cache-version:{namespace}"
    version = cache.get(key)
    if version is None:
        cache.add(key, 1, timeout=VERSION_TIMEOUT)
        version = cache.get(key) or 1
    return int(version)


def bump_namespace_version(namespace: str) -> int:
    key = f"cache-version:{namespace}"
    if cache.add(key, 2, timeout=VERSION_TIMEOUT):
        return 2
    try:
        return cache.incr(key)
    except ValueError:
        cache.set(key, 2, timeout=VERSION_TIMEOUT)
        return 2


def build_cache_key(namespace: str, *parts) -> str:
    version = get_namespace_version(namespace)
    raw = "::".join(_normalize_part(part) for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"api-cache:{namespace}:v{version}:{digest}"


def build_request_cache_key(request, namespace: str, *extra_parts) -> str:
    user = getattr(request, "user", None)
    user_scope = f"user:{user.id}" if getattr(user, "is_authenticated", False) else "user:anon"
    return build_cache_key(
        namespace,
        request.method,
        request.path,
        request.META.get("QUERY_STRING", ""),
        request.headers.get("Accept-Language", ""),
        user_scope,
        *extra_parts,
    )


def get_or_set_versioned_value(namespace: str, key_parts, builder, ttl: int | None = None):
    ttl = ttl if ttl is not None else int(getattr(settings, "API_RESPONSE_CACHE_TTL", 120))
    cache_key = build_cache_key(namespace, *key_parts)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    value = builder()
    cache.set(cache_key, value, ttl)
    return value


def cache_api_response(namespace: str, request, builder, ttl: int | None = None, *extra_parts):
    ttl = ttl if ttl is not None else int(getattr(settings, "API_RESPONSE_CACHE_TTL", 120))
    cache_key = build_request_cache_key(request, namespace, *extra_parts)
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached, status=200)

    response = builder()
    if getattr(response, "status_code", None) == 200:
        cache.set(cache_key, response.data, ttl)
    return response


class CachedListRetrieveMixin:
    list_cache_namespace = None
    retrieve_cache_namespace = None
    cache_ttl = None

    def list(self, request, *args, **kwargs):
        if not self.list_cache_namespace:
            return super().list(request, *args, **kwargs)
        parent = super(CachedListRetrieveMixin, self)
        return cache_api_response(
            self.list_cache_namespace,
            request,
            lambda: parent.list(request, *args, **kwargs),
            self.cache_ttl,
        )

    def retrieve(self, request, *args, **kwargs):
        if not self.retrieve_cache_namespace:
            return super().retrieve(request, *args, **kwargs)
        parent = super(CachedListRetrieveMixin, self)
        return cache_api_response(
            self.retrieve_cache_namespace,
            request,
            lambda: parent.retrieve(request, *args, **kwargs),
            self.cache_ttl,
        )
