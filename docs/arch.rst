================================
Large Wooden Rabbit Architecture
================================

.. contents::

Overview
========
Large Wooden Rabbit is the code name for the next generation of Release
Engineering's build infrastructure.

-----
Goals
-----
LWR will:

* be open source
* be made of reuable components
* be usable outside of Mozilla
* allow you to simply rebuild failed tasks, or hierarchies of tasks. These
  rebuilt tasks can satisfy previous dependency graphs.
* allow you to specify DAGs for job dependencies
* be able to change scheduling at run time via a web interface or API. some
  examples:

  * enable a new branch
  * change tests running on a branch
  * clone an existing branch config and modify it to report to an alternate
    location. This can be used to test out changes to the scheduling
    process.

* operate at scale. This means:

  * support multiple distributed clusters of slaves and 'masters'
  * support 10\ :sup:`5` slaves
  * support 10\ :sup:`5` pending jobs 

* Allow community members or other developer hosted projects to participate
  more easily

  * allow results to be submitted to be associated with e.g.
    mozilla-central changesets. For example, somebody should be able to
    build a static analysis test on his own machine, and have those results
    available in the same place as the official build and test results,
    associated with the revision of mozilla-central he did the tests from.

  * allow external community systems to connect and get jobs from LWR. This
    could be through direct connections, or a pubsub system.

----------
Anti-Goals
----------
LWR will not:

* gain you access to fortified french castles 

----------
Why not X?
----------

Buildbot
--------
Buildbot has served us well, but has a few fundamental limitations that
are very difficult to change or work around:

* require constant connection between build master and slave. This puts a
  high load on network infrastructure which causes burnt builds/tests due
  to dropped connections, and makes it hard to do maintenance on masters.
  Having build slave <-> master(s) communication be resilient to failure or
  being able to have slaves fall over to another master would be a great
  improvement to system stability.

* scheduling is opaque and difficult to change at run-time. buildbot
  doesn't provide much in the way of interfaces to the schedulers.
  Sometimes they log things to the master log files, most of the time
  they don't. Debugging misbehaving schedulers is a bit of a black art.
  Execution of one scheduler can block execution of other schedulers.
  It's also difficult to alter the set of jobs that happen as part of a
  build or test run at runtime. reconfigs don't cut it.

* poor support for non-trivial hierarchies of jobs. If you have a process
  with many fanout and collection points, it's very difficult to
  represent this in buildbot. It's even harder to know reliably when
  everything in the process is done.

* no single source of truth for build status. We've been maintaining our
  own mysql database to store build status, but it's not directly
  associated with the schedulerdb. Providing a consistent view of these
  databases is complicated; exports to other applications is expensive and
  complex.

Jenkins/Hudson
--------------
Jenkins seems well suited to simple processes, but for handling a large set
of complex tasks.

I really don't know it well enough to evaluate though. It's written in java
though :\\


Components
==========

.. image:: arch.png

-------
Planner
-------
The planner is responsible for responding to events and creating new jobs.
The planner maintains a list of Scheduler_\ s that respond to incoming
events and create new jobs to run in reponse to those events.

`Planner`_ -> `Job Queue`_
--------------------------
The `planner`_ has a one-way communication with the `job queue`_, it simply
notifies the `job queue`_ of new jobs to run.

* New job

---------
Job Queue
---------
The `job queue`_ is responsible for tracking new jobs, sending them for
execution to the `slave wrangler`_ if required, or queuing them up for later
processing.

All modifications to jobs are done through this component. This includes
cancelling or pausing jobs.

TODO:
It's a bit weird that there's little reading done from the queue. It looks
like a scheduler will have to query status_ to find old jobs/jobsets to act
on. either that or `job queue`_ will duplicate a lot of status_, which
doesn't seem like a good idea.

HTTP API
--------

``POST /jobqueue/v0.1/<bucket>/jobs``
    create a new job
    the id for the job is returned by this call

``POST /jobqueue/v0.1/<bucket>/job/<jobid>/trigger``
    fire a trigger
    TODO: Use events for this instead?

``PUT /jobqueue/v0.1/<bucket>/job/<jobid>``
    modify this job's state to cancel it, merge it, etc.

ZMQ API
-------
The `job queue`_ server(s) listen on a REP socket. Requests are made by
clients using a REQ socket with the following format:

TODO


`Job Queue`_ -> `Slave Wrangler`_
---------------------------------
* Run job A on slave X

`Job Queue`_ -> Status_
-----------------------
* Job A is new, running, pending, etc.

