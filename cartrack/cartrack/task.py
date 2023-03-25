
from celery import shared_task
from detect_and_track import mymain


@shared_task
def run_detect(loopfile, vdofile):
    saved_result = mymain(cmd=False,custom_arg=['--loop',loopfile,'--source',vdofile])
    
    return saved_result