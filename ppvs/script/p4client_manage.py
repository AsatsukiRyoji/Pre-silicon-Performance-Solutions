#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A mapping test
@author: Guo Shihao
"""
import os,re,sys,time
import subprocess,argparse,shutil

p4client_info = '''
# A Perforce Client Specification.
#
#  Client:      The client name.
#  Update:      The date this specification was last modified.
#  Access:      The date this client was last used in any way.
#  Owner:       The Perforce user name of the user who owns the client
#               workspace. The default is the user who created the
#               client workspace.
#  Host:        If set, restricts access to the named host.
#  Description: A short description of the client (optional).
#  Root:        The base directory of the client workspace.
#  AltRoots:    Up to two alternate client workspace roots.
#  Options:     Client options:
#                      [no]allwrite [no]clobber [no]compress
#                      [un]locked [no]modtime [no]rmdir
#  SubmitOptions:
#                      submitunchanged/submitunchanged+reopen
#                      revertunchanged/revertunchanged+reopen
#                      leaveunchanged/leaveunchanged+reopen
#  LineEnd:     Text file line endings on client: local/unix/mac/win/share.
#  Type:        Type of client: writeable/readonly/graph/partitioned.
#  Backup:      Client's participation in backup enable/disable. If not
#               specified backup of a writable client defaults to enabled.
#  ServerID:    If set, restricts access to the named server.
#  View:        Lines to map depot files into the client workspace.
#  ChangeView:  Lines to restrict depot files to specific changelists.
#  Stream:      The stream to which this client's view will be dedicated.
#               (Files in stream paths can be submitted only by dedicated
#               stream clients.) When this optional field is set, the
#               View field will be automatically replaced by a stream
#               view as the client spec is saved.
#  StreamAtChange:  A changelist number that sets a back-in-time view of a
#                   stream ( Stream field is required ).
#                   Changes cannot be submitted when this field is set.
#
# Use 'p4 help client' to see more about client views and options.

Client: %s

Update: %s

Access: %s

Owner:	%s

Description:
	Created the client by %s.

Root:  %s

Options:	noallwrite noclobber nocompress unlocked nomodtime rmdir

SubmitOptions:	revertunchanged

LineEnd:	local

View:
        //%s/... //%s/...
'''

P4CONFIG_info = '''P4CLIENT=%s
P4PORT=perforceserver.higon.com:1666
'''
p4config_cshrc = '''setenv P4PORT perforceserver.higon.com:1666
setenv P4CLIENT %s
'''
def get_now(which='dhms', delimiter=False):
      #[tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst]
    now= list(time.localtime())
    now= [str(i).zfill(2) for i in now] 
    def case(var):
        return {
            ('all', True): str(now[0]+'/'+now[1]+'/'+now[2]+' '+now[3]+':'+now[4]+':'+now[5]),
            ('dhms', True): str(now[2]+' '+now[3]+'-'+now[4]+'-'+now[5]),
            ('all', False): str(now[0]+now[1]+now[2]+now[3]+now[4]+now[5]),
            ('dhms', False): str(now[2]+now[3]+now[4]+now[5])
        }.get(var, "[get_now]Wrong request")
    return case((which, delimiter))

def call_from_sys(cmd, has_status=False):
    """Call a command from system.
    Deal different situation per python version
    Return: read handler.
    """
    if (sys.version_info > (3, 0)):
        if has_status == False:
            #py2 subprocess has no this getoutput. 3x can also use 2x way
            output = subprocess.getoutput(cmd)
            return output.split()
        else:
            status, output = subprocess.getstatusoutput(cmd)
            return output.split(), status
            #NOTE|return {'result': output.split(), 'status': status}
    else:
        #A handler as a file reader, can be used only once
        r = subprocess.Popen(cmd, shell= True, stdout= subprocess.PIPE, stderr= open(os.devnull,'w')).stdout
        #NOTE|i is byte string type as b'', need to be decoded to str
        return [i.decode() for i in r.readlines() if i != b'\n']
desc = """
1)  Please don't bootenv before you create the client with this manage script.      
"""

def option_parser(type=None):
    
    parser = argparse.ArgumentParser(description='%s ' %desc, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--tar_dir', default= '/project/bowen/b0/arch/username/', dest= 'tar_dir',  help= 'Create the client under username/tar_dir, which must be empty. For example: bowenb0_pv_regr_datetime')
    parser.add_argument('-c', '--client', default= '<yourname_> + tar_dir', dest= 'client', help= 'The client name. For example: yourname_bowenb0_pv_regr_datetime')
    parser.add_argument('-p', '--project', default= 'bowen_b0', dest= 'project', help= 'Client source of mapping. [bowen_a0 | kongming | kongming_c0 | bowen_b0 | bowen_b1 | anshi_gcd | kongming_e2 | bmz_eco | anshi_gdb | llc | bowen_c0 | nmz | bmz_eco2 | anshi_gcd_64cu | bowenc_xcd | yueying | saipan_b0].')
    parser.add_argument('-cl', '--changelist', default= None, dest= 'changelist', help= 'Sync the tree to which you specify changelist')
    #parser.add_argument('--full', default= False, action = 'store_true', dest = 'full_en', help= 'Fulll directory enable, tar_dir(-t) must be the absolute path.')
    #parser.add_argument('-d', '--delete', default= None, dest= 'delete', help= 'Delete client. Must be exactly the same as your client name')
    #parser.add_argument('-r', '--rmv_dir', default= None, dest= 'rmv_dir', help= 'Remove tree directory. Must be exactly the same as your client\'s full dir')

    options = parser.parse_args() 
    return options

# 1.Define a function, need 'directory', 'client', 'user',.
def build_tree (tar_dir, project, client, change_list):
    # 2 Check whether path of the directory exists:
        # If the directory is not empty, The error is reported.  
    user = os.environ['USER']
    # No matter what the path is full or just a target path, get the last dir as the part of the client name.
    _last_tar_dir = tar_dir.split('/')[-1] if tar_dir.split('/')[-1] != '' else tar_dir.split('/')[-2]
    client = user + '_' + _last_tar_dir if client == '<yourname_> + tar_dir' else client
    try: # If try is work, the input target dir is full, do nothing, tar_dir is tar_dir.
        whether_full = re.search('(/\w+)(/\w+)',tar_dir).groups()
    except: # If target dir isn't full, need genetate a target dir.
        tar_dir = '/project/bowen/b0/arch/' + user + '/' + _last_tar_dir if user != 'regressbotpv' else '/project/bowen/b0/arch/' + 'corepv/' + _last_tar_dir
    if os.path.exists(tar_dir) is True:
        if len(os.listdir(tar_dir))!=0: 
            print('The path isn\'t empty, please create a new path.')
            sys.exit()
    # 2.1 When the client 'path doesn't exist, create the path, and go the path:  
    else: 
        os.makedirs (tar_dir)  
    os.chdir(tar_dir)
    print('your client path: ', os.getcwd())
    #3.Modify the variable content of p4client_info, change name and update time information.
    tar_dir_clientfile = (tar_dir + '/' + client + '.template')
    update_time = get_now('all',True)   
    if project == 'bowen_a0':
        server_h = 'dcu/wukong/zifang/gfx_branch/bowen'
    elif project == 'kongming':
        server_h = 'dcu/wukong/kongming/gfx' 
    elif project == 'kongming_c0':
        server_h = 'dcu/subsys/gfx/main/kongming_c0'
    elif project == 'bowen_b0':
        server_h = 'dcu/subsys/gfx/main/bowen_b0'
    elif project == 'bowen_b1':
        server_h = 'dcu/subsys/gfx/main/bowen_b1'
    elif project == 'anshi_gcd':
        server_h = 'dcu/wukong/anshi_gcd/main'
    elif project == 'kongming_e2':
        server_h = 'dcu/subsys/gfx/main/kongming_e2'
    elif project == 'bmz_eco':
        server_h = 'dcu/subsys/gfx/main/bmz_eco'
    elif project == 'anshi_gbd':
        server_h = 'dcu/subsys/gfx/main/anshi_gbd'
    elif project == 'llc':
        server_h = 'dcu/subsys/llc/main'
    elif project == 'bowen_c0':
        server_h = 'dcu/subsys/gfx/main/bowen_c0'
    elif project == 'nmz':
        server_h = 'dcu/subsys/gfx/main/nmz'
    elif project == 'bmz_eco2':
        server_h = 'dcu/subsys/gfx/main/bmz_eco2'
    elif project == 'anshi_gcd_64cu':
        server_h = 'dcu/subsys/gfx/main/anshi_gcd_64cu'
    elif project == 'bowenc_xcd':
        server_h = 'dcu/subsys/gfx/main/bowenc_xcd'
    elif project == 'yueying':
        server_h = 'dcu/subsys/gfx/main/yueying'
    elif project == 'saipan_b0':
        server_h = 'dcu/subsys/gfx/main/saipan_b0'
    f1_temp=p4client_info%(client,\
            update_time,\
            update_time,\
            user,\
            user,\
            tar_dir,\
            server_h,client)
    open(tar_dir_clientfile,'w+').write(f1_temp)
    file_client=open(tar_dir_clientfile,'r')
    # 4. Generate the modified files to a client. There are two meathods.
    #r = subprocess.Popen('p4 client -i ', shell= True, stdin = file_client).stdout
    r = subprocess.Popen('p4 client -i ', shell= True, stdin = file_client, stdout=subprocess.PIPE).stdout
    if r!=None: 
        r0 = [i.decode() for i in r.readlines() if i != b'\n'][0]
        print(r0)
    else:
        print('Create client failed.')
        sys.exit()
    #if the Client is sucessfully created, create P4CONFIG, and p4 sync.
    if 'Client ' + client + ' saved' in r0:
        # 5. Setting environment variables, and p4 sync.
        print("Success create a tree with client name "+client)
        os.environ['P4CLIENT'] = client
        os.environ['P4PORT'] = 'perforceserver.higon.com:1666'
        if change_list:
            call_from_sys('p4 sync @' + change_list)
        else:
            call_from_sys('p4 sync')
        #create P4CONFIG
        open(tar_dir+'/'+'P4CONFIG','w').write(P4CONFIG_info%(client))
        print(P4CONFIG_info%(client))
        ### get the last changelist
        changes = os.popen('p4 changes -m 1 //...#have').read()
        ptn = r'(Change )(\d+)'
        changelist = re.search(ptn, changes).groups()[1]
        if project == 'anshi_gcd':
            open(tar_dir + '/configuration_ID','w').write(changelist)
            open(tar_dir + '/p4config.cshrc', 'w').write(p4config_cshrc%(client))
        else:
            open(tar_dir + '/configuration_id','w').write(changelist)
 

def delete_tree(rmv_dir, delete):
    '''delete your client and your client directory
    :rmv_dir, you must enter your client's full directory
    :delete, your client name
    '''
    call_from_sys('p4 client -d '+ delete)
    shutil.rmtree(rmv_dir)
    
if __name__=='__main__':
    
    opt = option_parser()
    build_tree(opt.tar_dir, opt.project, opt.client, opt.changelist)


    #if opt.tar_dir and opt.project and opt.client:# and opt.user :
    #    if (opt.rmv_dir or opt.delete):
    #        print('Please don\'t use both (-t, -u, -p, -c) and (-d or -r)')
    #        sys.exit()
    #    else:
    #        build_tree(opt.tar_dir, opt.project, opt.client)
    #elif opt.rmv_dir and opt.delete :
    #    delete_tree(opt.rmv_dir, opt.delete)
    #else :
    #    print('absent or incorrent use of paramenter(s).')
    #pass

