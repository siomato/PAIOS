import json
from datetime import datetime, timezone
from pathlib import Path


class KnowledgeManager:

    def __init__(self):

        # Backend directory
        BASE_DIR = Path(__file__).resolve().parents[2]

        # D:\PAIOS\backend\knowledge
        self.knowledge_path = BASE_DIR / "knowledge"

        self.knowledge_path.mkdir(
            exist_ok=True
        )

        self.profile_file = (
            self.knowledge_path / "profile.json"
        )

        self.preferences_file = (
            self.knowledge_path / "preferences.json"
        )

        self.projects_file = (
            self.knowledge_path / "projects.json"
        )

        self.tasks_file = (
            self.knowledge_path / "tasks.json"
        )

    # =================================================
    # GENERIC HELPERS
    # =================================================

    def load_json(
        self,
        file_path
    ):

        if not file_path.exists():

            if file_path.name == "projects.json":

                data = {
                    "projects": []
                }

            elif file_path.name == "tasks.json":

                data = {
                    "tasks": []
                }

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

    # =================================================
    # PROFILE
    # =================================================

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

    # =================================================
    # PROJECTS
    # =================================================

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

    # =================================================
    # PREFERENCES
    # =================================================

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

    # =================================================
    # TASK NORMALIZATION
    # =================================================

    def _normalize_task(
        self,
        task
    ):

        if not isinstance(
            task,
            str
        ):

            return set()

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
            "open",
            "find",
            "search",
            "web",
            "page",
            "pages",
            "result",
            "results"
        }

        tokens = set()

        for token in task.lower().split():

            token = token.strip(
                ".,!?;:()[]{}\"'"
            )

            if len(token) <= 2:
                continue

            if token in stop_words:
                continue

            tokens.add(
                token
            )

        return tokens

    # =================================================
    # DUPLICATE DETECTION
    # =================================================

    def _find_duplicate_task(
        self,
        task,
        tasks
    ):

        new_tokens = (
            self._normalize_task(
                task
            )
        )

        if not new_tokens:

            return None

        best_match = None
        best_score = 0.0

        for existing in tasks:

            if not isinstance(
                existing,
                dict
            ):

                continue

            existing_task = existing.get(
                "task",
                ""
            )

            existing_tokens = (
                self._normalize_task(
                    existing_task
                )
            )

            if not existing_tokens:

                continue

            intersection = (
                new_tokens
                & existing_tokens
            )

            if not intersection:

                continue

            # Jaccard similarity
            union = (
                new_tokens
                | existing_tokens
            )

            score = (
                len(intersection)
                / len(union)
            )

            if score > best_score:

                best_score = score
                best_match = existing

        # Conservative threshold.
        #
        # This prevents loosely related tasks
        # from being merged.
        if best_score >= 0.60:

            return best_match

        return None

    # =================================================
    # TASK MEMORY
    # =================================================

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

        now = datetime.now(
            timezone.utc
        ).isoformat()

        # ---------------------------------------------
        # Check for near-duplicate
        # ---------------------------------------------

        duplicate = (
            self._find_duplicate_task(
                task,
                tasks
            )
        )

        if duplicate is not None:

            duplicate["task"] = task

            duplicate["status"] = status

            duplicate["steps"] = int(
                steps
            )

            duplicate["replans_used"] = int(
                replans_used
            )

            duplicate["timestamp"] = now

            duplicate["occurrences"] = (
                int(
                    duplicate.get(
                        "occurrences",
                        1
                    )
                )
                + 1
            )

            data["tasks"] = tasks

            self.save_json(
                self.tasks_file,
                data
            )

            return duplicate

        # ---------------------------------------------
        # New task
        # ---------------------------------------------

        record = {

            "task": task,

            "status": status,

            "steps": int(
                steps
            ),

            "replans_used": int(
                replans_used
            ),

            "timestamp": now,

            "occurrences": 1
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

    # =================================================
    # TASK LIFECYCLE
    # =================================================

    def start_task(
        self,
        task
    ):
        """
        Create a new task or mark a matching task
        as running.
        """

        return self.update_task_status(
            task=task,
            status="running",
            steps=0,
            replans_used=0
        )

    def update_task_status(
        self,
        task,
        status,
        steps=None,
        replans_used=None
    ):
        """
        Update an existing task's lifecycle status.

        Supported statuses:

            pending
            running
            completed
            failed
            recovered

        If no matching task exists, a new task
        record is created.
        """

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

        valid_statuses = {

            "pending",
            "running",
            "completed",
            "failed",
            "recovered"
        }

        status = str(
            status
        ).strip().lower()

        if status not in valid_statuses:

            raise ValueError(
                f"Invalid task status: {status}"
            )

        data = self.load_json(
            self.tasks_file
        )

        tasks = data.get(
            "tasks",
            []
        )

        duplicate = (
            self._find_duplicate_task(
                task,
                tasks
            )
        )

        # ---------------------------------------------
        # No existing task
        # ---------------------------------------------

        if duplicate is None:

            return self.add_task(
                task=task,
                status=status,
                steps=(
                    0
                    if steps is None
                    else steps
                ),
                replans_used=(
                    0
                    if replans_used is None
                    else replans_used
                )
            )

        # ---------------------------------------------
        # Update existing task
        # ---------------------------------------------

        duplicate["status"] = status

        if steps is not None:

            duplicate["steps"] = int(
                steps
            )

        if replans_used is not None:

            duplicate["replans_used"] = int(
                replans_used
            )

        duplicate["timestamp"] = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        data["tasks"] = tasks

        self.save_json(
            self.tasks_file,
            data
        )

        return duplicate

    def get_tasks_by_status(
        self,
        status
    ):
        """
        Return all tasks matching a lifecycle status.
        """

        if not isinstance(
            status,
            str
        ):

            return []

        status = (
            status
            .strip()
            .lower()
        )

        return [

            task

            for task in self.get_tasks()

            if (
                isinstance(
                    task,
                    dict
                )
                and str(
                    task.get(
                        "status",
                        ""
                    )
                ).strip().lower()
                == status
            )
        ]

    # =================================================
    # GET TASKS
    # =================================================

    def get_tasks(self):

        data = self.load_json(
            self.tasks_file
        )

        return data.get(
            "tasks",
            []
        )

    # =================================================
    # TASK RETRIEVAL
    # =================================================

    def find_tasks(
        self,
        query,
        limit=5
    ):

        if not isinstance(
            query,
            str
        ):

            return []

        query = (
            query
            .strip()
            .lower()
        )

        if not query:

            return []

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

            # Exact phrase bonus
            if query in task_text:

                score += 0.50

            # Single-token query bonus
            if len(
                query_tokens
            ) == 1:

                score += 0.25

            scored_tasks.append(
                (
                    score,
                    task
                )
            )

        # Highest relevance first
        scored_tasks.sort(
            key=lambda item: item[0],
            reverse=True
        )

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