import os.path
import sys
from mu_repo.config import Config
from .print_ import Print


#===================================================================================================
# Status
#===================================================================================================
class Status(object):

    __slots__ = ['status_message', 'succeeded', 'config']

    def __init__(self, status_message, succeeded, config=None):
        self.status_message = status_message
        self.succeeded = succeeded
        self.config = config

#===================================================================================================
# Params
#===================================================================================================
class Params(object):

    #args = params.args
    #config_file = params.config_file
    #config = params.config

    __slots__ = ['config', 'args', 'config_file']

    def __init__(self, config, args, config_file):
        self.config = config
        self.args = args
        self.config_file = config_file


#===================================================================================================
# PrintTime
#===================================================================================================
def PrintTime(func):
    import time
    def Exec(*args, **kwargs):
        curr_time = time.time()
        ret = func(*args, **kwargs)
        diff = time.time() - curr_time
        Print('Total time: %.2f' % (diff,))
        return ret
    return Exec


#===================================================================================================
# main
#===================================================================================================
def main(config_file='.mu_repo', args=None):
    '''
    Entry point.
    
    Some things we may want to support in the future (and if not, at least keep for referencing):
    
    Searching (http://gitster.livejournal.com/30195.html)
        git grep -l --all-match -e Bar -e Foo
        git log --all-match --grep=APSTUD
        
    
    '''

    if args is None:
        args = sys.argv[1:]

    if len(args) == 0 or (len(args) == 1 and args[0] in ('help', '--help')):
        from string import Template
        msg = '''mu-repo is a command-line utility to deal with multiple git repositories.
        
It works with a .mu_repo file in the current working dir which provides the 
configuration of the directories that should be tracked on commands
(or may be used as a git replacement on directories containing a .git dir).

* ${START_COLOR}mu register repo1 repo2:${RESET_COLOR} Registers repo1 and repo2 to be tracked.
* ${START_COLOR}mu register --all:${RESET_COLOR} Marks for all subdirs with .git to be tracked.
* ${START_COLOR}mu list:${RESET_COLOR} Lists the currently tracked repositories.
* ${START_COLOR}mu set-var git=d:/bin/git/bin/git.exe:${RESET_COLOR} Set git location to be used.
* ${START_COLOR}mu get-vars:${RESET_COLOR} Prints the configuration file

* ${START_COLOR}mu dd:${RESET_COLOR}
     Creates a directory structure with working dir vs head and opens 
     WinMerge with it (doing mu ac will commit exactly what's compared in this
     situation)
     
     Also accepts a parameter to compare with a different commit/branch. I.e.:
     mu dd HEAD^^
     mu dd 9fd88da
     mu dd development

Also, it defines some shortcuts:

${START_COLOR}mu st         ${RESET_COLOR}= git status --porcelain
${START_COLOR}mu co branch  ${RESET_COLOR}= git checkout branch
${START_COLOR}mu mu-patch   ${RESET_COLOR}= git diff --cached --full-index > output to file for each repo 
${START_COLOR}mu mu-branch  ${RESET_COLOR}= git rev-parse --abbrev-ref HEAD (print current branch)
${START_COLOR}mu ac msg     ${RESET_COLOR}= git add -A & git commit -m (the message must always be passed) 
${START_COLOR}mu acp msg    ${RESET_COLOR}= same as 'mu ac' + git push origin current branch.
${START_COLOR}mu shell      ${RESET_COLOR}= On msysgit, call sh --login -i (linux-like env)

Any other command is passed directly to git for each repository:
I.e.:

${START_COLOR}mu pull            ${RESET_COLOR}
${START_COLOR}mu fetch           ${RESET_COLOR}
${START_COLOR}mu push            ${RESET_COLOR}
${START_COLOR}mu checkout release${RESET_COLOR}

Note: Passing --timeit in any command will print the time it took
      to execute the command.
'''
        Print(msg)
        return Status(msg, False)

    exists = os.path.exists(config_file)
    if not exists:
        contents = ''
    else:
        with open(config_file, 'r') as f:
            contents = f.read()
    config = Config.Create(contents)

    if not config.repos:
        if '.' == args[0]:
            del args[0]
            config.repos.append('.')
        elif os.path.exists('.git'):
            #Allow it to be used on single git repos too.
            config.repos.append('.')


    arg0 = args[0]
    if arg0 == 'set-var':
        from .action_set_var import Run

    elif arg0 == 'get-vars':
        from .action_get_vars import Run #@Reimport

    elif arg0 == 'register':
        from .action_register import Run #@Reimport

    elif arg0 == 'dd':
        from .action_diff import Run #@Reimport

    elif arg0 == 'up':
        from .action_up import Run #@Reimport

    elif arg0 == 'sync':
        from .action_sync import Run #@Reimport

    elif arg0 == 'list':
        from .action_list import Run #@Reimport

    elif arg0 == 'ac': #Add, commit
        from .action_add_and_commit import Run #@Reimport

    elif arg0 == 'acp': #Add, commit, push
        def Run(params):
            from .action_add_and_commit import Run #@Reimport
            Run(params, push=True)


    elif arg0 == 'shell':
        import subprocess
        try:
            subprocess.call(['sh', '--login', '-i'])
        except:
            #Ignore any error here (if the user pressed Ctrl+C before exit, we'd have an exception).
            import traceback;traceback.print_exc()
        return

    else:
        from .action_default import Run #@Reimport

    return Run(Params(config, args, config_file))


if '--timeit' in sys.argv:
    sys.argv.remove('--timeit')
    main = PrintTime(main)



