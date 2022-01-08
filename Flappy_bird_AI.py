import pygame
import neat
import time
import os
import random

pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

gen = 0

#Double the size of the image which they usually are and load them
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]    
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))


#score font style
STAT_FONT = pygame.font.SysFont("comicsans", 50)


#We'll create bird class which will make our bird moving
class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25 #when goin up how much degree bird will look up(tilt bird upwards and vice-versa)
	ROTATION_VELOCITY = 20 #how much will rotate each frame everytime will move the bird
	ANIMATION_TIME = 5  #how faster we want to show bird animation like its flappying in the frame

	def __init__(self, x, y):
		#initial position of the bird
		self.x = x
		self.y = y
		#each bird will have tilt, how much our bird will be tilted
		self.tilt = 0
		#this is used to find our bird physics, when we jump ,when we fall down, etc
		self.tick_count = 0 
		#Zero as its not moving obviously
		self.velocity = 0 
		self.height = self.y
		#which bird image we are showing now, we can keep track and animate that
		self.img_count = 0
		self.img = self.IMGS[0]

	def jump(self):
		#to move up we need negative velocity
		self.velocity = -10.5
		#keep track of when we last jumped, and its reset zero because we want to know when we changing directon, or changing velocity for our physics formmulas
		self.tick_count = 0
		#keep track from where bird start jumping from
		self.height = self.y

	
	def move(self):
		#A tick happen a frame moved by, will keep track of that
		self.tick_count +=1
		#Displacement i.e. how many pixels we are moving up and down this frame. The tick_counts tell for how many we are moving for
		d = self.velocity*self.tick_count + 1.5*self.tick_count**2 
		#-10.5*1 + 1.5*1 = - so in curr frame we are moving 9 frames upwards n then down causing projectile
		if d >= 16:   #making sure we don't have velocity way too far up and way to far down, i.e. when we reach 16 pixel we dont accelerate anymore
			d = 16
		if d < 0:
			d -= 2 # What it does, if we are moving upwards then lets just move upwards more(momentum), thus fine tune our movement

		#Now change our y position according to the displacement
		self.y = self.y + d

		#now titling the bird, because according to our movement(i.e. up and down) we see our bird tilting up or down
		if d < 0 or self.y < self.height + 50: #case: tilt bird upwards 
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION#move up rotate 25 directly
		else:
			if self.tilt > -90:#Case: downward
				self.tilt -= self.ROTATION_VELOCITY #we dropping down bird must rotate 90 degree to give impressing of droping fast

	def draw(self, window): #window represent the bird we our drawing on to
		self.img_count += 1 # to animate our bird we have to keep track of how many ticks we have shown our image for ie. for how many times our game loop "WHile" has ran

		#bascially we are cal. which Flappy bird image we should show based on image count
		if self.img_count < self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2:
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0

		#Also when our bird is falling ie tilted 90 degree we dont want it to flap
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2 #so when again move upward or jump it goes to level image again so that it dont look like it skipped a frame

		#Rotate image about its center in pygame, as all imagesare level with the screen and we have to tilt or rotate(how to make them go up and down)
		rotate_image = pygame.transform.rotate(self.img, self.tilt) 
		#but now have to move it to center with line below becuase the above line rotate our bird in top left corner
		new_rect = rotate_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
		#now will bilt our rotated image in window at position topleft which is our(x,y)
		window.blit(rotate_image, new_rect.topleft)

	def get_mask(self): #in case of collision
		return pygame.mask.from_surface(self.img)


class Pipe:
	GAP = 200
	VELOCITY = 5

	def __init__(self, x):
		self.x = x
		self.height = 0
		#We keep track where top of our pipe will be drawn and the bottom of the pipe will  be drawn
		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) # for pipe upside down flip the bottom pipe image
		self.PIPE_BOTTOM = PIPE_IMG #originally we have bottom pipe image
		# To check our bird passed the pipe for collision purpose and AI purposes
		self.passed = False 
		self.set_height() #This function will define where the top and bottom of our pipe is, there height ie. how tall bottom v/s top pipe and where is the gap and it will be randomly defined

	def set_height(self):
		#here just get a random number for where the top of our pipe should be
		self.height = random.randrange(50, 450)
		#To figure out where the top of our pipe should be we need to figure out the top left position of the image for our pipe
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		#To move our pipe we just need to change the x position based on the velocity that the pipe should move each frame
		self.x -= self.VELOCITY #ie. move the pipe to its left

	#to draw our pipe both at top and bottom
	def draw(self, window):
		window.blit(self.PIPE_TOP, (self.x, self.top))
		window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	#Pixel perfect collision, will do masking (mask collision) in which there will be two 2-D list of pixel and will see if they collide, ie. they are transparent or not(when collide not transparent) 
	def collide (self, bird):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		#Now cal. offset = which is how far away these masks are from each other
		#offset from the bird to the top mask
		top_offset = (self.x - bird.x, self.top - round(bird.y)) #cant have decimal no. so round
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y)) 

		#now will figure out if these masks collide and this done by finding the point of collision
		#if they dont collide the overlap() return us the None
		b_point = bird_mask.overlap(bottom_mask, bottom_offset) #this tells the point of collision or oint of overlap b/w bird mask and bottom mask using bottom offset, ie. how far that bird is from that bottom pipe
		t_point = bird_mask.overlap(top_mask, top_offset)

		#now check either of the points b_point and t_point exist, so if we aren't colliding then b_point and t_point will be None
		#for every time we move the bird will see it collide on the screen
		if b_point or t_point:
			return True
		return False

