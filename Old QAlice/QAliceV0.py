import random
import os
import discord

#Token
TOKEN = ""

#INput lists are global b/c im lazy
GREETINGS = ["hi", "hello", "greetings", "hey", "hi,", "hello,", "hey,"]
GOODBYES = ["goodbye", "bye"]
QUESTION_WORDS = ["who", "where", "when", "what", "why", "how"]
BEFORE_NOUN = ["the", "that", "your", "my", "a", "an", "those"]
PUNCT = [".", ",", "!", ";", "?", ":", "(", ")"]
END_PUNCT = [".", "!", "?"]

#random "tell me more" type of stuff
TELL_ME_MORE = ["Tell me more.", "That's so interesting.", "Crazy.", "Wowie Zowie, continue.", "Ahaha you're so sexy when you talk."]
HOW_ARE_YOU = ["I'm fine, thanks.", "Fine.", "I'm a robot, dumbass. No feelings.", "Insane, just like you."]

class Alice:
    __slots__ = ["__token", "__name", "__word_dict_lr", "__word_dict_rl"]
    def __init__(self, token, name):
        self.__token = token
        self.__name = name
        self.__word_dict_lr = {}
        self.__word_dict_rl = {}
        self.read()

    def get_token(self):
        return self.__token

    def get_name(self):
        return self.__name

    def read(self):
        with open("alice.txt") as aiw:
            sent_end = 0
            for line in aiw:
                sentence = line.split()
                for i in range(len(sentence)):
                    word = sentence[i].lower().strip()
                    try:
                        next_word_lr = sentence[i + 1].lower().strip()
                        next_word_rl = sentence[i - 1].lower().strip() 
                    except:
                        next_word_rl = None
                        next_word_lr = None
                        punc = None
                    
                    if word[-1] in END_PUNCT:
                        punc = word[-1]
                        word = word[:-1]
                        sent_end = 1
                    
                    if next_word_rl != None and next_word_rl[-1] in END_PUNCT:
                        next_word_rl = next_word_rl[:-1]
                    if next_word_lr == None:
                        if punc == None:
                            next_word = "."
                        else:
                            next_word = punc

                    if sent_end == 1:
                        sent_end = 2
                    elif sent_end == 2:
                        next_word = None
                        sent_end = 0
                    
                    if word not in self.__word_dict_rl:
                        self.__word_dict_rl[word] = [next_word_rl]
                    else:
                        self.__word_dict_rl[word] += [next_word_rl]

                    if word not in self.__word_dict_lr:
                        self.__word_dict_lr[word] = [next_word_lr]
                    else:
                        self.__word_dict_lr[word] += [next_word_lr]
                        

    def sentence_type(self, user_input, user_input_list):
        #determines if the users sentence is a statement, exclamation, or question
        if user_input[-1] == ".":
            return "s"
        elif user_input[-1] == "!":
            return "e"
        elif user_input[-1] == "?" or user_input_list[0].lower() in QUESTION_WORDS:
            return "q"
        else:
            return "s"

    def make_response(self, user_input_list, sent_type):
        #generates a response based on the subject
        #no adjtive support
        '''index = -1
        plural = 0
        for i in range(len(user_input_list)):
            if user_input_list[i] in BEFORE_NOUN:
                index = i + 1

        if index != -1:
            word = user_input_list[i]
            #delete punctuation
            if word[-1] in PUNCT:
                word = word[:-1]
            #for plural words
            if word[-1] == "s":
                plural = 1
            if sent_type == "q":
                return "I don't know much about " + word
            elif sent_type == "s":
                if plural == 1:
                    return word + " are pretty cool"
                else:
                    return "The " + word + " is real neat"
            else:
                if plural == 1:
                    return "Those " + word + " are amazing"
                else:
                    return "The " + word + " is really awesome"'''
        sentence = ""
        curr_word = random.choice(list(self.__word_dict_rl.keys()))
        first_word = str(curr_word)
        sentence += curr_word
        while True:
            next_word = random.choice(self.__word_dict_rl[curr_word])
            #if next_word in END_PUNCT:
            if next_word == None:
                #sentence += next_word
                break
            else:
                curr_word = next_word
                sentence = curr_word + " " + sentence

        sent_2 = first_word
        curr_word = first_word
        while True:
            next_word = random.choice(self.__word_dict_lr[curr_word])
            if next_word in END_PUNCT:
                sent_2 += next_word
                break
            else:
                curr_word = next_word
                print(curr_word)
                sent_2 += " " + curr_word
        return sentence + "\n" + sent_2

    def respond(self, message):
        #the magic, if you can call it that.
        #am i annoyed that this is the first step? yes. I get it though. baby steps
        #but jesus these are BABY steps, ya know?
        #it is nice to code something again

        user_input = message.content
        if user_input[0] == "$":
            user_input = user_input[1:] #strip the $ off it
            user_input_list = user_input.split()
            sent_type = self.sentence_type(user_input, user_input_list)
            if user_input_list[0].lower() in GREETINGS:
                return "Hello!"
            elif "who are you" in user_input.lower() or "who're you?" in user_input.lower():
                return "I am Alice."
            elif user_input_list[0].lower() in GOODBYES:
                return "See ya."
            elif user_input.lower() == "alice?":
                return "Yep, that's me."
            elif "how are you" in user_input.lower() or "how're you" in user_input.lower():
                return random.choice(HOW_ARE_YOU)
            else:
                return self.make_response(user_input_list, sent_type)
        else:
            return None

#Discord garbage
client = discord.Client()
qalice = Alice(TOKEN, "QAlice")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    response = qalice.respond(message)
    if response != None:
        await message.channel.send(response)

client.run(qalice.get_token())
