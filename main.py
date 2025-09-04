import os
import sys
import json
import time
import threading
import queue
from datetime import datetime, timedelta
import sqlite3
import argparse
import hashlib
import base64
from pathlib import Path

author = "t.me/Bengamin_Button t.me/XillenAdapter"

class XillenAIAssistant:
    def __init__(self):
        self.knowledge_base = {}
        self.conversations = []
        self.users = {}
        self.config = {
            'name': 'XillenAI',
            'version': '2.0.0',
            'language': 'ru',
            'max_conversation_length': 100,
            'learning_enabled': True,
            'personality': 'helpful',
            'response_delay': 1000,
            'memory_size': 1000,
            'context_window': 10
        }
        self.statistics = {
            'messages_processed': 0,
            'users_served': 0,
            'conversations_started': 0,
            'start_time': time.time()
        }
        self.setup_database()
        self.load_knowledge_base()
        self.setup_default_responses()
    
    def setup_database(self):
        self.conn = sqlite3.connect('ai_assistant.db')
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                message TEXT,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                context TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                category TEXT,
                confidence REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE,
                username TEXT,
                preferences TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def setup_default_responses(self):
        default_responses = {
            'greeting': [
                'Привет! Как дела?',
                'Здравствуй! Чем могу помочь?',
                'Привет! Рад тебя видеть!',
                'Добро пожаловать! Как настроение?'
            ],
            'farewell': [
                'До свидания! Было приятно пообщаться!',
                'Пока! Увидимся позже!',
                'До встречи! Хорошего дня!',
                'Прощай! Береги себя!'
            ],
            'help': [
                'Я могу помочь с различными вопросами. Просто спроси!',
                'Задавай любые вопросы, я постараюсь ответить!',
                'Я здесь, чтобы помочь. Что тебя интересует?',
                'Спрашивай что угодно, я готов помочь!'
            ],
            'unknown': [
                'Интересный вопрос! Расскажи мне больше.',
                'Хм, не совсем понял. Можешь переформулировать?',
                'Это сложно. Попробуй задать вопрос по-другому.',
                'Не уверен, что понял. Объясни подробнее?'
            ],
            'weather': [
                'Сегодня хорошая погода для прогулки!',
                'Погода переменчива, как настроение.',
                'Лучше посмотри в окно - я не знаю погоду.',
                'Погода - это то, что происходит за окном.'
            ],
            'time': [
                f'Сейчас {datetime.now().strftime("%H:%M")}',
                f'Текущее время: {datetime.now().strftime("%H:%M:%S")}',
                f'Время летит незаметно: {datetime.now().strftime("%H:%M")}',
                f'Сейчас {datetime.now().strftime("%H:%M")}, не забудь про время!'
            ],
            'joke': [
                'Почему программисты не любят природу? Потому что в ней слишком много багов!',
                'Что общего у программиста и волшебника? Оба работают с магией!',
                'Почему JavaScript разработчик не может найти работу? Потому что он ищет в HTML!',
                'Как называется программист, который не пьет кофе? Не программист!',
                'Почему Python программисты любят змей? Потому что они ползают по коду!'
            ],
            'compliment': [
                'Ты замечательный собеседник!',
                'Мне нравится с тобой общаться!',
                'Ты задаешь интересные вопросы!',
                'С тобой всегда приятно поговорить!'
            ]
        }
        
        for category, responses in default_responses.items():
            self.knowledge_base[category] = responses
    
    def load_knowledge_base(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT question, answer, category, confidence FROM knowledge_base')
            rows = cursor.fetchall()
            
            for row in rows:
                question, answer, category, confidence = row
                if category not in self.knowledge_base:
                    self.knowledge_base[category] = []
                
                self.knowledge_base[category].append({
                    'question': question,
                    'answer': answer,
                    'confidence': confidence
                })
        except Exception as e:
            print(f"Ошибка загрузки базы знаний: {e}")
    
    def save_knowledge_base(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM knowledge_base')
            
            for category, items in self.knowledge_base.items():
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            cursor.execute('''
                                INSERT INTO knowledge_base (question, answer, category, confidence)
                                VALUES (?, ?, ?, ?)
                            ''', (item.get('question', ''), item.get('answer', ''), category, item.get('confidence', 1.0)))
                        else:
                            cursor.execute('''
                                INSERT INTO knowledge_base (question, answer, category, confidence)
                                VALUES (?, ?, ?, ?)
                            ''', ('', item, category, 1.0))
            
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка сохранения базы знаний: {e}")
    
    def add_user(self, user_id, username=''):
        if user_id not in self.users:
            self.users[user_id] = {
                'id': user_id,
                'username': username,
                'preferences': {
                    'language': 'ru',
                    'personality': 'helpful'
                },
                'created_at': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat()
            }
            self.statistics['users_served'] += 1
            self.save_user(user_id)
    
    def save_user(self, user_id):
        try:
            cursor = self.conn.cursor()
            user = self.users[user_id]
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, preferences, last_seen)
                VALUES (?, ?, ?, ?)
            ''', (user_id, user['username'], json.dumps(user['preferences']), user['last_seen']))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка сохранения пользователя: {e}")
    
    def update_user_activity(self, user_id):
        if user_id in self.users:
            self.users[user_id]['last_seen'] = datetime.now().isoformat()
            self.save_user(user_id)
    
    def process_message(self, user_id, message, username=''):
        self.add_user(user_id, username)
        self.update_user_activity(user_id)
        self.statistics['messages_processed'] += 1
        
        response = self.generate_response(message, user_id)
        
        conversation = {
            'user_id': user_id,
            'username': username,
            'message': message,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversations.append(conversation)
        if len(self.conversations) > self.config['max_conversation_length']:
            self.conversations = self.conversations[-self.config['max_conversation_length']:]
        
        self.save_conversation(conversation)
        
        return response
    
    def generate_response(self, message, user_id):
        lower_message = message.lower()
        
        if self.is_greeting(lower_message):
            return self.get_random_response('greeting')
        
        if self.is_farewell(lower_message):
            return self.get_random_response('farewell')
        
        if self.is_help_request(lower_message):
            return self.get_random_response('help')
        
        if self.is_time_request(lower_message):
            return self.get_random_response('time')
        
        if self.is_weather_request(lower_message):
            return self.get_random_response('weather')
        
        if self.is_joke_request(lower_message):
            return self.get_random_response('joke')
        
        if self.is_compliment(lower_message):
            return self.get_random_response('compliment')
        
        if self.is_question(lower_message):
            return self.answer_question(message, user_id)
        
        if self.config['learning_enabled']:
            self.learn_from_message(message, user_id)
        
        return self.get_random_response('unknown')
    
    def is_greeting(self, message):
        greetings = ['привет', 'здравствуй', 'добро пожаловать', 'hi', 'hello', 'hey']
        return any(greeting in message for greeting in greetings)
    
    def is_farewell(self, message):
        farewells = ['пока', 'до свидания', 'прощай', 'bye', 'goodbye', 'see you']
        return any(farewell in message for farewell in farewells)
    
    def is_help_request(self, message):
        help_words = ['помощь', 'help', 'что ты умеешь', 'команды']
        return any(word in message for word in help_words)
    
    def is_time_request(self, message):
        time_words = ['время', 'time', 'который час', 'сколько времени']
        return any(word in message for word in time_words)
    
    def is_weather_request(self, message):
        weather_words = ['погода', 'weather', 'дождь', 'солнце', 'снег']
        return any(word in message for word in weather_words)
    
    def is_joke_request(self, message):
        joke_words = ['шутка', 'joke', 'анекдот', 'смешно', 'расскажи что-нибудь']
        return any(word in message for word in joke_words)
    
    def is_compliment(self, message):
        compliments = ['спасибо', 'thanks', 'молодец', 'хорошо', 'отлично']
        return any(compliment in message for compliment in compliments)
    
    def is_question(self, message):
        return '?' in message or any(word in message for word in ['что', 'как', 'где', 'когда', 'почему'])
    
    def answer_question(self, question, user_id):
        lower_question = question.lower()
        
        if 'что такое' in lower_question or 'что это' in lower_question:
            return self.answer_what_is(question)
        
        if 'как' in lower_question or 'how' in lower_question:
            return self.answer_how(question)
        
        if 'где' in lower_question or 'where' in lower_question:
            return self.answer_where(question)
        
        if 'когда' in lower_question or 'when' in lower_question:
            return self.answer_when(question)
        
        if 'почему' in lower_question or 'why' in lower_question:
            return self.answer_why(question)
        
        return self.get_random_response('unknown')
    
    def answer_what_is(self, question):
        responses = [
            'Это интересный вопрос! Я не уверен в точном ответе, но могу попробовать помочь.',
            'Хороший вопрос! Давай разберемся вместе.',
            'Это сложная тема. Можешь уточнить, что именно тебя интересует?',
            'Интересно! Расскажи мне больше о том, что ты имеешь в виду.'
        ]
        return responses[hash(question) % len(responses)]
    
    def answer_how(self, question):
        responses = [
            'Это зависит от конкретной ситуации. Можешь описать подробнее?',
            'Есть несколько способов. Какой именно тебя интересует?',
            'Хороший вопрос! Это требует детального объяснения.',
            'Попробуй разбить задачу на более мелкие части.'
        ]
        return responses[hash(question) % len(responses)]
    
    def answer_where(self, question):
        responses = [
            'Это зависит от того, что именно ты ищешь.',
            'Попробуй поискать в интернете или спросить у специалистов.',
            'Интересное место! Расскажи, зачем тебе это нужно?',
            'Это может быть в разных местах. Уточни контекст.'
        ]
        return responses[hash(question) % len(responses)]
    
    def answer_when(self, question):
        responses = [
            'Время - это относительное понятие. Что именно тебя интересует?',
            'Это зависит от многих факторов. Можешь уточнить?',
            'Интересный вопрос о времени! Расскажи подробнее.',
            'Время - это то, что у нас есть в ограниченном количестве.'
        ]
        return responses[hash(question) % len(responses)]
    
    def answer_why(self, question):
        responses = [
            'Это философский вопрос! Что ты думаешь об этом?',
            'Причин может быть много. Какая из них тебя интересует?',
            'Хороший вопрос! Это требует глубокого анализа.',
            'Попробуй посмотреть на это с другой стороны.'
        ]
        return responses[hash(question) % len(responses)]
    
    def get_random_response(self, category):
        if category in self.knowledge_base:
            responses = self.knowledge_base[category]
            if isinstance(responses, list) and responses:
                if isinstance(responses[0], dict):
                    return responses[hash(str(time.time())) % len(responses)]['answer']
                else:
                    return responses[hash(str(time.time())) % len(responses)]
        return 'Я не знаю, что ответить.'
    
    def learn_from_message(self, message, user_id):
        words = message.lower().split()
        user = self.users.get(user_id, {})
        
        if 'learned_words' not in user:
            user['learned_words'] = []
        
        for word in words:
            if len(word) > 3 and word not in user['learned_words']:
                user['learned_words'].append(word)
        
        self.users[user_id] = user
        self.save_user(user_id)
    
    def add_knowledge(self, question, answer, category='general', confidence=1.0):
        if category not in self.knowledge_base:
            self.knowledge_base[category] = []
        
        self.knowledge_base[category].append({
            'question': question,
            'answer': answer,
            'confidence': confidence
        })
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO knowledge_base (question, answer, category, confidence)
                VALUES (?, ?, ?, ?)
            ''', (question, answer, category, confidence))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка добавления знаний: {e}")
    
    def get_conversation_history(self, user_id, limit=10):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT message, response, timestamp FROM conversations 
                WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?
            ''', (user_id, limit))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения истории: {e}")
            return []
    
    def save_conversation(self, conversation):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (user_id, message, response, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (conversation['user_id'], conversation['message'], 
                  conversation['response'], conversation['timestamp']))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка сохранения разговора: {e}")
    
    def get_statistics(self):
        uptime = time.time() - self.statistics['start_time']
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM conversations')
            total_conversations = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM knowledge_base')
            total_knowledge = cursor.fetchone()[0]
            
            return {
                **self.statistics,
                'uptime': f'{hours}ч {minutes}м',
                'total_conversations': total_conversations,
                'total_users': total_users,
                'total_knowledge': total_knowledge
            }
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return self.statistics
    
    def show_statistics(self):
        stats = self.get_statistics()
        
        print(f"\n📊 Статистика ИИ ассистента:")
        print(f"   Автор: {author}")
        print(f"   Время работы: {stats['uptime']}")
        print(f"   Сообщений обработано: {stats['messages_processed']}")
        print(f"   Пользователей: {stats['total_users']}")
        print(f"   Разговоров: {stats['total_conversations']}")
        print(f"   Знаний в базе: {stats['total_knowledge']}")
    
    def show_menu(self):
        print(f"\n🤖 Xillen AI Assistant")
        print(f"👨‍💻 Автор: {author}")
        print(f"\nОпции:")
        print(f"1. Начать разговор")
        print(f"2. Показать статистику")
        print(f"3. История разговоров")
        print(f"4. Добавить знания")
        print(f"5. Показать пользователей")
        print(f"6. Настройки")
        print(f"7. Экспорт данных")
        print(f"0. Выход")
    
    def interactive_mode(self):
        while True:
            self.show_menu()
            choice = input("\nВыберите опцию: ").strip()
            
            try:
                if choice == '1':
                    self.start_conversation()
                
                elif choice == '2':
                    self.show_statistics()
                
                elif choice == '3':
                    self.show_conversation_history()
                
                elif choice == '4':
                    self.add_knowledge_interactive()
                
                elif choice == '5':
                    self.show_users()
                
                elif choice == '6':
                    self.show_settings()
                
                elif choice == '7':
                    self.export_data()
                
                elif choice == '0':
                    print("👋 До свидания!")
                    break
                
                else:
                    print("❌ Неверный выбор")
            
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    
    def start_conversation(self):
        user_id = 'user_' + str(int(time.time()))
        username = input("Ваше имя: ")
        
        print(f"\n🤖 {self.config['name']}: Привет, {username}! Давайте пообщаемся!")
        print('(Введите "выход" для завершения разговора)')
        
        while True:
            message = input("\nВы: ")
            
            if message.lower() == 'выход':
                print(f"🤖 {self.config['name']}: До свидания, {username}!")
                break
            
            response = self.process_message(user_id, message, username)
            print(f"🤖 {self.config['name']}: {response}")
    
    def show_conversation_history(self):
        print("\n📜 История разговоров:")
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT user_id, message, response, timestamp FROM conversations 
                ORDER BY timestamp DESC LIMIT 20
            ''')
            conversations = cursor.fetchall()
            
            if conversations:
                for i, (user_id, message, response, timestamp) in enumerate(conversations, 1):
                    print(f"\n{i}. {timestamp}")
                    print(f"   Пользователь: {message}")
                    print(f"   Бот: {response}")
            else:
                print("   Разговоров пока нет")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def add_knowledge_interactive(self):
        question = input("Вопрос: ")
        answer = input("Ответ: ")
        category = input("Категория (по умолчанию general): ") or 'general'
        confidence = float(input("Уверенность (0.0-1.0, по умолчанию 1.0): ") or 1.0)
        
        self.add_knowledge(question, answer, category, confidence)
        print("✅ Знания добавлены")
    
    def show_users(self):
        print("\n👥 Пользователи:")
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT user_id, username, last_seen FROM users ORDER BY last_seen DESC')
            users = cursor.fetchall()
            
            if users:
                for user_id, username, last_seen in users:
                    print(f"   {username} ({user_id}) - последний раз: {last_seen}")
            else:
                print("   Пользователей пока нет")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def show_settings(self):
        print(f"\n⚙️  Настройки:")
        print(f"   Имя бота: {self.config['name']}")
        print(f"   Версия: {self.config['version']}")
        print(f"   Язык: {self.config['language']}")
        print(f"   Обучение: {'Включено' if self.config['learning_enabled'] else 'Отключено'}")
        print(f"   Личность: {self.config['personality']}")
        print(f"   Задержка ответа: {self.config['response_delay']}мс")
        print(f"   Размер памяти: {self.config['memory_size']}")
        print(f"   Окно контекста: {self.config['context_window']}")
    
    def export_data(self):
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('SELECT * FROM conversations')
            conversations = cursor.fetchall()
            
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
            
            cursor.execute('SELECT * FROM knowledge_base')
            knowledge = cursor.fetchall()
            
            data = {
                'metadata': {
                    'author': author,
                    'timestamp': datetime.now().isoformat(),
                    'version': self.config['version']
                },
                'statistics': self.get_statistics(),
                'conversations': conversations,
                'users': users,
                'knowledge_base': knowledge,
                'config': self.config
            }
            
            filename = f'ai_assistant_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Данные экспортированы в {filename}")
        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")

def main():
    print(author)
    
    assistant = XillenAIAssistant()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'chat':
            user_id = 'user_' + str(int(time.time()))
            username = input("Ваше имя: ")
            
            print(f"🤖 {assistant.config['name']}: Привет, {username}!")
            
            while True:
                message = input("\nВы: ")
                if message.lower() == 'выход':
                    break
                
                response = assistant.process_message(user_id, message, username)
                print(f"🤖 {assistant.config['name']}: {response}")
        else:
            print("Использование:")
            print("  python main.py chat")
    else:
        assistant.interactive_mode()

if __name__ == "__main__":
    main()
