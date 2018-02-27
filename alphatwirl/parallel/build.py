# Tai Sakuma <tai.sakuma@gmail.com>
import sys
import logging

from alphatwirl import concurrently, progressbar
from alphatwirl.misc.deprecation import atdeprecated

from .parallel import Parallel

##__________________________________________________________________||
def build_parallel(parallel_mode, quiet=True, processes=4, user_modules=[ ],
                   htcondor_job_desc_extra=[ ]):

    dispatchers = ('subprocess', 'htcondor')
    parallel_modes = ('multiprocessing', ) + dispatchers
    default_parallel_mode = 'multiprocessing'

    if not parallel_mode in parallel_modes:
        logger = logging.getLogger(__name__)
        logger.warning('unknown parallel_mode "{}", use default "{}"'.format(
            parallel_mode, default_parallel_mode
        ))
        parallel_mode = default_parallel_mode

    if parallel_mode == 'multiprocessing':
        return _build_parallel_multiprocessing(quiet=quiet, processes=processes)

    return _build_parallel_dropbox(
        parallel_mode=parallel_mode,
        user_modules=user_modules,
        htcondor_job_desc_extra=htcondor_job_desc_extra
    )

##__________________________________________________________________||
def _build_parallel_dropbox(parallel_mode, user_modules,
                           htcondor_job_desc_extra=[ ]):
    tmpdir = '_ccsp_temp'
    user_modules = set(user_modules)
    user_modules.add('alphatwirl')
    progressMonitor = progressbar.NullProgressMonitor()
    if parallel_mode == 'htcondor':
        dispatcher = concurrently.HTCondorJobSubmitter(job_desc_extra=htcondor_job_desc_extra)
    else:
        dispatcher = concurrently.SubprocessRunner()
    workingarea = concurrently.WorkingArea(
        topdir=tmpdir,
        python_modules=list(user_modules)
    )
    dropbox = concurrently.TaskPackageDropbox(
        workingArea=workingarea,
        dispatcher=dispatcher
    )
    communicationChannel = concurrently.CommunicationChannel(
        dropbox=dropbox
    )
    return Parallel(progressMonitor, communicationChannel, workingarea)

##__________________________________________________________________||
def _build_parallel_multiprocessing(quiet, processes):

    if quiet:
        progressBar = None
    elif sys.stdout.isatty():
        progressBar = progressbar.ProgressBar()
    else:
        progressBar = progressbar.ProgressPrint()

    if processes is None or processes == 0:
        progressMonitor = progressbar.NullProgressMonitor() if quiet else progressbar.ProgressMonitor(presentation = progressBar)
        communicationChannel = concurrently.CommunicationChannel0()
    else:
        progressMonitor = progressbar.NullProgressMonitor() if quiet else progressbar.BProgressMonitor(presentation = progressBar)
        dropbox = concurrently.MultiprocessingDropbox(processes, progressMonitor)
        communicationChannel = concurrently.CommunicationChannel(dropbox = dropbox)

    return Parallel(progressMonitor, communicationChannel)

##__________________________________________________________________||

##__________________________________________________________________||
@atdeprecated(msg='use alphatwirl.parallel.build.build_parallel() instead.')
def build_parallel_multiprocessing(quiet, processes):
    return build_parallel(
        parallel_mode='multiprocessing',
        quiet=quiet, processes=processes
    )

##__________________________________________________________________||