--------------
Slave Wrangler
--------------
Receives jobs from the `job queue`_ and runs them on slaves.

Mostly just a broker to talk to slaves.

`Slave Wrangler`_ -> `Slave`_
------------------------------
* Run job A

-----
Slave
-----
Slaves do work!

Slave_ -> `Job Queue`_
----------------------
* Create new job
* Send trigger (TODO: should this go via events? - that lets regular
  subscriptions to event types work for the jobset scheduler)
* Delete jobs (e.g. a scheduler job could cancel other pending work)
* Merge jobs (e.g. a scheduler job could merge pending work together)

Slave_ -> Files_
----------------
* Upload files and logs, store urls
* See also `Files -> Slave`_

Slave_ -> Status_
-----------------
Notification of job status: started, finished, including meta data like:

* build started/finished
* start/stop time
* per-step start/stop time
* results (success, failure, etc.)
* rich results (??? e.g. multi l10n repacks)
* urls to logs, files
* See also `Status -> Slave`_

------
Status
------
Get and retrieve status on individual jobs and job sets.

HTTP API
--------
``GET /status/v0.1/<bucket>/jobs/<jobid>``
    get status about job $jobid

``GET /status/v0.1/<bucket>/jobsets/<jobsetid>``
    get status about $jobsetid

``GET /status/v0.1/<bucket>/bytags/<tags>``
    get status about jobs associated with $tags

``POST /status/v0.1/<bucket>/jobs``
    TODO: is this required? this doesn't actually cause a new job to get run
    create new job

``POST /status/v0.1/<bucket>/jobsets``
    TODO: is this required? this doesn't actually cause a new jobset to exist
    create new jobset

``PUT /status/v0.1/<bucket>/jobs/<jobid>``
    update job

``PUT /status/v0.1/<bucket>/jobsets/<jobsetid>``
    update job set

Except for searching for things by tag, this looks an awful lot like S3....

ZMQ API
-------
The Status_ server(s) listen on a REP socket. Requests are made by clients
using a REQ socket with the following format:

* Frame 0
    ``version``
        status protocol version (0.1)

    ``auth``
        authentication information

    ``bucket``
        which bucket we're talking to

    ``method``
        ``getjob``, ``getjobset``, ``newjob``, ``newjobset``, ``updatejob``,
        ``updatejobset``

* Frame 1
    ``job`` or ``jobset`` data

Status_ -> Slave_
-----------------
* fetch status of old jobs (e.g. a scheduler job might want to know state of other jobs)

Status_ -> Event_
------------------
* job finished
* job added

-----
Event
-----
Events are used by a few things in LWR:
* notifications of external things that require action, e.g.

  * hg pushes

  * request for custom build

* internally generated events

  * build finished. this in turn can trigger another scheduler to run more
    builds / tests

  * build trigger. e.g in our existing build process we run 'sendchange'
    after uploading so that tests can get started before things like 'make
    check' are run.

* most events are published for external consumers via http or rmq

  * event publishing controlled by bucket policy?

Events are specified as a tuple ``(bucket.name, data)``, eg.
``('releng.hg.mozilla-central', {'revision': 'abcdef123456'})``

Event_ -> Planner_
------------------
* new pushes to hg / git / cvs / etc.
* triggers
* builds starting / builds stopping

-----
Files
-----
Files and logs go here.

The APIs for this should be pretty simple. You need to be able to upload a file and get back a URL. The existing scp / post_upload.py would suffice.

Files_ -> Slave_
----------------
* Download files

Objects
=======

---------
Scheduler
---------
A scheduler is basically a job template with a list of event subscriptions.
The job template will be instantiated when a matching event is received by
the planner. The event will be attached to the job and then sent to the
`job queue`_.

Schedulers are managed and triggered by the planner_.

A scheduler can be specified thought of as a tuple of
(``owner``, ``bucket``, ``event_type``, ``job_template``, ``data``).

``event_type`` doesn't have to be in ``owner``'s bucket, as long as
``owner`` has read access to ``event_type``'s bucket.

``event_type`` is split on the
period (``.``), and the first element is treated as the bucket. Everything
after that is arbitrary.

Some examples:

* A "jobset" scheduler subscribes to "<bucket>.build.finished", "<bucket>.build.trigger", "<bucket>.jobsets.new" events
  and creates a job that determines if any new jobs in a jobset are
  runnable.

* A "mozilla" scheduler subscribes to hg push events and creates a full
  hierarchy of builds and tests (a `job set`_) with proper dependencies
  between them.

