import tkinter as tk
import sys
import random
import math
from pprint import pprint
from VoronoiTypes import Point
from Voronoi import Voronoi
import time

###########################################################################
## some of the code in this has been adapted from this C++ implementation
## source here: https://www.cs.hmc.edu/~mbrubeck/voronoi.html
###########################################################################

class MainWidget(object):
    _HEIGHT = 800
    _WIDTH = 800
    _RADIUS = 3

    def __init__(self, num_points=500):
        super(MainWidget).__init__()
        #return
        self._NUM_POINTS = num_points
        self._master = tk.Tk()
        self._master.title('Voronoi Maps')
        self._frame = tk.Frame(self._master, relief=tk.RAISED)
        self._frame.pack()
        self._canvas = tk.Canvas(self._frame, width=self._WIDTH, height=self._HEIGHT)
        self._canvas.pack()
        self._build_ui()
        self._master.mainloop()
        self._points = []

    def _build_ui(self):
        self._button_frame = tk.Frame(self._master)
        self._button_frame.pack()

        self._generate_button = tk.Button(
            self._button_frame,
            text='Generate Points',
            command=self._generate_points)
        self._generate_button.pack(side=tk.LEFT)

        self._create_new_voronoi_button = tk.Button(
            self._button_frame,
            text='Create New Voronoi Diagram',
            command=self.create_new_voronoi
        )
        self._create_new_voronoi_button.pack(side=tk.LEFT)

        self._clear_button = tk.Button(
            self._button_frame,
            text='Clear Window',
            command=self.clear_window
        )
        self._clear_button.pack(side=tk.LEFT)

        self._dosomething = tk.Button(
            self._button_frame,
            text='do something',
            command=self.do_thing
        )
        #self._dosomething.pack(side=tk.LEFT)

    def do_thing(self):
        for segment_list in self.reg_list:
            for segment in segment_list:
                slope = (segment.end.y - segment.start.y) / (segment.end.x - segment.start.x)
                # y = mx+b
                b = segment.start.y - slope * segment.start.x

                if segment.start.x < 0:
                    segment.start.x = 0
                    segment.start.y = b
                if segment.start.y < 0:
                    segment.start.y = 0
                    segment.start.x = -b / slope
                if segment.end.x < 0:
                    segment.end.x = 0
                    segment.end.y = b
                if segment.end.y < 0:
                    segment.end.y = 0
                    segment.end.x = -b / slope
                if segment.start.x > self._WIDTH:
                    segment.start.x = self._WIDTH
                    segment.start.y = slope * segment.start.x + b
                if segment.end.x > self._WIDTH:
                    segment.end.x = self._WIDTH
                    segment.end.y = slope * segment.end.x + b
                if segment.start.y > self._HEIGHT:
                    segment.start.y = self._HEIGHT
                    segment.start.x = (self._HEIGHT - b) / slope
                if segment.end.y > self._HEIGHT:
                    segment.end.y = self._HEIGHT
                    segment.end.x = (self._HEIGHT - b) / slope

        for x in self.reg_list:
            a,b = self.calc_centeroid(x)

            self._canvas.create_oval(
                a - self._RADIUS,
                b - self._RADIUS,
                a + self._RADIUS,
                b + self._RADIUS,
                fill='red'
            )

    def calc_centeroid(self, region):
        signed_area = 0
        center_x = 0
        center_y = 0
        for line in region:
            x0 = line.start.x
            x1 = line.end.x
            y0 = line.start.y
            y1 = line.end.y
            a = x0 * y1 - x1 * y0
            signed_area += a
            center_x += (x0 + x1)*a
            center_y += (y0 + y1)*a

        signed_area *= 0.5
        center_x /= 6.0 * signed_area
        center_y /= 6.0 * signed_area
        return center_x, center_y


    def clear_window(self):
        self._canvas.delete(tk.ALL)


    def _generate_points(self):
        self.clear_window()
        self._points = []
        for x in range(self._NUM_POINTS):
            x = random.randint(self._RADIUS, self._HEIGHT)
            y = random.randint(self._RADIUS, self._WIDTH)
            self._points.append(Point.point_builder(x, y))
            self._canvas.create_oval(
                x - self._RADIUS,
                y - self._RADIUS,
                x + self._RADIUS,
                y + self._RADIUS,
                fill='black'
            )

    def create_new_voronoi(self):
        self.current_voronoi = Voronoi(self._points, self._WIDTH, self._HEIGHT)
        start = time.time()
        line_segement_list = self.current_voronoi.fortunes()
        print("Time: %f" % (time.time() - start))
        self.reg_list = []
        for line in line_segement_list:
            start = line.start
            end = line.end
            if start is None or end is None:
                continue
            self._canvas.create_line(start.x, start.y, end.x, end.y, fill='blue')
            #x = self.get_region(line)
            #self.reg_list.append(x)


    def get_region(self, line):
        x = self.get_region_recur_left(line, line, True)
        y = self.get_region_recur_right(line, line, True)

        return list(set(x+y))

    def region_rec_1(self, line, original):
        pass

    def get_region_recur_left(self, line, original, first=False):

        if len(line.end.out_segments) == 0 or (line == original and not first):
            return [line]

        a_dir_vec = Point(line.end.x - line.start.x, line.end.y - line.start.y)
        min_theta = math.pi
        best_line = None
        for otherline in line.end.out_segments:
            b_dir_vec = Point(otherline.start.x - otherline.end.x, otherline.end.y - otherline.start.y)
            theta = self.dot_product(a_dir_vec, b_dir_vec)
            if theta < min_theta:
                best_line = otherline
                min_theta = theta

        if best_line is None:
            return []
        retval = self.get_region_recur_left(best_line, original)
        if line in retval:
            return retval
        return retval + [line]

    def get_region_recur_right(self, line, original, first=False):
        if len(line.end.out_segments) == 0 or (line == original and not first):
            return [line]
        a_dir_vec = Point(line.start.x - line.end.x, line.end.y - line.start.y)
        min_theta = math.pi
        best_line = None
        for otherline in line.start.in_segments:
            b_dir_vec = Point(otherline.end.x - otherline.start.x, otherline.end.y - otherline.start.y)
            theta = self.dot_product(a_dir_vec, b_dir_vec)
            if theta < min_theta:
                min_theta = theta
                best_line = otherline
        if best_line is None:
            return []
        retval = self.get_region_recur_right(best_line, original)
        if line in retval:
            return retval
        return retval + [line]

    def dot_product(self, a, b):
        a_b = a.x * b.x + a.y * b.y
        a_size = math.sqrt(a.x**2 + a.y**2)
        b_size = math.sqrt(b.x**2 + b.y**2)
        theta = math.acos(a_b / (a_size * b_size))
        return theta

def main():
    if len(sys.argv) > 1:
        MainWidget(sys.argv[1])
    else:
        MainWidget()


if __name__ == "__main__":
    main()