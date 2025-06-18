import sqlite3
import os
from langchain_community.utilities import SQLDatabase


class SQLiteDB:
    def __init__(self, db_name: str):
        self.db_name = f"db/{db_name}"  
        os.makedirs(os.path.dirname(self.db_name), exist_ok=True)

        db_exists = os.path.exists(self.db_name)

        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)

        if not db_exists:
            self._create_tables()

        self.sqlDatabase = SQLDatabase.from_uri(f"sqlite:///{self.db_name}")

    def _create_tables(self):
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL UNIQUE
        );
        """

        create_food_categories_table = """
        CREATE TABLE IF NOT EXISTS food_categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE,
            nutrition_value TEXT,
            recommended_frequency TEXT
        );
        """

        create_meals_table = """
        CREATE TABLE IF NOT EXISTS meals (
            meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            meal_date DATE DEFAULT CURRENT_DATE,
            meal_type TEXT CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')) NOT NULL,
            food_name TEXT NOT NULL,
            category_id INTEGER,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES food_categories (category_id) ON DELETE SET NULL
        );
        """

        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(create_users_table)
            cursor.execute(create_food_categories_table)
            cursor.execute(create_meals_table)
            
            default_categories = [
                ('蔬菜类', '富含维生素、矿物质和膳食纤维，低热量', '每天至少摄入300-500克'),
                ('水果类', '富含维生素C、抗氧化物和膳食纤维', '每天1-2份'),
                ('谷物类', '提供碳水化合物和B族维生素，是能量的主要来源', '每天作为主食'),
                ('肉蛋类', '富含优质蛋白质和铁', '每周3-5次，每次适量'),
                ('奶制品', '富含钙质和蛋白质', '每天1-2份'),
                ('豆制品', '提供植物蛋白和异黄酮', '每周3-4次'),
                ('坚果类', '含有健康脂肪和多种矿物质', '每天一小把（约25克）'),
                ('海鲜类', '富含优质蛋白质和ω-3脂肪酸', '每周2-3次')
            ]
            
            cursor.executemany(
                "INSERT OR IGNORE INTO food_categories (category_name, nutrition_value, recommended_frequency) VALUES (?, ?, ?)",
                default_categories
            )
            
            conn.commit()
        print("数据库和表已创建，默认食物类别已添加。")
        

    def register_user(self, username):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO users (user_name) VALUES (?)", (username,))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
            
    def login_user(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_name = ?", (username,))
        result = cursor.fetchone()
        return result[0] if result else None
        
    def get_user_by_name(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id, user_name FROM users WHERE user_name = ?", (username,))
        result = cursor.fetchone()
        if result:
            return {"user_id": result[0], "user_name": result[1]}
        return None

    def add_food_category(self, category_name, nutrition_value=None, recommended_frequency=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO food_categories (category_name, nutrition_value, recommended_frequency) VALUES (?, ?, ?)",
                (category_name, nutrition_value, recommended_frequency)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
            
    def get_all_food_categories(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT category_id, category_name, nutrition_value, recommended_frequency FROM food_categories")
        results = cursor.fetchall()
        categories = []
        for row in results:
            categories.append({
                "category_id": row[0],
                "category_name": row[1],
                "nutrition_value": row[2],
                "recommended_frequency": row[3]
            })
        return categories
        
    def add_meal(self, user_id, meal_type, food_name, category_id=None, description=None, meal_date=None):
        cursor = self.conn.cursor()
        if meal_date:
            cursor.execute(
                "INSERT INTO meals (user_id, meal_type, food_name, category_id, description, meal_date) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, meal_type, food_name, category_id, description, meal_date)
            )
        else:
            cursor.execute(
                "INSERT INTO meals (user_id, meal_type, food_name, category_id, description) VALUES (?, ?, ?, ?, ?)",
                (user_id, meal_type, food_name, category_id, description)
            )
        self.conn.commit()
        return cursor.lastrowid
        
    def get_user_meals(self, user_id, start_date=None, end_date=None):
        cursor = self.conn.cursor()
        query = """
        SELECT m.meal_id, m.meal_date, m.meal_type, m.food_name, m.description, 
               c.category_id, c.category_name, c.nutrition_value, c.recommended_frequency
        FROM meals m
        LEFT JOIN food_categories c ON m.category_id = c.category_id
        WHERE m.user_id = ?
        """
        params = [user_id]
        
        if start_date:
            query += " AND m.meal_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND m.meal_date <= ?"
            params.append(end_date)
            
        query += " ORDER BY m.meal_date DESC, m.meal_type"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        meals = []
        for row in results:
            meals.append({
                "meal_id": row[0],
                "meal_date": row[1],
                "meal_type": row[2],
                "food_name": row[3],
                "description": row[4],
                "category_id": row[5],
                "category_name": row[6],
                "nutrition_value": row[7],
                "recommended_frequency": row[8]
            })
        return meals

    def get_sqlDatabase(self):
        return self.sqlDatabase
        
    def close(self):
        self.conn.close()
        print("数据库连接已关闭。")

if __name__ == "__main__":
    db = SQLiteDB("healthMealAssistant.db")
    db.close()