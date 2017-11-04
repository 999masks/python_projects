"""
import numpy as np
import matplotlib.pyplot as plt
x = np.arange(0, 10, 0.1)
y1 = 0.05 * x**2
y2 = -1 *y1
print y1

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()
ax1.plot(x, y1, 'g-')
ax2.plot(x, y2, 'b-')

ax1.set_xlabel('X data')
ax1.set_ylabel('Y1 data', color='g')
ax2.set_ylabel('Y2 data', color='b')

plt.show()

"""
"""
import matplotlib.pyplot as plt
my_xtiks = ['14:51:58','14:51:50','14:51:53','14:51:56','14:51:57','14:51:54']
fig = plt.figure()
host = fig.add_subplot(111)

par1 = host.twinx()
par2 = host.twinx()
par3 = host.twinx()

host.set_xlim(0, 2)
host.set_ylim(0, 2)
par1.set_ylim(0, 4)
par2.set_ylim(1, 65)
#par3.set_ylim(5, 70)

host.set_xlabel("Distance")
host.set_ylabel("Density")
par1.set_ylabel("Temperature")
par2.set_ylabel("Velocity")
par3.set_ylabel("extra")

color1 = plt.cm.viridis(0)
color2 = plt.cm.viridis(0.5)
color3 = plt.cm.viridis(.9)
#color4 = plt.cm.viridis(0.8)

p1, = host.plot([0, 1, 2], [0, 1, 2], color=color1,label="Density")
p2, = par1.plot([0, 1, 2], [0, 3, 2], color=color2, label="Temperature")
p3, = par2.plot([0, 1, 2], [50, 30, 15], color=color3, label="Velocity")
p4, = par3.plot([0, 1, 2], [40, 20, 5], color=color3, label="extra")

lns = [p1, p2, p3, p4]
host.legend(handles=lns, loc='best')

# right, left, top, bottom
par2.spines['right'].set_position(('outward', 60))
# no x-ticks
par2.xaxis.set_ticks([])
# Sometimes handy, same for xaxis
#par2.yaxis.set_ticks_position('right')

host.yaxis.label.set_color(p1.get_color())
par1.yaxis.label.set_color(p2.get_color())
par2.yaxis.label.set_color(p3.get_color())
par3.yaxis.label.set_color(p4.get_color())
plt.savefig("pyplot_multiple_y-axis.png", bbox_inches='tight')
plt.show()
"""
import matplotlib.pyplot as plt

fig = plt.figure()
host = fig.add_subplot(111)

par1 = host.twinx()
par2 = host.twinx()
par3 = host.twinx()

#host.set_xlim(0, 8)
#host.set_ylim(0, 2)
#par1.set_ylim(0, 4)
#par2.set_ylim(1, 65)

host.set_xlabel("Distance")
host.set_ylabel("Density")
par1.set_ylabel("Temperature")
par2.set_ylabel("Velocity")
par3.set_ylabel("xtra")

color1 = plt.cm.viridis(0)
color2 = plt.cm.viridis(0.5)
color3 = plt.cm.viridis(.9)
color4 = plt.cm.viridis(.7)

my_xtiks = ['14:51:58','14:51:50','14:51:53','14:51:56']
plt.xticks([0, 1, 2, 3],my_xtiks )

p1, = host.plot([0, 1, 2, 3], [0, 1, 2,4], color=color1,label="Density")
p2, = par1.plot([0, 1, 2, 3], [0, 3, 2, 6], color=color2, label="Temperature")
p3, = par2.plot([0, 1, 2, 3], [50, 30, 15, 9], color=color3, label="Velocity")
p4, = par3.plot([0, 1, 2, 3], [10, 20, 40, 30], color=color4, label="Xtra")

lns = [p1, p2, p3, p4]
host.legend(handles=lns, loc='best')

# right, left, top, bottom
par2.spines['right'].set_position(('outward', 30))
# no x-ticks
#par2.xaxis.set_ticks([])
# Sometimes handy, same for xaxis
#par2.yaxis.set_ticks_position('right')

host.yaxis.label.set_color(p1.get_color())
par1.yaxis.label.set_color(p2.get_color())
par2.yaxis.label.set_color(p3.get_color())
par3.yaxis.label.set_color(p4.get_color())

plt.savefig("pyplot_multiple_y-axis.png", bbox_inches='tight')

plt.show()