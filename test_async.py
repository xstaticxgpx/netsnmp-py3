#!/usr/bin/python3

from netsnmp._api import get_async
from async_devtypes import SNMP_DEVTYPES
#import cx_Oracle
import zmq
import redis, hiredis
import logging, logging.handlers
import queue, random, sys, threading, time
import multiprocessing as mp

# command name
cmdname = sys.argv[0]

# configure short loglevel names
logging._levelToName = {
    logging.CRITICAL: 'CRI',
    logging.ERROR:    'ERR',
    logging.WARNING:  'WAR',
    logging.INFO:     'INF',
    logging.DEBUG:    'DBG',
    logging.NOTSET:   'NOSET',
}

# DB definitions
DB = {
    "db": {
        'server': 'host',
        'port'  : '1521',
        'name'  : 'name',
        'user'  : 'user',
        'pass'  : 'pass',
    },
}

### Global definitions
#BUG: udp sendto failures when 49116 > MAX_WORKERS*MAX_PER_WORKER > 49112
# limitation lies somewhere between 49112 and 49116(??) - getting EPERM (1)... kernel dropping?
#http://comments.gmane.org/gmane.comp.security.firewalls.netfilter.devel/29993
# Ceiling is around 8 * 4096 = 32768 max requests at any given time
# or 4096*12 = 3072*16 = 49152
MAX_WORKERS = 4
MAX_PER_WORKER = 4096

# Number of ZMQ PULL processes to spawn
ZMQ_PROCESSORS = 2

# Time to pause for ZMQ initialization (Seconds)
ZMQ_PAUSE=0.01

# ZMQ High water mark
ZMQ_HWM=10000000

# ZMQ endpoints
ZMQ_IN  = "ipc:///tmp/%s_in" % cmdname
ZMQ_OUT = "ipc:///tmp/%s_out" % cmdname

## SNMP
# SNMP timeout is in milliseconds
SNMP_TIMEOUT=1250
SNMP_RETRIES=1
SNMP_TIMEOUT_DELTA=MAX_WORKERS

# Response callback message intake/processing
def ZMQProcessor(success, timeout, oidcount):
    """
    Intake work via ZeroMQ IPC socket and queue for processing after _sentinel is signaled
    """
    # ZeroMQ Message Frame pointers ([OP, HOST, DEVTYPE, OIDS..])
    OP=0
    HOST=1
    DEVTYPE=2
    OIDS=3
    # Local counters, rolled up into mp.Value at end
    _type_count = {}
    _success = 0
    _timeout = 0
    _oidcount = 0

    # Processor ZMQ PULL socket
    incoming = zmq.Context().socket(zmq.PULL)
    incoming.setsockopt(zmq.RCVHWM, ZMQ_HWM)
    incoming.connect(ZMQ_OUT)

    log.debug('Starting up...')

    ## Intake

    _redis = redis.Redis(host='127.0.0.1')
    with _redis.pipeline() as _redispipe:
        i=0
        # Pull messages via ZMQ, process and ship to Redis
        while True:
            response = [frame.decode() for frame in incoming.recv_multipart()]
            if response[OP] == '_sentinel':
                log.debug('Shutting down ZMQ_PULL socket...')
                incoming.close()
                break

            elif response[OP] == '1':
                _success+=1
 
                try:
                    _type_count[response[DEVTYPE]]+=1
                except KeyError:
                    # Need to define
                    _type_count[response[DEVTYPE]]=1

                # Parse OIDs
                _vars = SNMP_DEVTYPES[response[DEVTYPE]].parse_oids(response[OIDS:])
                _oidcount+=len(_vars)
                #log.debug(_vars)
                try: 
                    #log.debug("%s [%s] %s", response[HOST], response[DEVTYPE], vars)
                    # splice if ipv6
                    _redispipe.hmset(response[HOST] if not response[HOST][:4]=="udp6" else response[HOST][6:][:-1],
                                 _vars)
                    i+=1
                except redis.exceptions.RedisError as e:
                    log.debug('redis exception: %s %s:%s', str(e).strip(), response[HOST], _vars)
                    continue
                # Flush redis pipeline periodically
                if i > 4096:
                    _redispipe.execute()
                    i=0

            elif response[OP] == '2':
                _timeout+=1

        _redispipe.execute()

    # Counter rollup
    with success.get_lock():
        success.value+=_success
    with timeout.get_lock():
        timeout.value+=_timeout
    with oidcount.get_lock():
        oidcount.value+=_oidcount

    #log.info('Finished processing %d responses in %.3fs' % (qsize, elapsed))
    log.info('Processed %d responses', (_success+_timeout))
    log.debug('%s', _type_count)

