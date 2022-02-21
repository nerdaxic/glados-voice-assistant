import json
import random

# Load answers from a json file into a "playlist"
file = open("skills/glados_magic_8_ball.json")
answers = json.load(file)

# Shuffle the list
random.shuffle(answers)

# Global variable to make sure same answer does not come up twice in a row
answer_index = 0;

# Fetch the next answer from the playlist
def magic_8_ball(id=False, verdict=False):
	global answer_index

	# TODO: filter answers by verdict
	# TODO: fetch spesific answer

	answer = answers[answer_index]["message"]
	answer_index += 1;

	# Loop the "playlist"	
	if(answer_index > len(answers)):
		answer_index = 0
		random.shuffle(answers)

	return answer