import spacy
from typing import List, Dict, Tuple
from data_management_module import DataManager
import logging
from collections import Counter

class AIJobMatcher:
    def __init__(self, db_name: str = 'job_search.db'):
        self.nlp = spacy.load("en_core_web_sm")
        self.data_manager = DataManager(db_name)
        self.logger = logging.getLogger(__name__)

    def preprocess_text(self, text: str) -> List[str]:
        doc = self.nlp(text.lower())
        return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.is_alpha]

    def extract_skills(self, text: str) -> List[str]:
        doc = self.nlp(text)
        skills = [ent.text.lower() for ent in doc.ents if ent.label_ == "SKILL"]
        skills.extend([chunk.text.lower() for chunk in doc.noun_chunks if chunk.root.pos_ == "NOUN"])
        return list(set(skills))

    def calculate_similarity(self, profile_skills: List[str], job_skills: List[str]) -> float:
        profile_set = set(profile_skills)
        job_set = set(job_skills)
        intersection = profile_set.intersection(job_set)
        return len(intersection) / (len(profile_set) + len(job_set) - len(intersection))

    def rank_jobs_for_user(self, user_id: int, top_n: int = 10) -> List[Tuple[Dict, float]]:
        user_profile = self.data_manager.get_user_profile(user_id)
        if not user_profile:
            self.logger.error(f"User profile not found for user_id: {user_id}")
            return []

        user_skills = self.extract_skills(user_profile['skills'] + " " + user_profile['experience'] + " " + user_profile['resume_text'])
        
        all_jobs = self.data_manager.get_all_jobs()
        job_rankings = []

        for job in all_jobs:
            job_skills = self.extract_skills(job['title'] + " " + job['description'])
            similarity_score = self.calculate_similarity(user_skills, job_skills)
            job_rankings.append((job, similarity_score))

        return sorted(job_rankings, key=lambda x: x[1], reverse=True)[:top_n]

    def get_skill_recommendations(self, user_id: int, top_n: int = 5) -> List[str]:
        user_profile = self.data_manager.get_user_profile(user_id)
        if not user_profile:
            self.logger.error(f"User profile not found for user_id: {user_id}")

        user_skills = set(self.extract_skills(user_profile['skills'] + " " + user_profile['experience'] + " " + user_profile['resume_text']))
        
        all_jobs = self.data_manager.get_all_jobs()
        job_skills = []

        for job in all_jobs:
            job_skills.extend(self.extract_skills(job['title'] + " " + job['description']))

        skill_counter = Counter(job_skills)
        recommended_skills = [skill for skill, _ in skill_counter.most_common() if skill not in user_skills]
        return recommended_skills[:top_n]

    def update_user_profile_skills(self, user_id: int) -> bool:
        user_profile = self.data_manager.get_user_profile(user_id)
        if not user_profile:
            self.logger.error(f"User profile not found for user_id: {user_id}")
            return False

        extracted_skills = self.extract_skills(user_profile['skills'] + " " + user_profile['experience'] + " " + user_profile['resume_text'])
        updated_skills = ", ".join(extracted_skills)

        return self.data_manager.update_user_profile(user_id, {'skills': updated_skills})

    def close(self):
        self.data_manager.close()

