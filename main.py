#! /usr/bin/python3.6
from flask import Flask, request
from config import Configuration
from classes.keyboard import Keyboard
from bot import Bot

import random
import arguments
import requests
import keys
import json
import re
import os



app = Flask(__name__)
app.config.from_object(Configuration)

bot = Bot(keys.TOKEN)

groups_spec_kbrd = Keyboard(arguments.specializace)
groups_spec_kbrd.create_table()
week_day_kbrd = Keyboard(arguments.DAYS)
week_day_kbrd.create_table()


def reader(day, user_group):

	filename = 'groups/days_{}/{}'.format(user_group,day)
	with open(filename, 'r') as file:
		table = file.read()
		return table

def removing_tmp_file(path):
	import os
	if os.path.exists(path):
		os.remove(path)


def parsing(message, user_id):
	user_id = str(user_id)
	message = message.upper()
	if message.lower() == 'перевыбрать группу':
		removing_tmp_file('tmp/'+user_id)
		return {"keyboard": groups_spec_kbrd.get_body(), "message": "Первые 2 бувы своей специальности:"}



	elif message in arguments.specializace:
		groups_num_kbrd = Keyboard(arguments.gnums[message])
		groups_num_kbrd.create_table()
		return{"keyboard": groups_num_kbrd.get_body(), "message": "Полное название вашей группы:"}


	elif message in arguments.group_full:
			if not os.path.exists('tmp/'):
				os.mkdir('tmp/')
			with open('tmp/' + user_id, 'w') as file:
				file.write(message)
			return{"keyboard": week_day_kbrd.get_body(), "message": "День недели:"}

	elif message.lower() in arguments.DAYS:
		try:
			with open('tmp/' + user_id, 'r') as file:
				user_group = file.read()
			return{"keyboard":week_day_kbrd.get_body(), "message": reader(message.lower(), user_group)}
		except:
			return {"keyboard": 
week_day_kbrd.get_body(), "message":"Видимо вы ввели неправильно день недели, используйте сокращенные названия дней недели (пн, вт, ср и т.д.), либо расписание вашей группы еще не добавлено"}

	else:
		# убрано удаление, т.к. сервер может отправить 2 сообщения, и при этом удаляет временный файл, когда это не нужно
		# removing_tmp_file('tmp/'+user_id)
		return {"keyboard": 
groups_spec_kbrd.get_body(), "message": "хостинг забыл вашу группу, пожалуйста, впишите ее заного"}



@app.route('/bot', methods = ['POST', 'GET'])
def main():
	if request.method == 'POST':
		r = request.get_json()
		print(r)
		if not r:
			return 'ne ok'
		elif r['type'] == 'confirmation':
			return keys.CONFIRMATION_KEY

		elif r['type'] == 'message_new':
			params = {
				'user_id': r['object']['peer_id'],
				'message' : r['object']['text']
			}
			pars = parsing(params['message'], params['user_id'])
			print(params['message'])
			print(pars['keyboard'])
			bot.send_message(params['user_id'], pars["message"], kbrt = pars["keyboard"], random_id = random.randint(100000000, 999999999))
			return 'ok'
	else:
		return 'ne ok'


@app.route('/')
def index():
	return '<h1>hello</h1>'






if __name__ == '__main__':
	app.run()
