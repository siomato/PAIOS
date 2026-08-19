import json
from datetime import datetime, timezone
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

            self.save_json(
                file_path,
                data
            )

            return data

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def save_json(
        self,
        file_path,
        data
    ):

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    # -------------------------
    # Profile
    # -------------------------

    def save_name(
        self,
        name
    ):

        profile = self.load_json(
            self.profile_file
        )

        profile["name"] = name

        self.save_json(
            self.profile_file,
            profile
        )

    def get_name(self):

        profile = self.load_json(
            self.profile_file
        )

        return profile.get(
            "name"
        )

    # -------------------------
    # Projects
    # -------------------------

    def add_project(
        self,
        project
    ):

        data = self.load_json(
            self.projects_file
        )

        projects = data.get(
            "projects",
            []
        )

        if project not in projects:

            projects.append(
                project
            )

        data["projects"] = projects

        self.save_json(
            self.projects_file,
            data
        )

    def get_projects(self):

        data = self.load_json(
            self.projects_file
        )

        return data.get(
            "projects",
            []
        )

    # -------------------------
    # Preferences
    # -------------------------

    def save_preference(
        self,
        key,
        value
    ):

        data = self.load_json(
            self.preferences_file
        )

        data[key] = value

        self.save_json(
            self.preferences_file,
            data
        )

    def get_preference(
        self,
        key
    ):

        data = self.load_json(
            self.preferences_file
        )

        return data.get(
            key
        )

    # -------------------------
    # Task Memory
    # -------------------------

    def add_task(
        self,
        task,
        status="completed",
        steps=0,
        replans_used=0
    ):

        if not isinstance(
            task,
            str
        ):

            raise TypeError(
                "task must be a string."
            )

        task = task.strip()

        if not task:

            raise ValueError(
                "task cannot be empty."
            )

        data = self.load_json(
            self.tasks_file
        )

        tasks = data.get(
            "tasks",
            []
        )

        record = {

            "task": task,

            "status": status,

            "steps": int(
                steps
            ),

            "replans_used": int(
                replans_used
            ),

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat()
        }

        tasks.append(
            record
        )

        data["tasks"] = tasks

        self.save_json(
            self.tasks_file,
            data
        )

        return record

    def get_tasks(self):

        data = self.load_json(
            self.tasks_file
        )

        return data.get(
            "tasks",
            []
        )

    # -------------------------
    # Task Retrieval
    # -------------------------

    def find_tasks(
        self,
        query,
        limit=5
    ):

        """
        Retrieve previous tasks using deterministic
        token-overlap relevance scoring.

        The original substring behavior is preserved
        for exact phrases, while broader queries can
        now match individual meaningful words.

        Returns tasks ordered from most relevant to
        least relevant.
        """

        if not isinstance(
            query,
            str
        ):

            return []

        query = query.strip().lower()

        if not query:

            return []

        # ---------------------------------------------
        # Common words with little retrieval value
        # ---------------------------------------------

        stop_words = {

            "the",
            "and",
            "for",
            "with",
            "from",
            "this",
            "that",
            "what",
            "did",
            "was",
            "were",
            "have",
            "has",
            "had",
            "you",
            "our",
            "your",
            "about",
            "into",
            "using",
            "use",
            "can",
            "could",
            "would",
            "should",
            "tell",
            "me",
            "please",
            "previous",
            "earlier",
            "successfully"
        }

        # ---------------------------------------------
        # Tokenize query
        # ---------------------------------------------

        query_tokens = {

            token.strip(
                ".,!?;:()[]{}\"'"
            )

            for token in query.split()

            if len(
                token.strip(
                    ".,!?;:()[]{}\"'"
                )
            ) > 2
        }

        query_tokens -= stop_words

        if not query_tokens:

            return []

        scored_tasks = []

        # ---------------------------------------------
        # Evaluate every stored task
        # ---------------------------------------------

        for task in self.get_tasks():

            if not isinstance(
                task,
                dict
            ):

                continue

            task_text = str(
                task.get(
                    "task",
                    ""
                )
            ).strip().lower()

            if not task_text:

                continue

            # -----------------------------------------
            # Tokenize stored task
            # -----------------------------------------

            task_tokens = {

                token.strip(
                    ".,!?;:()[]{}\"'"
                )

                for token in task_text.split()

                if len(
                    token.strip(
                        ".,!?;:()[]{}\"'"
                    )
                ) > 2
            }

            task_tokens -= stop_words

            if not task_tokens:

                continue

            # -----------------------------------------
            # Calculate token overlap
            # -----------------------------------------

            matched_tokens = (
                query_tokens
                & task_tokens
            )

            if not matched_tokens:

                continue

            score = (
                len(matched_tokens)
                / len(query_tokens)
            )

            # -----------------------------------------
            # Exact phrase bonus
            # -----------------------------------------

            if query in task_text:

                score += 0.50

            # -----------------------------------------
            # Single-token query bonus
            # -----------------------------------------

            if len(
                query_tokens
            ) == 1:

                score += 0.25

            # -----------------------------------------
            # Store score internally
            # -----------------------------------------

            scored_tasks.append(
                (
                    score,
                    task
                )
            )

        # ---------------------------------------------
        # Highest relevance first
        # ---------------------------------------------

        scored_tasks.sort(
            key=lambda item: item[0],
            reverse=True
        )

        # ---------------------------------------------
        # Return only tasks
        # ---------------------------------------------

        return [

            task

            for _, task
            in scored_tasks[
                :max(
                    1,
                    int(limit)
                )
            ]

        ]


knowledge_manager = KnowledgeManager()