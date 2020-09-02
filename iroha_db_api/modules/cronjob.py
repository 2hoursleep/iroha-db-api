# add huey or mini huey


from gevent import monkey

monkey.patch_all()
import gevent

from huey.contrib.mini import MiniHuey


huey = MiniHuey()

# If we want to support scheduling tasks for execution in the future, or for
# periodic execution (e.g. cron), then we need to call `huey.start()` which
# starts a scheduler thread.