class Base:
	VELOCITY = 5 #same as pipe, so they look like they are movin together
	WIDTH = BASE_IMG.get_width() #just how wide out base image is
	IMG = BASE_IMG

	def __init__(self, y): #x will be moving left so no need to define that
		self.y = y
		#make two images of base
		#first will be at 0 and second right of it ie. after width of screen
		self.x1 = 0 
		self.x2 = self.WIDTH

	def move(self):
		#move both with same velocity
		self.x1 -= self.VELOCITY
		self.x2 -= self.VELOCITY

		#when one gets out of the screen to the left then cycle it back to right of the screen so that it came move left again after curr base image, creating a cycle
		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	#just draw the base on window
	def draw(self, window):
		window.blit(self.IMG, (self.x1, self.y))
		window.blit(self.IMG, (self.x2, self.y))


#function that will draw window for our game
def draw_window(window, birds, pipes, base, score, gen):
	#blit means draw
	#draw img of bg at topleft corner at (0,0)
	window.blit(BG_IMG, (0,0))

	#pipe can come as list cause we can have more than 1 pipe on the screen at once
	for pipe in pipes:
		pipe.draw(window)

	#render the score (score, anti-aliasing, color(white here 255,255,255))
	text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
	window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10)) # by this no matter how big our score gets big., will move it left to accomadate it

	#for showing generation
	text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
	window.blit(text, (10,10)) 

	#draw base
	base.draw(window)
	
	#draw the birds too, draw funtion we created above for bird will handle all the animation, tilting and drawing of bird on the window
	for bird in birds:
		bird.draw(window)
	
	#to update screen or refresh it
	pygame.display.update() 



def main(genomes, config):

	#to keep track of generations
	global gen
	gen += 1 
 
	nets = [] #keep track of neural network that controls each bird
	ge = [] #keep track of genomes, so that i can change there fitness based on how far they move or if they hit a pipe 
	birds = [] #keep track of birds, where is there position on the screen
	
	# start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    #genome have{genome_id, genome_obj} ie.eg {1,ge}. We only care about genome_obj
	for genome_id, genome in genomes:
		genome.fitness = 0  #start with fitness level of 0
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		nets.append(net)
		birds.append(Bird(230,350)) #(230, 350) best coordinate for bird 
		genome.fitness = 0  #initially fitness is zero
		ge.append(genome)


	base = Base(730) #at the bottom
	pipes = [Pipe(600)]
	#create a pygame window
	window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	#clock can control how fast the loop will run
	clock = pygame.time.Clock()
	score = 0
	run = True
	#This move() will be called every 30FPS
	while run:
		clock.tick(30)
		for event in pygame.event.get(): #it will see the event like click of mouse, and run our loop through those events
			if event.type == pygame.QUIT: #if we click on close button
				run = False
				pygame.quit() #quit the pygame
				quit() #quit the program as well

		#move the birds based on there NN
		pipe_ind = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): #means if we have passed those pipes, then change the pipe we are looking at to be the second pipe in the list
				pipe_ind = 1
			#if len of bird is not greater than zero than it means we have no birds left and I want to quit this generation and quit running the game too
		else:
			run = False
			break

		#now for of the birds we are gonna move them
		for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
			ge[x].fitness += 0.1 #we giving less fitness point ie. 0.1 as while loop running 30 times in a second (30FPS) so every second bird earn in total 1 point, and will encourage bird to stay alive and not to fly all above the screen or all below
			bird.move()
		

            #now we have to activate our NN with our input
            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

			if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump (can also use over 0, but 0.5 works better here)
				bird.jump()


		add_pipe = False
		rem = []
		for pipe in pipes:
			for x, bird in enumerate(birds):
				if pipe.collide(bird):
					ge[x].fitness -= 1 #bird that hit the pipe will have less fitness than bird that dont hit the pipe so that to encourage bird to go b/w the pipes
					#bird that hit, remove it from the screen and also the associated neural network and genomes with it
					birds.pop(x) 
					nets.pop(x)
					ge.pop(x)


				#check that if we passed the pipe because as soon as we passed the pipe we have to generate a new one for it, so almost before crossing the curr pipe check the passed variable
				if not pipe.passed and pipe.x < bird.x:
					pipe.passed = True
					add_pipe = True

			#check the position of the pipe ie. check pipe is completely off the screen (x pos of pipe and width of it is < 0 then its off)
			#now we can literally remove the pipe list as we are looping on it so we are adding it to a remove pipe list "rem"
			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe)

			


			pipe.move()
		
		#when passed a pipe increase score and add new pipe to the screen
		if add_pipe:
			score += 1
			#give extra 5 fitness points to birds if they pass the pipe, instead ramming them into the pipe
			for g in ge:
				g.fitness += 5
			pipes.append(Pipe(600))

		#remove the pipe from list rem which we passed, as they are off the screen
		for r in rem:
			pipes.remove(r) 

		for x, bird in enumerate(birds):
			#also check if bird hit the floor. Also if some bird reach top of the screen, that should also not survive, because some birds will jump right off the screen or above the pipes
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)

				 


		base.move() 
		draw_window(window, birds, pipes, base, score, gen)





def run(config_path):
	"""
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)


    # Create the population, which is the top-level object for a NEAT run. Bascially creating population based on config file.
	p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal. Stats reporter
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))
	
	# Run for up to 50 generations.
	#run(fitness_fun, generations)
	winner = p.run(main, 50)


if __name__ == "__main__":
	# Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)

