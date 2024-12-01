import matplotlib.pyplot as plt
import matplotlib
from matplotlib.animation import FuncAnimation
import numpy as np
import time

class Pie_Chart_Data_Visualizer():
    def __init__(self, pie_graph_title="title", colors=["red","blue","purple"], labels = [], data = []):
        plt.ion()
        self.pie_graph_title = pie_graph_title
        self.data = data
        self.labels = labels
        self.fig, self.ax = plt.subplots()
        self.colors = colors

    def update_pie(self, data, labels):
        self.labels = labels
        self.data = data
        self.ax.clear()
        self.ax.pie(self.data,
                    labels=self.labels,
                    autopct='%1.1f%%',
                    colors=self.colors
                    )
        self.ax.set_title(self.pie_graph_title)
        plt.pause(0.001)
        return self

    def show(self):
        plt.show(block=False)
        plt.pause(0.001)
        return self
    
    def close(self):
        plt.close()


# ani = FuncAnimation(fig, update_pie, interval=1000) # Update every 1 second
# plt.show()

# pie = Pie_Chart_Data_Visualizer().update_pie([20,53,22]).show().show()
# time.sleep(3)
# pie.update_pie([76,53,0]).show()
# time.sleep(3)
# pie.update_pie([0,3,4]).show()
# time.sleep(3)
