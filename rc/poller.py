# -*- coding: utf-8 -*-
import select


class BasePoller(object):
    is_supported = False

    def __init__(self, objects):
        self.objects = dict(objects)

    def poll(self, timeout=None):
        """The return value is two list of objects that are ready:
        (rlist, wlist).
        """
        raise NotImplementedError()

    def pop(self, host_name):
        return self.objects.pop(host_name, None)

    def __len__(self):
        return len(self.objects)


class SelectPoller(BasePoller):
    is_supported = hasattr(select, 'select')

    def poll(self, timeout=None):
        objs = self.objects.values()
        rlist, wlist, _ = select.select(objs, objs, [], timeout)
        return rlist, wlist


class PollPoller(BasePoller):
    is_supported = hasattr(select, 'poll')

    def __init__(self, objects):
        BasePoller.__init__(self, objects)
        self.pollobj = select.poll()
        self.fd_to_object = {}
        for _, obj in objects:
            self.pollobj.register(obj.fileno(), select.POLLIN | select.POLLOUT)
            self.fd_to_object[obj.fileno()] = obj

    def pop(self, host_name):
        rv = BasePoller.pop(self, host_name)
        if rv is not None:
            self.pollobj.unregister(rv.fileno())
            self.fd_to_object.pop(rv.fileno(), None)
        return rv

    def poll(self, timeout=None):
        rlist = []
        wlist = []
        for fd, event in self.pollobj.poll(timeout):
            obj = self.fd_to_object[fd]
            if event & select.POLLIN:
                rlist.append(obj)
            elif event & select.POLLOUT:
                wlist.append(obj)
        return rlist, wlist


class KQueuePoller(BasePoller):
    is_supported = hasattr(select, 'kqueue')

    def __init__(self, objects):
        BasePoller.__init__(self, objects)
        self.kqueue = select.kqueue()
        self.events = []
        self.fd_to_object = {}
        for _, obj in objects:
            r_event = select.kevent(
                obj.fileno(), filter=select.KQ_FILTER_READ,
                flags=select.KQ_EV_ADD | select.KQ_EV_ENABLE)
            self.events.append(r_event)
            w_event = select.kevent(
                obj.fileno(), filter=select.KQ_FILTER_WRITE,
                flags=select.KQ_EV_ADD | select.KQ_EV_ENABLE)
            self.events.append(w_event)
            self.fd_to_object[obj.fileno()] = obj

    def pop(self, host_name):
        rv = BasePoller.pop(self, host_name)
        if rv is not None:
            self.events = [e for e in self.events if e.ident != rv.fileno()]
            self.fd_to_object.pop(rv.fileno(), None)
        return rv

    def poll(self, timeout=None):
        rlist = []
        wlist = []
        events = self.kqueue.control(self.events, 128, timeout)
        for event in events:
            obj = self.fd_to_object.get(event.ident)
            if obj is None:
                continue
            if event.filter == select.KQ_FILTER_READ:
                rlist.append(obj)
            elif event.filter == select.KQ_FILTER_WRITE:
                wlist.append(obj)
        return rlist, wlist


class EpollPoller(BasePoller):
    is_supported = hasattr(select, 'epoll')

    def __init__(self, objects):
        BasePoller.__init__(self, objects)
        self.epoll = select.epoll()
        self.fd_to_object = {}
        for _, obj in objects:
            self.fd_to_object[obj.fileno()] = obj
            self.epoll.register(obj.fileno(), select.EPOLLIN | select.EPOLLOUT)

    def pop(self, host_name):
        rv = BasePoller.pop(self, host_name)
        if rv is not None:
            self.epoll.unregister(rv.fileno())
            self.fd_to_object.pop(rv.fileno(), None)
        return rv

    def poll(self, timeout=None):
        if timeout is None:
            timeout = -1
        rlist = []
        wlist = []
        for fd, event in self.epoll.poll(timeout):
            obj = self.fd_to_object[fd]
            if event & select.EPOLLIN:
                rlist.append(obj)
            elif event & select.EPOLLOUT:
                wlist.append(obj)
        return rlist, wlist


supported_pollers = [poller for poller in [EpollPoller, KQueuePoller,
                                           PollPoller, SelectPoller]
                     if poller.is_supported]
poller = supported_pollers[0]
