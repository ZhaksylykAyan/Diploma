import hashlib
from django.core.cache import cache
from django.http import HttpResponse

class GlobalCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Только GET-запросы
        if request.method != 'GET':
            return self.get_response(request)

        # Не кэшировать если пользователь авторизован
        if request.user.is_authenticated:
            return self.get_response(request)

        # Уникальный ключ по URL + query params
        cache_key = self._build_cache_key(request)
        cached = cache.get(cache_key)

        if cached:
            return HttpResponse(cached['content'], content_type=cached['content_type'])

        # Генерация нового ответа
        response = self.get_response(request)

        # Только успешные ответы кэшируем
        if response.status_code == 200:
            cache.set(cache_key, {
                'content': response.content,
                'content_type': response['Content-Type'],
            }, timeout=60)  # можно изменить timeout

        return response

    def _build_cache_key(self, request):
        url = request.get_full_path()
        hash_key = hashlib.md5(url.encode()).hexdigest()
        return f"global_cache:{hash_key}"
