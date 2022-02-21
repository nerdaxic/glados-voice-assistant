import json
import random

# Load jokes from a json file into a "playlist"
file = open("skills/glados-jokes.json")
jokes = json.load(file)

# Shuffle the list
random.shuffle(jokes)

# Global variable to make sure same joke does not come up twice in a row
joke_index = 0;

# Fetch the next joke from the playlist
def fetch_joke(id=False, topic=False):
	global joke_index

	# TODO: filter jokes by topic

	joke = jokes[joke_index]["body"]
	joke_index += 1;

	# Loop the "playlist"	
	if(joke_index > len(jokes)):
		joke_index = 0

	return joke