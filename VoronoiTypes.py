import heapq


class Point(object):

    point_dict = {}
    point_list = []

    @classmethod
    def point_builder(cls, x, y):
        if x in cls.point_dict:
            if y in cls.point_dict[x]:
                return cls.point_dict[x][y]
            else:
                point = Point(x, y)
                cls.point_dict[x][y] = point
                cls.point_list.append(point)
                return point
        else:
            point = Point(x, y)
            cls.point_dict[x] = {y: point}
            cls.point_list.append(point)
            return point

    def __init__(self, x, y, type='Point'):
        self.x = x
        self.y = y
        self._type = type
        self.in_segments = []
        self.out_segments = []

    def in_lines(self, segment):
        self.in_segments.append(segment)

    def out_lines(self, segment):
        self.out_segments.append(segment)


    def __cmp__(self, other):
        if self.x > other.x:
            return 1
        elif self.x < other.x:
            return -1
        else:
            return 0

    def __lt__(self, other):
        if type(other) == Circle:
            return self.x < other.x + other.radius

        if type(other) == Point:
            return self.x < other.x

    def __str__(self):
        return "%s(%d, %d)" % (self._type, self.x, self.y)

    def __repr__(self):
        return self.__str__()


class Circle(Point):

    def __init__(self, point, r, arc):
        super(Circle, self).__init__(point.x, point.y, type='Circle')
        self.radius = r
        self.arc = arc
        self.valid = True

    def __lt__(self, other):
        if type(other) == Point:
            return self.x + self.radius < other.x
        if type(other) == Circle:
            return self.x + self.radius < other.x + other.radius


class Segment(object):
    def __init__(self, point):
        self.start = point
        self.end = None
        self.done = False

    def complete_line(self, point):
        if self.done:
            return
        self.end = point
        self.done = True
        self.start.out_lines(self)
        self.end.in_lines(self)

    def __str__(self):
        return("%s -> %s" % (self.start, self.end))

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        if self.start.x < self.end.x:
            p1 = self.start
            p2 = self.end
        elif self.start.x > self.end.x:
            p1 = self.end
            p2 = self.start
        elif self.start.y < self.end.y:
            p1 = self.start
            p2 = self.end
        else:
            p1 = self.end
            p2 = self.start
        hashstr = '%s->%s' % (p1, p2)
        return hash(hashstr)


    def __eq__(self, other):
        if self.start == other.start and self.end == other.end:
            return True
        if self.end == other.start and self.start == other.end:
            return True
        return False

class Beachline(object):

    def __init__(self, point, left_neighbor=None, right_neighbor=None):
        self.point = point
        self.prev_p = left_neighbor
        self.next_p = right_neighbor
        self.e = None
        self.in_line = None
        self.out_line = None

    def remove(self, segment, endpoint):
        if self.prev_p is not None:
            self.prev_p.next_p = self.next_p
            self.prev_p.out_line = segment
        if self.next_p is not None:
            self.next_p.prev_p = self.prev_p
            self.next_p.in_line = segment
        if self.in_line is not None:
            self.in_line.complete_line(endpoint)
        if self.out_line is not None:
            self.out_line.complete_line(endpoint)

    def __str__(self):
        previous = []
        nextps = []
        curr = self.prev_p
        while curr is not None:
            previous.append(curr.point)
            curr = curr.prev_p

        curr = self.next_p
        while curr is not None:
            nextps.insert(0, curr.point)
            curr = curr.next_p

        full_list = previous + ['<- previous'] + [self.point] + ['next ->'] + nextps
        return str(full_list)

    def __repr__(self):
        return self.__str__()


class PriorityQueue(object):
    def __init__(self):
        self._priority_queue = []

    def push(self, item):
        if item not in self._priority_queue:
            heapq.heappush(self._priority_queue, item)

    def pop(self):
        return heapq.heappop(self._priority_queue)

    def top(self):
        return self._priority_queue[0]

    def empty(self):
        return len(self._priority_queue) == 0