# Messaging Pipeline
def ZMQStreamer(running):
    """
    Proxy ZeroMQ via pipeline (zmq.STREAMER)
    """

    incoming = zmq.Context().socket(zmq.PULL)
    incoming.setsockopt(zmq.RCVHWM, ZMQ_HWM*MAX_WORKERS)
    incoming.bind(ZMQ_IN)

    outgoing = zmq.Context().socket(zmq.PUSH)
    outgoing.setsockopt(zmq.SNDHWM, ZMQ_HWM*ZMQ_PROCESSORS)
    outgoing.bind(ZMQ_OUT)

    log.debug('Starting up...')
    with running.get_lock():
        running.value = 1
    zmq.device(zmq.STREAMER, incoming, outgoing)

if __name__ == '__main__':

    #db = DB['db']
    #dbh = cx_Oracle.connect('%s/%s@%s/%s' % (db['user'], db['pass'], db['server'], db['name']))

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s.%(msecs)03dZ [%(processName)s/%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S')
    log = logging.getLogger(__name__)

    _log_queue = queue.Queue()
    log_async  = logging.handlers.QueueHandler(_log_queue)
    log_queue  = logging.handlers.QueueListener(_log_queue, *log.handlers)

    log_queue.start()

    # Overwrite handlers to only utilize QueueHandler()
    log.handlers = [log_async,]

    #select = dbh.cursor()
    #select.arraysize = 4096

    query = "select something from somewhere"
    community = "public"

    CM_IP = 0
    MODEL = 1

    # Absolute start timer
    _start = time.time()
    # Step timer
    start = time.perf_counter()
    #list(tuple(peername str, community str, devtype str, devtype class instance)..)
    hosts = [(
         "udp6:["+host[CM_IP]+"]" if host[CM_IP][4]==':' else host[CM_IP],
         community,
         host[MODEL] if host[MODEL] in SNMP_DEVTYPES else '__other__',
         SNMP_DEVTYPES[host[MODEL]] if host[MODEL] in SNMP_DEVTYPES else SNMP_DEVTYPES['__other__']
         ) for host in (('archt01', 'other'), ('archt02', 'other'), ('archt03', 'other'), ('archt04', 'other'), ('archt05', 'other'))*20000]
    #select.close()
    #dbh.close()
    total = len(hosts)
    end = time.perf_counter()
    log.info('got %d hosts from DB in %.3fms' % (total, (end-start)*1000))

    try:
        ## Global multiprocessing-safe counters
        success = mp.Value('i', 0)
        timeout = mp.Value('i', 0)
        oidcount = mp.Value('i', 0)
        ## ZMQStreamer switch (set to 1 after successful initialization)
        zmq_streamer_running = mp.Value('i', 0)


        # Start ZeroMQ Streamer
        zmq_streamer = mp.Process(target=ZMQStreamer,
                                   args=(zmq_streamer_running,),
                                   name='ZMQStreamer',
                                   daemon=True)

        zmq_streamer.start()

        # Let the ZMQ sockets start up
        time.sleep(ZMQ_PAUSE)
        if not zmq_streamer_running.value == 1:
            raise RuntimeError("ZMQStreamer failed to initialize")

        # Spin up ZeroMQ Processors
        zmq_processors = []
        for i in range(ZMQ_PROCESSORS):
            zmq_processors.append(
                mp.Process(target=ZMQProcessor,
                            args=(success, timeout, oidcount),
                            name='ZMQProc-%03d' % (i+1),
                            daemon=True)
            )
            zmq_processors[-1].start()

        time.sleep(ZMQ_PAUSE)

        # List of multiprocessing.Process() objects (worker processes)
        active_workers = []
        
        # Worker/process id iterator
        p=0
        # Host index range iterator
        i=0
        # While any hosts or workers exist
        start = time.perf_counter()
        _timeout = SNMP_TIMEOUT
        while hosts or active_workers:
            remaining = total-i
            if hosts and len(active_workers) < MAX_WORKERS:
                #_timeout = SNMP_TIMEOUT+random.randint(p%2, SNMP_TIMEOUT_DELTA)
                _upper = i+MAX_PER_WORKER if remaining > MAX_PER_WORKER else i+remaining
                log.debug('Defining process for range %d:%d (%d*%dms)', i, _upper, (SNMP_RETRIES+1), _timeout)

                # Define process(es) which call get_async C function
                # get_async([(str hostname, str community, [str oid,..])..], int timeout_ms, int retries, int ZMQ_HWM, str ZMQ_IN)
                active_workers.append(
                    mp.Process(target=get_async,
                                args=(hosts[:MAX_PER_WORKER], 
                                      _timeout,
                                      SNMP_RETRIES, 
                                      ZMQ_HWM, 
                                      ZMQ_IN), daemon=True)
                )
                active_workers[-1].start()

                del hosts[:MAX_PER_WORKER]
                i+=MAX_PER_WORKER
                if len(active_workers) < MAX_WORKERS:
                    p+=1
                    # test, slow initial startup
                    time.sleep((SNMP_TIMEOUT/MAX_WORKERS)/1000)
                    continue
                else:
                    p=0

            pids = [proc.pid for proc in active_workers]
            log.debug('Process PIDs: %s' % pids)

            # Continually monitor progress and re-loop when all workers are finished, or maintain process pool with force_reloop
            while active_workers:
                force_reloop = False
                for proc in active_workers:
                    if proc.is_alive():
                        continue
                    else:
                        active_workers.remove(proc)
                        if proc.exitcode == 0:
                            log.debug('%d - Process finished' % proc.pid)
                        else:
                            log.error('%d - Process failed (%d)' % (proc.pid, proc.exitcode))
                        # if processes take variable amount of time, might want to break and loop to start a new process
                        # this ensures MAX_WORKERS processes active at all times
                        force_reloop = True
                        break
                if force_reloop:
                    break

        # Finally, raise successful completion
        raise SystemExit

    except RuntimeError as e:
        log.critical("%s", e)

    except SystemExit:
        # Exit with success

        end = time.perf_counter()
        elapsed = end-start
        log.info('Polling completed in %.3fs' % elapsed)

        __start = time.perf_counter()
        log.debug('Waiting for ZMQProcessors...')
        # Signal end to ZMQProcessor(s)
        zmq_sentinel = zmq.Context().socket(zmq.PUSH)
        zmq_sentinel.connect(ZMQ_IN)
        for _ in range(ZMQ_PROCESSORS):
            zmq_sentinel.send(b'_sentinel')
        zmq_sentinel.close()

        # Wait for ZMQProcessor(s) to complete
        while zmq_processors:
            for zmq_processor in zmq_processors:
                zmq_processor.join()
                zmq_processors.remove(zmq_processor)

        __elapsed = time.perf_counter()-__start
        log.debug('ZMQProcessors took an additional %.3fs', __elapsed)

        log.info('from %d total hosts got %d timeouts (%.1f%%)' % (total, timeout.value, ((timeout.value/total)*100)))
        log.info('got %d oid responses from %d hosts' % (oidcount.value, success.value))
        log.info('lost %d hosts' % (total-(success.value+timeout.value)))
        log.info('%.2f oids/sec' % (oidcount.value/elapsed))
        log.info('%.2f reqs/sec' % ((success.value+timeout.value)/elapsed))

    finally:

        _end = time.time()
        _elapsed = _end-_start
        log.info('total time taken %.3fs' % _elapsed)

        # Ensure logging is flushed
        log_queue.stop()

