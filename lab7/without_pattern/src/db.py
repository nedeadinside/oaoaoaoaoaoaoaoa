import sqlite3
import hashlib


class DatabaseManager:
    def __init__(self, db_path='task_manager.db'):
        self.db_path = db_path
        self._create_tables_if_not_exists()
    

    def _create_tables_if_not_exists(self):
        """Создание таблиц, если они не существуют"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            email_notify INTEGER DEFAULT 0,
            telegram_id TEXT,
            telegram_notify INTEGER DEFAULT 0
        )
        ''')
        
        # Таблица задач
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            datetime TEXT NOT NULL,
            is_completed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    

    def _hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha384(password.encode()).hexdigest()


    def create_user(self, username, password, email=None, telegram_id=None):
        """Создание нового пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                password_hash = self._hash_password(password)
                cursor.execute(
                    "INSERT INTO users (username, password_hash, email, telegram_id) VALUES (?, ?, ?, ?)",
                    (username, password_hash, email, telegram_id)
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None
    
    
    def authenticate_user(self, username, password):
        """Проверка учетных данных пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
        
            password_hash = self._hash_password(password)
            cursor.execute(
                "SELECT id FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            
            user_id = cursor.fetchone()
        
        return user_id[0] if user_id else None
    
    
    def get_user_info(self, user_id):
        """Получение информации о пользователе"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT username, email, email_notify, telegram_id, telegram_notify FROM users WHERE id = ?",
                (user_id,)
            )
            
            user_info = cursor.fetchone()
            
        if user_info:
            return {
                'username': user_info[0],
                'email': user_info[1],
                'email_notify': bool(user_info[2]),
                'telegram_id': user_info[3],
                'telegram_notify': bool(user_info[4])
            }
        return None

    def user_exists(self, username):
        with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                result = cursor.execute("SELECT * FROM users WHERE `username` = ?", (username,)).fetchall()
        return bool(len(result))

    def _update_record(self, table_name, record_id, id_field, fields_dict):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                update_fields = []
                update_values = []
                
                for field, value in fields_dict.items():
                    if value is not None:
                        update_fields.append(f"{field} = ?")
                        if isinstance(value, bool):
                            update_values.append(int(value))
                        else:
                            update_values.append(value)
                
                if not update_fields:
                    return False
                
                query = f"UPDATE {table_name} SET {', '.join(update_fields)} WHERE {id_field} = ?"
                update_values.append(record_id)
                
                cursor.execute(query, update_values)
                conn.commit()
                
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении записи в {table_name}: {e}")
            return False
    
    
    def update_task(self, task_id, title=None, description=None, datetime=None, is_completed=None):
        """Обновление задачи"""
        fields_dict = {
            'title': title,
            'description': description,
            'datetime': datetime,
            'is_completed': is_completed
        }
        return self._update_record('tasks', task_id, 'id', fields_dict)


    def update_user_notification_settings(self, user_id, email=None, email_notify=None, 
                                        telegram_id=None, telegram_notify=None):
        """Обновление настроек уведомлений пользователя"""
        fields_dict = {
            'email': email,
            'email_notify': email_notify,
            'telegram_id': telegram_id,
            'telegram_notify': telegram_notify
        }
        return self._update_record('users', user_id, 'id', fields_dict)
    
    
    def create_task(self, user_id, title, description, datetime):
        """Создание новой задачи"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "INSERT INTO tasks (user_id, title, description, datetime) VALUES (?, ?, ?, ?)",
                (user_id, title, description, datetime)
            )
            
            task_id = cursor.lastrowid
            conn.commit()
        
        return task_id
    
    
    def get_user_tasks(self, user_id):
        """Получение всех задач пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, title, description, datetime, is_completed FROM tasks WHERE user_id = ? ORDER BY datetime",
            (user_id,)
        )
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'datetime': row[3],
                'is_completed': bool(row[4])
            })
        
        conn.close()
        return tasks
    
    
    def delete_task(self, task_id):
        """Удаление задачи"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()