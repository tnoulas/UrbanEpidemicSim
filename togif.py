#https://stackoverflow.com/questions/753190/programmatically-generate-video-or-animated-gif-in-python
import imageio
import glob
images = []
filenames = (glob.glob("./netgraphs/*.png"))
print (sorted(filenames))

for i in range(0 , max(len(filenames), 160)):
	filename = './netgraphs/nyc_net_' + str(i) + '.png'
	images.append(imageio.imread(filename))
imageio.mimsave('movie.gif', images)

