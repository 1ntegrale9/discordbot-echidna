import traceback
from functools import wraps
from constant import LOG_CHANNEL_ID

def excepter(func):
    @wraps(func)
    async def wrapped(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except Exception as e:
            orig_error = getattr(e, 'original', e)
            error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
            await self.bot.get_channel(LOG_CHANNEL_ID).send(f'```python\n{error_msg}\n```')
    return wrapped
