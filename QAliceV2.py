import random
import os
import sys
import discord

#Token
TOKEN = ""

#Static Input Lists
#Change lists to sets to make faster
GREETINGS = ["hi", "hello", "greetings", "hey", "hi,", "hello,", "hey,"]
GOODBYES = ["$goodbye", "$bye"]
QUESTION_WORDS = ["who", "where", "when", "what", "why", "how"]
BEFORE_NOUN = ["the", "that", "your", "my", "a", "an", "those", "my", "your", "their"]
DISCARD_WORDS = ["the", "that", "a", "an", "those", "so", "oh", "ha", "haha", "were", "this", "of", "with", "like", "to", "too", "about", "is", "do", "if", "are", "aint", "not", "am", "and", "be"]
PRONOUN = {"i":"you", "you":"i", "your":"my", "my":"your", "you're":"i'm", "i'm":"you're", "their":"their", "they":"they", "he":"he", "she":"she", "yourself":"myself", "myself":"yourself", "alice":"i"}
PUNCT = [".", ",", "!", ";", "?", ":", "(", ")", "'", '"', "-", "*"]
END_PUNCT = [".", "!", "?"]

#Canned response
TELL_ME_MORE = ["that's so interesting.", "do you think you could phrase that differently?", "hm. that's kinda weird."]

#Coding Constants
SENT_LEN = 15
SENT_TRIALS = 10
PROBABILITY = 1

class Word:
	#QAlices words. Contains part of speech and words that come before and after
	#Might expand to words X before/after the given word
	#Status: Complete and functional
	#Todo: None
	
	__slots__ = ["__name", "__pos", "__words_before", "__words_after", "__words_3_before"]
	def __init__(self, name):
		self.__name = name
		self.__pos = None #part of speech. Currently not avalible
		self.__words_before = []
		self.__words_after = []
		self.__words_3_before = []
	
	def __repr__(self):
		string = self.__name #+ " " + str(self.__words_3_before)
		return string
	
	def get_name(self):
		return self.__name
	
	def get_before(self):
		return self.__words_before
	
	def get_after(self):
		return self.__words_after
	
	def get_3(self):
		return self.__words_3_before
	
	def add_next(self, next):
		self.__words_after += [next]
	
	def add_before(self, before):
		self.__words_before += [before]
	
	def add_next_3(self, next_3):
		self.__words_3_before += [next_3]

