import random
import os
import sys
import discord

#Token
TOKEN = ""

#Static Input Lists
GREETINGS = ["hi", "hello", "greetings", "hey", "hi,", "hello,", "hey,"]
GOODBYES = ["$goodbye", "$bye"]
QUESTION_WORDS = ["who", "where", "when", "what", "why", "how"]
BEFORE_NOUN = ["the", "that", "your", "my", "a", "an", "those", "my", "your", "their"]
PRONOUN = {"i":"you", "you":"i", "your":"my", "my":"your", "you're":"i'm", "i'm":"you're", "their":"their", "they":"they", "he":"he", "she":"she"}
PUNCT = [".", ",", "!", ";", "?", ":", "(", ")", "'", '"', "-", "*"]
END_PUNCT = [".", "!", "?"]


#Coding Constants
SENT_LEN = 20
SENT_TRIALS = 10

class AliceChatModule:
	__slots__ = ["__token", "__name", "__word_dict_lr", "__word_dict_rl"]
	def __init__(self, token, name):
		self.__token = token
		self.__name = name
		self.__word_dict_lr = {}
		self.__word_dict_rl = {}
		try:
                        self.read_lr("copsp.txt")
                        self.read_rl("copsp.txt")
	
	def get_token(self):
		return self.__token
	
	def remove_punct(self, word):
		#strips the punctuation off of the words
		 
		while True:
			if len(word) > 0 and word[-1] in PUNCT:
				word = word[:-1]
			else:
				break
		
		while True:
			if len(word) > 0 and word[0] in PUNCT:
				word = word[1:]
			else:
				break
		
		return word
	
	def add_to_vocab(self, user_input):
		file = open("copsp.txt", "a")
		file.write("\n" + user_input)
		sentence = user_input.lower().split()
		
		for i in range(len(sentence)):
			word = sentence[i].lower().strip()
				
			#Trys to get the next word. If it cant, it sets it assumes
			#its the end of a sentence
			try:
				next_word = sentence[i + 1].lower().strip()
			except:
				next_word = "."
					
			#makes the next word punctuation if it ends in punc
			#this is so the program later knows when to end the
			#sentence
			if word[-1] in END_PUNCT:
				next_word = word[-1]
				
			#delete extranious punctuation
			word = self.remove_punct(word)
			if len(next_word) != 1:
				next_word = self.remove_punct(next_word)

			if word not in self.__word_dict_lr:
				self.__word_dict_lr[word] = [next_word]
			else:
				self.__word_dict_lr[word] += [next_word]
				
		sent_end = 0
		for i in range(len(sentence)):
			word = sentence[i].lower().strip()
			try:
				next_word = sentence[i - 1].lower().strip()
			except:
				next_word = None
					
			#when it the sentence ends, it sets sent end to 1
			#so it can make the word that comes after the start
			#of the sentence
			if word[-1] in END_PUNCT:
				sent_end = 1
			
			word = self.remove_punct(word)
			if next_word != None:
				next_word = self.remove_punct(next_word)
					
			#the continuation of recognizing the start of the sentence
			if sent_end == 1:
				sent_end = 2
			elif sent_end == 2:
				next_word = None
				sent_end = 0
			
			if word not in self.__word_dict_rl:
				self.__word_dict_rl[word] = [next_word]
			else:
				self.__word_dict_rl[word] += [next_word]
	
	def find_key_words(self, user_input_list):
		#finds the key words in a users input
		noun = None
		pronoun = None
		for i in range(len(user_input_list)):
			if user_input_list[i] in BEFORE_NOUN:
				noun = self.remove_punct(user_input_list[i + 1])
			if user_input_list[i] in list(PRONOUN.keys()):
				pronoun = PRONOUN[user_input_list[i]]
		
		return pronoun, noun

	def read_lr(self, filename):
		#Reads a book and makes a dictionary
		#The key is a word, and the value is a list of words that come after the word
		#This one creates a sentence from left to right
		
		with open(filename) as file:
			for line in file:
				sentence = line.split()
				for i in range(len(sentence)):
					word = sentence[i].lower().strip()
					
					#Trys to get the next word. If it cant, it sets it assumes
					#its the end of a sentence
					try:
						next_word = sentence[i + 1].lower().strip()
					except:
						next_word = "."

					#makes the next word punctuation if it ends in punc
					#this is so the program later knows when to end the
					#sentence
					if word[-1] in END_PUNCT:
						next_word = word[-1]
					
					#delete extranious punctuation
					word = self.remove_punct(word)
					if len(next_word) != 1:
						next_word = self.remove_punct(next_word)

					if word not in self.__word_dict_lr:
						self.__word_dict_lr[word] = [next_word]
					else:
						self.__word_dict_lr[word] += [next_word]
	
	def read_rl(self, filename):
		#Reads a book and makes a dictionary
		#The key is a word, and the value is a list of words that come after the word
		#This one creates a sentence from left to right
		
		with open(filename) as file:
			sent_end = 0 #determines when the end of a sentence is
			for line in file:
				sentence = line.split()
				
				#Trys to get the next word. If it cant, it sets it assumes
				#its the beginning of a sentence
				for i in range(len(sentence)):
					word = sentence[i].lower().strip()
					try:
						next_word = sentence[i - 1].lower().strip()
					except:
						next_word = None
					
					#when it the sentence ends, it sets sent end to 1
					#so it can make the word that comes after the start
					#of the sentence
					if word[-1] in END_PUNCT:
						sent_end = 1
					
					word = self.remove_punct(word)
					if next_word != None:
						next_word = self.remove_punct(next_word)
					
					#the continuation of recognizing the start of the sentence
					if sent_end == 1:
						sent_end = 2
					elif sent_end == 2:
						next_word = None
						sent_end = 0
					
					if word not in self.__word_dict_rl:
						self.__word_dict_rl[word] = [next_word]
					else:
						self.__word_dict_rl[word] += [next_word]

	def sentence_type(self, user_input, user_input_list):
		#determines if the users input is a statement, exclamation, or question
		#if it cant decide, it assumes its a statement
		
		if user_input[-1] == ".":
			return "s"
		elif user_input[-1] == "!":
			return "e"
		elif user_input[-1] == "?" or user_input_list[0].lower() in QUESTION_WORDS:
			return "q"
		else:
			return "s"


	def make_response_lr(self, start_word):
		#Currently has no relation to what the user inputs
		#Check version 0 for a basic, canned response system
		#Makes a response by using the dictionaries to create a randomly
		#generated sentence.
		#curr_word = random.choice(list(self.__word_dict_lr.keys()))
		
		curr_word = start_word
		sentence = curr_word
		while True:
			curr_word = random.choice(self.__word_dict_lr[curr_word])
			
			#breaks when it finds punctuation
			if curr_word in END_PUNCT:
				sentence += curr_word
				break
			else:
				sentence += " " + curr_word
		return sentence
	
	def make_response_rl(self, start_word):
		#Makes a response by using the dictionaries to create a randomly
		#generated sentence. But backwards
		#curr_word = random.choice(list(self.__word_dict_rl.keys()))
		
		curr_word = start_word
		sentence = curr_word
		while True:
			curr_word = random.choice(self.__word_dict_rl[curr_word])
			if curr_word == None:
				break
			else:
				sentence = curr_word + " " + sentence
		return sentence
	
	def combine_response(self):
		#Combines the lr and rl responses with one common word.
		
		start_word = random.choice(list(self.__word_dict_lr.keys()))
		first = self.make_response_rl(start_word)
		last = self.make_response_lr(start_word)
		last = last[len(start_word):]
		return first + last
	
	def connect_words(self, start, end):
		#Trys to connect 2 words
		before_end = self.__word_dict_rl[end]
		
		for j in range(SENT_TRIALS):
			sentence = start
			
			if start in before_end:
				return sentence + " " + end
				
			curr_word = random.choice(self.__word_dict_lr[start])
			
			#Makes sure its not a punctuation
			x = 0
			while curr_word in PUNCT:
				if x < 100:
					curr_word = random.choice(self.__word_dict_lr[start])
					x += 1
				else:
					break
			#if it is, break and try again
			if curr_word in PUNCT:
				break
			
			#if not continue on
			else:
				sentence += " " + curr_word
				if curr_word in before_end:
					return sentence
			
				for i in range(SENT_LEN):
					next_word = random.choice(self.__word_dict_lr[curr_word])
					
					#Makes sure its not punctuation
					x = 0
					while next_word in PUNCT:
						if x < 100:
							next_word = random.choice(self.__word_dict_lr[curr_word])
							x += 1
						else:
							break
					
					#if it is, break
					if next_word in PUNCT:
						next_word = None
						break
						
					#if not continue
					else:
						curr_word = next_word
						sentence += " " + curr_word
						if curr_word in before_end:
							return sentence + " " + end
			
			sentence = start + " and " + end
		return sentence

	def respond(self, message):
		#A hub for responses!
		#Basically just has a standard hello response and calls the make_response
		
		user_input = message.content
		
		#Check if it starts with $
		if user_input[0] == "$":
			user_input = user_input[1:] #strip the $ off
			user_input_list = user_input.split()
			sent_type = self.sentence_type(user_input, user_input_list)
			if user_input_list[0].lower() in GREETINGS:
				return "Hello!"
			else:
				#start = random.choice(list(self.__word_dict_lr.keys()))
				#end = random.choice(list(self.__word_dict_lr.keys()))
				start, end = self.find_key_words(user_input_list)
				if start == None:
					start = random.choice(list(self.__word_dict_lr.keys()))
				if end == None:
					end = random.choice(list(self.__word_dict_lr.keys()))
				last = random.choice(list(self.__word_dict_lr.keys()))
				
				sentence = self.connect_words(start, end) + self.connect_words(end, last)[len(end):]
				
				return sentence
		else:
			return None

#Makeing it compatible with Discord stuff
client = discord.Client()
qalice = AliceChatModule(TOKEN, "QAlice")

@client.event
async def on_ready():
	print("QAlice is online. Currently running V.1.6")

@client.event
async def on_message(message):
	if message.content[0] == "$": 
		qalice.add_to_vocab(message.content.lower()[1:])
	else:
		qalice.add_to_vocab(message.content.lower())
		
	response = qalice.respond(message)
	
	#Log Alice off when I say goodbye
	if message.content.lower() in GOODBYES:
		await message.channel.send("See ya!")
		await client.logout()
		await client.close()
		print("QAlice has logged off successfully")
		sys.exit(0)
		
	#make a response if there is a message sent
	if response != None:
		await message.channel.send(response)

client.run(qalice.get_token())
