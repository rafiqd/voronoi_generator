from VoronoiTypes import PriorityQueue, Circle, Beachline, Point, Segment
import math
from pprint import pprint


class Voronoi(object):

    def __init__(self, points, window_x, window_y):
        super(Voronoi).__init__()
        self._points = points
        self.bounding_box_x1 = 0
        self.bounding_box_y1 = 0
        self.bounding_box_x2 = window_x
        self.bounding_box_y2 = window_y
        self._beachline = None
        self.output = []
        self.scanline_x = 0

        self._priority_queue = PriorityQueue()
        for p in points:
            self._priority_queue.push(p)

    def fortunes(self):

        self._beachline = Beachline(self._priority_queue.pop())
        while not self._priority_queue.empty():
            event = self._priority_queue.pop()
            if type(event) == Point:
                self.point_event(event)
            elif type(event) == Circle:
                self.circle_event(event)

        length = self.bounding_box_x2 + (self.bounding_box_x2 - self.bounding_box_x1) + (self.bounding_box_y2 - self.bounding_box_y1)
        current_arc = self._beachline
        while current_arc.next_p is not None:
            if current_arc.out_line is not None:
                endpoint = self.intersection(current_arc.point, current_arc.next_p.point, Point.point_builder(length*2, 0))
                current_arc.out_line.complete_line(endpoint)
            current_arc = current_arc.next_p

        return self.output

    def circle_event(self, event):
        if event.valid:
            segment = Segment(event)
            self.output.append(segment)
            event.arc.remove(segment, event)

            if event.arc.prev_p is not None:
                self.is_circle_event(event.arc.prev_p)
            if event.arc.next_p is not None:
                self.is_circle_event(event.arc.next_p)

    def intersection(self, a, b, c):
        p = a
        if a.x == b.x:
            py = (a.y + b.y) / 2.0
        elif b.x == c.x:
            py = b.y
        elif a.x == c.x:
            py = a.y
            p = b
        else:
            d0 = 2.0 * (a.x - c.x)
            d1 = 2.0 * (b.x - c.x)
            e = 1.0 / d0 - 1.0 / d1
            f = -2.0 * (a.y / d0 - b.y / d1)
            g = (a.y**2 + a.x**2 - c.x**2) / d0 - 1.0 * (b.y**2 + b.x**2 - c.x**2) / d1
            py = (-f - math.sqrt(f**2 - 4*e*g)) / (2*e)

        try:
            px = (p.x**2 + (p.y - py) ** 2 - c.x ** 2) / (2 * p.x - 2 * c.x)
        except:
            px = (p.x ** 2 + (p.y - py) ** 2 - c.x ** 2) / (2 * p.x - 2 * (c.x + 0.000001))

        res = Point.point_builder(px, py)
        return res

    def circle_center(self, a, b, c):

        if ((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) > 0:
            return None, 0

        d = (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y)
        if d == 0:
            return None, 0

        # store these first so we dont keep computing squares
        axay = a.x**2 + a.y**2
        bxby = b.x**2 + b.y**2
        cxcy = c.x**2 + c.y**2
        # calculating determinate to find the center of the circle
        A = a.x*(b.y - c.y) - a.y*(b.x - c.x) + b.x * c.y - c.x * b.y
        B = axay*(c.y - b.y) + bxby*(a.y - c.y) + cxcy*(b.y - a.y)
        C = axay*(b.x - c.x) + bxby*(c.x - a.x) + cxcy*(a.x - b.x)
        D = axay*(c.x*b.y - b.x*c.y) + bxby*(a.x*c.y - c.x*a.y) + cxcy*(b.x*a.y - a.x*b.y)

        A2 = -2*A
        x = B / A2
        y = C / A2

        inside = (B**2 + C**2 - 4*A*D)/(4*A**2)
        radius = math.sqrt(inside)
        return Point.point_builder(x, y), radius

    def intersect(self, point, arc):
        if arc is None:
            return None
        a = 0.0
        b = 0.0

        if arc.prev_p is not None:
            a = self.intersection(arc.prev_p.point, arc.point, point).y
        if arc.next_p is not None:
            b = self.intersection(arc.point, arc.next_p.point, point).y

        if (arc.prev_p is None or a <= point.y) and (arc.next_p is None or point.y <= b):
            py = point.y
            try:
                px = (arc.point.x**2 + (arc.point.y - py)**2 - point.x**2) / (2 * arc.point.x - 2 * point.x)
            except:
                numerator = (arc.point.x**2 + (arc.point.y - py)**2 - point.x**2)
                px = numerator / (2 * arc.point.x - 2 * (point.x + 0.000001) )
            return Point.point_builder(px, py)
        return None

    def is_circle_event(self, arc):
        if arc.next_p is None or arc.prev_p is None:
            # not enough points for a circle yet
            return

        if arc.e is not None and arc.e.x != self.scanline_x:
            arc.e.valid = False
        arc.e = None

        new_circle_point, radius = self.circle_center(arc.prev_p.point, arc.point, arc.next_p.point)
        if new_circle_point is not None and new_circle_point.x + radius > self.scanline_x:
            arc.e = Circle(new_circle_point, radius, arc)
            self._priority_queue.push(arc.e)

    def point_event(self, event):

        current_arc = self._beachline
        intersect_point = None
        while intersect_point is None:
            intersect_point = self.intersect(event, current_arc)
            if intersect_point is None:
                current_arc = current_arc.next_p

        second_intersection = self.intersect(event, current_arc.next_p)
        if second_intersection is None and current_arc.next_p is not None:
            # insert new parabola of the beachline between the two
            # set current one as it's previous, and the currenones neighbor as its next
            extended_beachline_arc = Beachline(current_arc.point, current_arc, current_arc.next_p)
            current_arc.next_p.prev_p = extended_beachline_arc
            current_arc.next_p = extended_beachline_arc
        else:
            # doesn't intersect with anything else so just insert it next
            extended_beachline_arc = Beachline(current_arc.point, current_arc)
            current_arc.next_p = extended_beachline_arc
        current_arc.next_p.out_line = current_arc.out_line

        new_beachline_arc = Beachline(event, current_arc, current_arc.next_p)
        current_arc.next_p.prev_p = new_beachline_arc
        current_arc.next_p = new_beachline_arc
        current_arc = new_beachline_arc

        segment = Segment(intersect_point)
        current_arc.prev_p.out_line = current_arc.in_line = segment
        self.output.append(segment)
        segment = Segment(intersect_point)
        current_arc.next_p.in_line = current_arc.out_line = segment
        self.output.append(segment)
        self.is_circle_event(current_arc)
        self.is_circle_event(current_arc.next_p)
        self.is_circle_event(current_arc.prev_p)




            