-------
Job Set
-------
A job set is a `directed acyclic graph`_ that describes a hierarchy of jobs
to run and how they're related. An example would be the set of builds
created for an hg push, and the tests for that build. The tests depend on
the builds to succeed. By creating everything under a single jobset you can
know when everything is completed or not, and have a place to look up all
the results associated with a single push.

Another example would be our release automation. We have a fairly complex
set of dependencies between tagging / builds / repacks / updates (en-US
builds depend on en-US tagging, repacks depend on locale tagging and en-US
builds, updates depend on builds, partner repacks depend on repacks, virus
scan depends on everything, ...)

Sample format::

    A -> B -> C
         B -> D
              D -[trigger t1]-> F
         B -[onfailure]-> E

Where A,B,C,D,E are job ids. A is run first.
If A succeeds, then B is run.
If B succeeds, then C and D are run.
If B fails, then E is run.
If D generates trigger t1, then F is run

.. _directed acyclic graph: http://en.wikipedia.org/wiki/Directed_acyclic_graph

To submit a job set, each job in the set should be created first with
state=waiting, and then the jobset can be created referencing all the job
ids. Once the jobset is submitted the jobset scheduler will run and mark
any jobs in the jobset as runnable.

---
Job
---
A job is an object that has the following fields:

* ``id``
    a unique identifier for the job

* ``command``
    the command to run

* ``tags``
    list of strings to tag the jobs with. some of these may be restricted
    due to policy

* ``starttime/stoptime``

* ``state``
    One of:

    ``pending``
        this job is waiting for something else to complete before it can run
    ``runnable``
        this job can be run
    ``running``
        this job is running
    ``finished``
        this job is done

* ``status``
    a code indicating whether the job was successful, failed, etc.

* ``required_slave_tags``
    what type of slave this job needs

* MOAR!

Access control
==============
*This section isn't finished yet - just some random thoughts here for now*

What about buckets? S3 gives coarse grain access control with
buckets...that's nice!  It's also gives you a separate namespace per
bucket, which is also nice!

possible buckets:

- mozilla-central
- mozilla-inbound
- nanojit
- thunderbird/mozilla-central
- mozilla-release
- seamonkey/mozilla-central
- emscripten
- tenfourfox/mozilla-central
- fuzzing
- mozilla_releng

however, access control at a per bucket level would make it hard for
community projects to be involved, unless they were given their own bucket.
in the case of several projects based around a single repository, but
spread across many buckets, status reporting tools (like tbpl) would need
to know to look in different buckets for results. The status_ API could
include querying by bucket as well as by tag, or buckets could be an
implicit tag.

Can we have hierarchical name spaces?

- mozilla-central.firefox
- mozilla-central.tenfourfox
- mozilla-central.thunderbird

instead, can we have ACLs on certain tags?

e.g.:
    "mozilla-central": requires auth releng

    "mozilla-central", "static-analysis": requires auth foo

    "mozilla-central", "comm-central", "seamonkey": requires auth bar

    "mozilla-central", "release": requires auth releng

the more I think about this, the more I like buckets. trying to resolve
ACLs on sets of tags seems complicated.

having a single flat bucket namespace is clean and simple.

Resource policies
=================
We need to enforce certain kind of resource policies or prioritizations,
e.g.:

- mozilla-central builds are more important than elm

- fuzzing jobs should only happen at idle time, and make sure that it
  doesn't consume all available slaves

- mozilla-central should be guaranteed X% of the resources

- guarantee Y% to developer / community jobs.

TODO
====

* Policy control

  * who can run what type of jobs, and how often?
  * control over tags
  * resource allocation

* Split up `job queue`_ into pieces that queue jobs, mark as runnable, etc.?

  * marking jobs as runnable is handled by a scheduler that manages job
    sets.

* Integration with other tools, like tree status - when tree is closed,
  stop new jobs from getting scheduled. When infra fails, automatically
  close tree.

* Data integrity - how do we ensure that commands and build artifacts are
  transferred throughout the system without tampering

* Managing secrets. Lots of times we have slaves deal with sensitive
  information. How can we get secrets on and off of the slaves securely?

* Log streaming. It would be nice to be stream log files to developers. I
  think zmq would be great for this.

* MOAR buckets!

  * planner could list schedulers by bucket. auth'ed users could change the
    scheduling for their bucket

  * events are per bucket

  * files are per bucket

* specify ZMQ message encoding

* reaper
  ttls

* timers (for generating events)
