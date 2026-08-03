import json
from pathlib import Path


class KnowledgeManager:

    def __init__(self):

        # Backend directory
        BASE_DIR = Path(__file__).resolve().parents[2]

        # D:\PAIOS\backend\knowledge
        self.knowledge_path = BASE_DIR / "knowledge"

        # Create the folder if it doesn't exist
        self.knowledge_path.mkdir(exist_ok=True)

        self.profile_file = self.knowledge_path / "profile.json"
        self.preferences_file = self.knowledge_path / "preferences.json"
        self.projects_file = self.knowledge_path / "projects.json"
        self.tasks_file = self.knowledge_path / "tasks.json"

    # -------------------------
    # Generic Helpers
    # -------------------------

    def load_json(self, file_path):

        if not file_path.exists():

            if file_path.name == "projects.json":
                data = {"projects": []}

            elif file_path.name == "tasks.json":
                data = {"tasks": []}

            else:
                data = {}

            self.save_json(file_path, data)
            return data

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_json(self, file_path, data):

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    # -------------------------
    # Profile
    # -------------------------

    def save_name(self, name):

        profile = self.load_json(self.profile_file)

        profile["name"] = name

        self.save_json(self.profile_file, profile)

    def get_name(self):

        profile = self.load_json(self.profile_file)

        return profile.get("name")

    # -------------------------
    # Projects
    # -------------------------

    def add_project(self, project):

        data = self.load_json(self.projects_file)

        projects = data.get("projects", [])

        if project not in projects:
            projects.append(project)

        data["projects"] = projects

        self.save_json(self.projects_file, data)

    def get_projects(self):

        data = self.load_json(self.projects_file)

        return data.get("projects", [])
        # -------------------------
    # Preferences
    # -------------------------

    def save_preference(self, key, value):

        data = self.load_json(self.preferences_file)

        data[key] = value

        self.save_json(self.preferences_file, data)

    def get_preference(self, key):

        data = self.load_json(self.preferences_file)

        return data.get(key)