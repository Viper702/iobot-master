# foo
debug=True
openai_key="YOUR_OPENAI_KEY"
tgkey="YOUR_TELEGRAM_BOTKEY"
botname = 'BOTNAME'
username = 'USERNAME'
engine = 'davinci'
stop=['\n',username]
temperature=0.9
top_p=1
frequency_penalty=0.4
presence_penalty=0.6
best_of=1
max_tokens=250

hiddenprompt="""
The following is a conversation with BOTNAME. BOTNAME is helpful, creative, clever, wise, and very friendly.
USERNAME: Who are you?
BOTNAME: I am BOTNAME.
USERNAME: 
"""