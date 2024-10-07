import sqlite3
from typing import Dict, List, Optional
import logging

class DataManager:
    def __init__(self, db_name: str = 'job_search.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                salary TEXT,
                url TEXT,
                date_posted TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                skills TEXT,
                experience TEXT,
                resume_text TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_interactions (
                id INTEGER PRIMARY KEY,
                job_id TEXT,
                user_id INTEGER,
                interaction_type TEXT,
                interaction_date TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs (job_id),
                FOREIGN KEY (user_id) REFERENCES user_profile (id)
            )
        ''')

        self.conn.commit()

    def add_job(self, job: Dict[str, str]) -> bool:
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO jobs 
                (job_id, title, company, location, description, salary, url, date_posted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job['job_id'], job['title'], job['company'], job['location'],
                job['description'], job['salary'], job['url'], job['date_posted']
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding job: {e}")
            return False

    def get_job(self, job_id: str) -> Optional[Dict[str, str]]:
        try:
            self.cursor.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
            job = self.cursor.fetchone()
            if job:
                return dict(zip([column[0] for column in self.cursor.description], job))
            return None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving job: {e}")
            return None

    def update_job(self, job_id: str, updates: Dict[str, str]) -> bool:
        try:
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE jobs SET {set_clause} WHERE job_id = ?"
            self.cursor.execute(query, list(updates.values()) + [job_id])
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error updating job: {e}")
            return False

    def delete_job(self, job_id: str) -> bool:
        try:
            self.cursor.execute('DELETE FROM jobs WHERE job_id = ?', (job_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error deleting job: {e}")
            return False

    def get_all_jobs(self) -> List[Dict[str, str]]:
        try:
            self.cursor.execute('SELECT * FROM jobs')
            jobs = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], job)) for job in jobs]
        except sqlite3.Error as e:
            logging.error(f"Error retrieving all jobs: {e}")
            return []

    def add_user_profile(self, profile: Dict[str, str]) -> bool:
        try:
            self.cursor.execute('''
                INSERT INTO user_profile (name, email, skills, experience, resume_text)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                profile['name'], profile['email'], profile['skills'],
                profile['experience'], profile['resume_text']
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding user profile: {e}")
            return False

    def get_user_profile(self, user_id: int) -> Optional[Dict[str, str]]:
        try:
            self.cursor.execute('SELECT * FROM user_profile WHERE id = ?', (user_id,))
            profile = self.cursor.fetchone()
            if profile:
                return dict(zip([column[0] for column in self.cursor.description], profile))
            return None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving user profile: {e}")
            return None

    def update_user_profile(self, user_id: int, updates: Dict[str, str]) -> bool:
        try:
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE user_profile SET {set_clause} WHERE id = ?"
            self.cursor.execute(query, list(updates.values()) + [user_id])
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error updating user profile: {e}")
            return False

    def add_job_interaction(self, interaction: Dict[str, str]) -> bool:
        try:
            self.cursor.execute('''
                INSERT INTO job_interactions (job_id, user_id, interaction_type, interaction_date)
                VALUES (?, ?, ?, ?)
            ''', (
                interaction['job_id'], interaction['user_id'],
                interaction['interaction_type'], interaction['interaction_date']
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding job interaction: {e}")
            return False

    def get_job_interactions(self, job_id: str, user_id: int) -> List[Dict[str, str]]:
        try:
            self.cursor.execute('''
                SELECT * FROM job_interactions 
                WHERE job_id = ? AND user_id = ?
            ''', (job_id, user_id))
            interactions = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], interaction)) for interaction in interactions]
        except sqlite3.Error as e:
            logging.error(f"Error retrieving job interactions: {e}")
            return []

    def search_jobs(self, keyword: str) -> List[Dict[str, str]]:
        try:
            query = '''
                SELECT * FROM jobs 
                WHERE title LIKE ? OR company LIKE ? OR description LIKE ?
            '''
            pattern = f"%{keyword}%"
            self.cursor.execute(query, (pattern, pattern, pattern))
            jobs = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], job)) for job in jobs]
        except sqlite3.Error as e:
            logging.error(f"Error searching jobs: {e}")
            return []

    def close(self):
        self.conn.close()