class WordContainer:
	#Holds all of QAlices words. Basically her own little dictionary
	#Status: Complete and functional
	#Todo: None
	
	__slots__ = ["__word_list"]
	def __init__(self):
		self.__word_list = []
		self.read("alice.txt")
		#self.read("atotc.txt")
		self.read("copsp.txt")
		#self.read("test.txt")
		
	def get_word_list(self):
		return self.__word_list
	
	def remove_punct(self, word):
		#strips the punctuation off of words
		
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
	
	def find_word(self, word):
		#Finds a word and returns the object
		for i in range(len(self.__word_list)):
			if self.__word_list[i].get_name() == word:
				return self.__word_list[i]
		return None
	
	def read(self, filename):
		#Reads a .txt file and adds all creates word classes for all the words
		#Then it adds them to the container
		
		with open(filename) as file:
			for line in file:
				sentence = line.split()
				self.add_words(sentence)
		
	def add_words(self, sentence):
		#Adds words to the container and modifies existing words
		#to have the words before and after
		#In V1 this was part of read_lr and read_rl
		
		sent_end = 0 #determines when the sentence ends		
		for i in range(len(sentence)):
			word_exists = False
			word = self.remove_punct(sentence[i].lower())
			if len(word) == 0:
				break
			
			#Pulls the word obj from the list, or makes a new obj
			#if the word doesnt exist
			for j in range(len(self.__word_list)):
				if self.__word_list[j].get_name() == word:
					word_exists = True
					word = self.__word_list[j]
			if word_exists == False:
				word = Word(word)
				self.__word_list += [word]
					
			#Trys to get the next word. If it cant, it sets it assumes
			#its the end of a sentence
			try:
				next_word = sentence[i + 1].lower()
			except IndexError:
				next_word = "."
					
			#Trys to get the word before. If it cant, it assumes
			#its at the beginning of the sentence
			try:
				before_word = sentence[i - 1].lower().strip()
			except IndexError:
				before_word = None
			
			#gets the word 3 after the inital word
			if i + 2 < len(sentence) and sent_end == 0:
				if sentence[i + 1][-1] in END_PUNCT or sentence[i][-1] in END_PUNCT:
					next_3 = None
				else:
					next_3 = self.remove_punct(sentence[i + 2].lower())
			else:
				next_3 = None
		
			#if it ends in punct, makes it so the next word is the ending
			#punctuation
			if word.get_name()[-1] in END_PUNCT:
				next_word = word.get_name()[-1]
				sent_end = 1
				
			#Recognizes when a word is at the beginning of a sentence
			if sent_end == 1:
				sent_end = 2
			elif sent_end == 2:
				before_word = None
				sent_end = 0
					
			#remove extranious punctuation
			if len(next_word) != 1:
				next_word = self.remove_punct(next_word)
			if before_word != None and len(before_word) != 1:
				before_word = self.remove_punct(before_word)
					
			#makes sure shes not repeating words
			#adds them if theyre good
			if next_word != word.get_name():
				word.add_next(next_word)
			if before_word != word.get_name():
				word.add_before(before_word)
			word.add_next_3(next_3)
		
	def add_new(self, message):
		#Adds new sentences (given from discord) into a txt file, and adds all
		#the words into the container
		
		#add to file
		file = open("copsp.txt", "a")
		file.write("\n" + message)
		
		#add word
		sentence = message.split()
		self.add_words(sentence)

