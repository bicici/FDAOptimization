import time, os, sys
import subprocess
from subprocess import call

def callFDA(params, setting, outfile):
    fda_path, train_source_path, train_target_path, test_source_path, test_target_path, fda_n, fda_numwords = setting
    d = params[0]
    c = params[1]
    s = params[2]
    i = params[3]
    l = params[4]
    
    traintest_str = train_source_path + ' ' + test_source_path + ' ' + train_target_path + ' ' + test_target_path
    cmd = fda_path + ' -v1 -t' + str(fda_numwords) +' -d'+str(d) +' -c'+str(c) + ' -s'+str(s) + ' -i'+str(i)+ ' -l'+str(l)+ ' -n'+str(fda_n) + ' -o ' + outfile + ' ' + traintest_str
    call(cmd, shell=True)

def parseParameters(fname):
    f = open(fname, 'r')
    lines = f.readlines()
    f.close()
    if not lines[-2].strip() == 'Best Solution:':
        print 'Not optimized:', fname
        return ([], 0.0)
    '[0.9708416233889112, 1.967478145261805, 1.7272752956318222, 2.4181764466803015, -2.1316843143114115, 1.566880023155688, 1.9711510539714792, 1.4458724192714572, 1.248709529467827, 1.419752034088665] : 0.775379519735'
    parts = lines[-1].strip().split(':')
    tcov = float(parts[1])
    weights = eval(parts[0])
    params = weights[:5]
    return (params, tcov)

def getSettings(configfile):
    import ConfigParser
    if not os.path.exists(configfile):
        print configfile + " does not exist."
    else:
        config = ConfigParser.SafeConfigParser()
        config.read(configfile)
        fda_path = config.get('FDAPar', 'fda_path')
        train_source_path = config.get('FDAPar', 'train_source')
        train_target_path = config.get('FDAPar', 'train_target')
        test_source_path = config.get('FDAPar', 'test_source')
        test_target_path = config.get('FDAPar', 'test_target')
        fda_n = config.getint('FDAPar', 'n')
        fda_numwords = config.getint('FDAPar', 'numwords')
        if not os.path.exists(fda_path):
            print fda_path, 'does not exist.'
            sys.exit()
        if not os.path.exists(train_source_path):
            print train_source_path, 'does not exist.'
            sys.exit()
        if not os.path.exists(train_target_path):
            print train_target_path, 'does not exist.'
            sys.exit()
        if not os.path.exists(test_source_path):
            print test_source_path, 'does not exist.'
            sys.exit()
        if not os.path.exists(test_target_path):
            print test_target_path, 'does not exist.'
            sys.exit()
        return (fda_path, train_source_path, train_target_path, test_source_path, test_target_path, fda_n, fda_numwords)

def runExperiment(configfile, numproc=0):
    import optFDA
    stime = time.time()
    # Run FDA optimization
    settings = getSettings(configfile)
    print 'optimization settings:', settings
    if numproc > 0:
        cmd = 'python /ichec/home/users/ebicici/SMT/Tools/FDA/FDAOptimization/optFDA.py -c ' + configfile + ' -p ' + str(numproc) + ' > ' + configfile+'.optparams'
        call(cmd, shell=True)
    else:
        cmd = 'python /ichec/home/users/ebicici/SMT/Tools/FDA/FDAOptimization/optFDA.py -c ' + configfile + ' > ' + configfile+'.optparams'
        call(cmd, shell=True)
    print 'Optimization took:', time.time() - stime
    
    fdastime = time.time()
    settings = getSettings(configfile)
    (params, tcov) = parseParameters(configfile+'.optparams')
    
    outfile = configfile + '.selection'
    callFDA(params, settings, outfile)
    print 'FDA5 took:', time.time() - fdastime
    
    print 'Overall time:', time.time() - stime

if __name__ == '__main__':
    configfile = sys.argv[1]
    if len(sys.argv) == 3:
        numproc = int(sys.argv[2])
    else:
        numproc = 0
    runExperiment(configfile, numproc)

