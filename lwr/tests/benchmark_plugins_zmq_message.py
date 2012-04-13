import time
from lwr.plugins.zmq import message
from lwr.planner.plan import Event, Plan, JobTemplate

e = Event(owner='me', bucket='public', name='hg.pushes', data={'rev': '1234567890', 'branch': 'projects/awesomesauce'})
jt = JobTemplate(command="echo hello world", interpreter="bash", data={'extra_args': ['--disable-tests']})
p = Plan(owner='me', bucket='b1', events=["public.hg.pushes"], job_template=jt)
j = p.run(e)

obj = j.asDict()

results = {}

def time_serialize(encoder, compressor, n=1000):
    mh = message.MessageHandler()
    mh.setEncoder(encoder)
    mh.setCompressor(compressor)

    start = time.time()
    for i in xrange(n):
        mh.serialize(obj)
    end = time.time()
    return end-start

def time_unserialize(encoder, compressor, n=1000):
    mh = message.MessageHandler()
    mh.setEncoder(encoder)
    mh.setCompressor(compressor)

    s = mh.serialize(obj)

    start = time.time()
    for i in xrange(n):
        mh.unserialize(s)
    end = time.time()
    return end-start

def len_serialize(encoder, compressor):
    mh = message.MessageHandler()
    mh.setEncoder(encoder)
    mh.setCompressor(compressor)

    s = mh.serialize(obj)
    return len(s)

if __name__ == '__main__':
    results = []
    raw_size = len_serialize('json', 'raw')

    for encoder in message.MessageHandler.encoders:
        if encoder == 'raw':
            continue
        for compressor in message.MessageHandler.compressors:
            try:
                size = len_serialize(encoder, compressor)
                ts = time_serialize(encoder, compressor)
                tu = time_unserialize(encoder, compressor)
            except:
                print "problem with", encoder, compressor
                raise
            size_ratio = size / float(raw_size)
            ts_score = (1-size_ratio) / float(ts)
            tu_score = (1-size_ratio) / float(tu)
            results.append( (encoder, compressor, size, ts, tu, size_ratio, ts_score, tu_score) )

    # Sort by ts_score - how much we've compressed divided by the time it takes
    # to serialize
    results.sort(key=lambda x:x[6])
    print "%s/%s\t%4s %4s %4s %4s %4s" % ("enc", "comp", "sz%", "ts", "tu", "z_ts", "z_tu")
    for encoder, compressor, size, ts, tu, size_ratio, ts_score, tu_score in results:
        print "%s/%s\t%.2f %.2f %.2f %.2f %.2f" % (encoder, compressor, size_ratio, ts, tu, ts_score, tu_score)
    print