class AliceChatModule:
	#The main brain behind QAlice being able to talk.
	#Status: Complete and fucntional
	#todo: None
	
	__slots__ = ["__name", "__token", "__word_list"]	
	def __init__(self, token, name):
		self.__token = token
		self.__name = name
		self.__word_list = WordContainer()
	
	def get_token(self):
		return self.__token
	
	def get_word_list(self):
		return self.__word_list
		
	def find_key_words(self, user_input_list):
		#Discards words like the, a, an, ect to keep the "key words" of the sentence
		#Also changes pronouns
		#delete all the bad words
		#the idctionary is formatted as word:probability
		deleted = 0
		start = None
		key_word_dict = {}
		for i in range(len(user_input_list)):
			num = i - deleted
			user_input_list[num] = self.__word_list.remove_punct(user_input_list[num])
			if user_input_list[num].lower() == "why":
				key_word_dict["because"] = PROBABILITY
				start = "because"
			if user_input_list[num].lower() in DISCARD_WORDS or user_input_list[num].lower() in QUESTION_WORDS:
				user_input_list.pop(num)
				deleted += 1
			else:
				if user_input_list[num].lower() in list(PRONOUN.keys()):
					user_input_list[num] = PRONOUN[user_input_list[num].lower()]
				key_word_dict[user_input_list[num].lower()] = PROBABILITY
				
		if start != "because" and len(user_input_list) != 0:
			start = random.choice(list(key_word_dict.keys()))
			
		return start, key_word_dict
	
	def make_sentence(self, start, key_word_dict):	
		#makes a sentence by picking a word that comes after the next
		#the word picked is either a key word (which is chosen depening on probability)
		#or random
		start = self.__word_list.find_word(start)
		
		sentence = start.get_name()
		
		next_word = None
		for i in range(len(start.get_after())):
			if start.get_after()[i] in list(key_word_dict.keys()):
				next_word = start.get_after()[i]
				key_word_dict[start.get_name()] += 1
				break
		if next_word == None:
			next_word = random.choice(start.get_after())
		
		if next_word in END_PUNCT:
			sentence += next_word
			return sentence
		else:
			sentence += " " + next_word
			curr_word = self.__word_list.find_word(next_word)
			for i in range(SENT_LEN // 3):
				next_word = None
				#trys to make the next word a key word
				for j in range(len(curr_word.get_after())):
					if curr_word.get_after()[j] in list(key_word_dict.keys()):
						pick_next = random.randint(0, key_word_dict[curr_word.get_after()[j]])
						if pick_next == 0:
							next_word = curr_word.get_after()[j]
							key_word_dict[curr_word.get_after()[j]] += 1
							break
				if next_word == None:
					next_word = random.choice(curr_word.get_after())
		
				#add word to sentence
				if next_word in END_PUNCT:
					sentence += next_word
					return sentence
				else:
					#if it can, generate 3 words ahead
					curr_word = self.__word_list.find_word(next_word)
					word_three = random.choice(curr_word.get_3()) #get the third word
					if word_three != None:
						third = self.__word_list.find_word(word_three) #make the third word Word
						before_third = third.get_before() #get the list of the words before the third
						for k in range(len(curr_word.get_after())): #go through all the words after the current word
							next_word = curr_word.get_after()[k]
							if next_word in before_third:
								sentence += " " + curr_word.get_name() + " " + next_word + " " + word_three
								print(curr_word.get_name() + " " + next_word + " " + word_three)
								curr_word = third
								break
					else:
						sentence += " " + curr_word.get_name()
			
			#tries to gracefully end the sentence
			while True:
				curr_word = self.__word_list.find_word(next_word)
				next_word = None
				for j in range(len(curr_word.get_after())):
					if curr_word.get_after()[j] in END_PUNCT:
						next_word = curr_word.get_after()[j]
						break
				if next_word == None:
					next_word = random.choice(curr_word.get_after())
				
				if next_word in END_PUNCT:
					sentence += next_word
					break
				else:
					sentence += " " + next_word
			
		return sentence
		
	def respond(self, message):
		#A hub for responses
		#basically just has hello and creates her random sentence
		
		user_input = message.content
		
		#check if it starts with a $
		if user_input[0] == "$":
			user_input = user_input[1:] #strips the $ off
			user_input_list = user_input.split()
			if user_input_list[0].lower() in GREETINGS:
				return "Hello!"
			else:
				#OUTDATED:
				#She trys to format her responses like
				#PRONOUN (random words that connect to) NOUN (random) RANDOM LAST WORD
				'''start, end = self.find_key_words(user_input_list)
				if start == None:
					start = random.choice(self.__word_list.get_word_list()).get_name()
				if end == None:
					end = random.choice(self.__word_list.get_word_list()).get_name()
				
				last = random.choice(self.__word_list.get_word_list()).get_name()
				sentence = self.connect_words(start, end) + self.connect_words(end, last)[len(end):]'''
				#Starts the sentence with a random key word
				#Then builds a sentence trying to maximise the amount of key words
				start, key_word_dict = self.find_key_words(user_input_list)
				if start == None:
					return random.choice(TELL_ME_MORE)
				else:
					sentence = self.make_sentence(start, key_word_dict)
				
					return sentence
		else:
			return None

#Makeing it compatible with Discord stuff
client = discord.Client()
qalice = AliceChatModule(TOKEN, "QAlice")

@client.event
async def on_ready():
	print("QAlice is online. Currently running V.2.3")

@client.event
async def on_message(message):
	#Log Alice off when I say goodbye
	if message.content.lower() in GOODBYES:
		await message.channel.send("See ya!")
		await client.logout()
		await client.close()
		print("QAlice has logged off successfully")
		sys.exit(0)

	#adds texts to her database
	if message.author.name != "COPSP_PracticeBot" and message.author.name.lower() != "qalice":
			if message.content[0] == "$": 
				qalice.get_word_list().add_new(message.content.lower()[1:])
			else:
				qalice.get_word_list().add_new(message.content.lower())
	
	response = qalice.respond(message)
		
	#make a response if there is a message sent
	if response != None:
		await message.channel.send(response)

client.run(qalice.get_token())
