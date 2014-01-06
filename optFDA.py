import random, os, sys, time, shutil
from tempfile import mkstemp
from subprocess import call
from random import Random
import inspyred

""" 
    Copyright (c) 2013, Ergun Bicici <ergunbicici@yahoo.com>
    
    dmin, dmax, cmin, cmax, smin, smax, imin, imax, lmin, lmax values can be changed to select a different space for the optimization.

    numberofprocessors determine the number of processors to use during optimization.

"""

dmin = 0.0001
dmax = 1.0
dtop = 1.0+1e-323
cmin = 0.0
cmax = 3.0001
smin = 0.0
smax = 3.0001
imin = 0.0
imax = 5.0001
lmin = -5.0001
lmax = 5.0001

numberofprocessors = 6
tmpdir = 'tmp'

def parseFDAScores(errfile):
    f = open(errfile, 'r')
    l = f.readline()
    f.close()
    os.remove(errfile)
    parts = l.split()
    tffound = float(parts[-1])
    sffound = float(parts[-4])
    alltf = float(parts[-2])
    allsf = float(parts[-5])
    scov = sffound / allsf
    tcov = tffound / alltf
    numsents = float(parts[-7])
    return (scov, tcov, allsf, alltf, sffound, tffound, numsents)

def generate_randomFDA5Params(random, args):
    d = random.uniform(dmin, dtop)
    c = random.uniform(cmin, cmax)
    s = random.uniform(smin, smax)
    i = random.uniform(imin, imax)
    l = random.uniform(lmin, lmax)
    return [d,c,s,i,l]

def bound_FDA(candidate, args):
    d = max(min(candidate[0], dmax), dmin)
    c = max(min(candidate[1], cmax), cmin)
    s = max(min(candidate[2], smax), smin)
    i = max(min(candidate[3], imax), imin)
    l = max(min(candidate[4], lmax), lmin)
    candidate = [d, c, s, i, l]
    return candidate

def FDAEvalFunction(newguess): #, verbose=0):
    global fda_path, train_source_path, train_target_path, test_source_path, test_target_path, fda_n, fda_numwords
    d = newguess[0]
    c = newguess[1]
    s = newguess[2]
    i = newguess[3]
    l = newguess[4]

    traintest_str = train_source_path + ' ' + test_source_path + ' ' + train_target_path + ' ' + test_target_path
    if not os.path.exists(tmpdir):
        try:
            os.mkdir(tmpdir)
        except:
            pass
    (fd, errfname) = mkstemp(dir=tmpdir)
    cmd = fda_path + ' -v1 -t' + str(fda_numwords) +' -d'+str(d) +' -c'+str(c) + ' -s'+str(s) + ' -i'+str(i)+ ' -l'+str(l)+ ' -n'+str(fda_n) + ' -o /dev/null ' + ' ' + traintest_str + ' 2> ' + errfname
    call(cmd, shell=True)
    (scov, tcov, allsf, alltf, sffound, tffound, numsents) = parseFDAScores(errfname)
#    if verbose:
#        print tcov, scov, '[', ' '.join(map(str, newguess)), ']', 'n:', fda_n
#        sys.stdout.flush()
    return tcov

def evaluate_FDA5(candidates, args):
    fitness = []
    for cs in candidates:
        fit = FDAEvalFunction(cs)
        fitness.append(fit)
    return fitness

def main(configFile, prng=None, display=False):
    if prng is None:
        prng = Random()
        prng.seed(time.time())

    ea = inspyred.ec.ES(prng)
    ea.terminator = [inspyred.ec.terminators.evaluation_termination,
                     inspyred.ec.terminators.diversity_termination,
                     inspyred.ec.terminators.generation_termination]
    final_pop = ea.evolve(generator = generate_randomFDA5Params, 
                          evaluator = inspyred.ec.evaluators.parallel_evaluation_mp,
                          mp_evaluator = evaluate_FDA5, 
                          mp_nprocs = numberofprocessors,
                          pop_size = 100,
                          bounder = bound_FDA,
                          maximize = True,
                          max_evaluations = 10000,
                          max_generations = 5,
                          num_inputs=5)
    
    if display:
        best = max(final_pop) 
        print('Best Solution: \n{0}'.format(str(best)))
    """
    The first n items are the solution, the second n items are the strategy parameters:
    
    The candidate solutions to an ES are augmented by strategy parameters of
    the same length (using ``inspyred.ec.generators.strategize``). These
    strategy parameters are evolved along with the candidates and are used as
    the mutation rates for each element of the candidates. The evaluator is
    modified internally to use only the actual candidate elements (rather than
    also the strategy parameters), so normal evaluator functions may be used
    seamlessly.
    """
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)

def getCommands():
    import ConfigParser
    from optparse import OptionParser
    global fda_path, train_source_path, train_target_path, test_source_path, test_target_path, fda_n, fda_numwords
    
    usage = "usage: %prog [options] arg1 arg2 ..."
    parser = OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-c", "--configfile", dest="configfile",
                      help="supply a user defined configfile")
    (options, args) = parser.parse_args()
    
    if not options.configfile:
        if len(args) == 1:
            parser.error("configfile is required.")
            parser.print_help()
        else:
            parser.error("options other than -c are used with a configfile.")
            parser.print_help()
    else:
        if not os.path.exists(options.configfile):
            parser.error(options.configfile + " does not exist.")
            parser.print_help()
        else:
            print >> sys.stderr, '\nconfigfile:', options.configfile, '\n'
            config = ConfigParser.SafeConfigParser()
            config.read(options.configfile)
            
            # SMTPar: SMT Parameters
            fda_path = config.get('FDAPar', 'fda_path')
            train_source_path = config.get('FDAPar', 'train_source')
            train_target_path = config.get('FDAPar', 'train_target')
            test_source_path = config.get('FDAPar', 'test_source')
            test_target_path = config.get('FDAPar', 'test_target')
            fda_n = config.getint('FDAPar', 'n')
            fda_numwords = config.getint('FDAPar', 'numwords')
#            print fda_path, train_source_path, train_target_path, test_source_path, test_target_path, fda_n, fda_numwords
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
            main(options.configfile, display=True)

if __name__ == '__main__':
    getCommands()
