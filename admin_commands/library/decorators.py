from . import wraps, Member, User, deps

def transguild_admin(error_message='У вас нет прав на выполнение этой команды'):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            user: Member | User = None
            for arg in args:
                if hasattr(arg, 'author') and arg.author:
                    user = arg.author
                    break
                elif isinstance(arg, Member):
                    user = arg
                    break
                elif hasattr(arg, 'user'):
                    user = arg.user
                    break
            
            if not user:
                if 'member' in kwargs and isinstance(kwargs['member'], Member):
                    user = kwargs['member']
                elif 'user' in kwargs and isinstance(kwargs['user'], (User, Member)):
                    user = kwargs['user']
                elif 'interaction' in kwargs and hasattr(kwargs['interaction'], 'user'):
                    user = kwargs['interaction'].user
            
            if not user:
                raise ValueError(f'Не удалось определить пользователя в {func.__name__}')
            
            user = deps.capital.get_member(user.id)
            if not user:
                raise ValueError('Не удалось найти пользователя в столичном сервере!')
            
            if not any(deps.a_transguild.id == role.id for role in user.roles): # Исправить
                for arg in args:
                    if hasattr(arg, 'channel') and arg.channel:
                        await arg.channel.send(error_message)
                        break
                    elif hasattr(arg, 'response') and hasattr(arg.response, 'send_message'):
                        await arg.response.send_message(error_message, ephemeral=True)
                        break
                return 
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator