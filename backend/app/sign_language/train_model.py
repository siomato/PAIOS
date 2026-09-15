import os
import csv
import joblib
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "gesture_model.joblib"
)


# =========================================================
# NORMALIZE LANDMARKS
# =========================================================

def normalize_landmarks(values):

    if len(values) != 63:
        return None

    points = np.array(
        values,
        dtype=np.float32
    ).reshape(21, 3)

    # Wrist becomes origin
    wrist = points[0].copy()

    points = points - wrist

    # Hand-size normalization
    scale = np.linalg.norm(
        points[9]
    )

    if scale < 1e-6:
        return None

    points = points / scale

    return points.flatten().tolist()


# =========================================================
# LOAD DATASET
# =========================================================

def load_dataset():

    X = []
    y = []

    if not os.path.isdir(DATASET_DIR):

        raise RuntimeError(
            f"Dataset directory not found:\n"
            f"{DATASET_DIR}"
        )

    for gesture in sorted(
        os.listdir(DATASET_DIR)
    ):

        gesture_dir = os.path.join(
            DATASET_DIR,
            gesture
        )

        if not os.path.isdir(
            gesture_dir
        ):
            continue

        csv_path = os.path.join(
            gesture_dir,
            "samples.csv"
        )

        if not os.path.isfile(
            csv_path
        ):
            continue

        print(
            f"📂 Loading: {gesture}"
        )

        with open(
            csv_path,
            "r",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                try:

                    raw = []

                    for i in range(21):

                        raw.extend([
                            float(row[f"x{i}"]),
                            float(row[f"y{i}"]),
                            float(row[f"z{i}"])
                        ])

                    features = normalize_landmarks(
                        raw
                    )

                    if features is None:
                        continue

                    X.append(features)
                    y.append(gesture)

                except (
                    ValueError,
                    KeyError
                ):
                    continue

    return X, y


# =========================================================
# TRAIN
# =========================================================

def main():

    print()
    print("=" * 60)
    print("🧠 PAIOS MLP SIGN LANGUAGE TRAINING")
    print("=" * 60)
    print()

    X, y = load_dataset()

    if len(X) == 0:

        raise RuntimeError(
            "No valid samples found."
        )

    classes = sorted(
        set(y)
    )

    print()
    print(
        f"📊 Total samples: {len(X)}"
    )

    print(
        f"🏷️ Classes: {classes}"
    )

    print()

    # -----------------------------------------------------
    # Dataset distribution
    # -----------------------------------------------------

    for gesture in classes:

        print(
            f"   {gesture:<20} "
            f"{y.count(gesture)}"
        )

    print()

    if len(classes) < 2:

        raise RuntimeError(
            "At least two gesture classes "
            "are required."
        )

    # -----------------------------------------------------
    # Train / test split
    # -----------------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    print(
        f"📚 Training samples: "
        f"{len(X_train)}"
    )

    print(
        f"🧪 Testing samples: "
        f"{len(X_test)}"
    )

    print()

    # =====================================================
    # MLP MODEL
    # =====================================================

    model = Pipeline(
        [
            (
                "scaler",
                StandardScaler()
            ),

            (
                "classifier",
                MLPClassifier(
                    hidden_layer_sizes=(
                        128,
                        64
                    ),
                    activation="relu",
                    solver="adam",
                    alpha=0.0001,
                    batch_size=32,
                    learning_rate_init=0.001,
                    max_iter=500,
                    early_stopping=True,
                    validation_fraction=0.15,
                    n_iter_no_change=20,
                    random_state=42
                )
            )
        ]
    )

    print(
        "🧠 Training MLP neural network..."
    )

    model.fit(
        X_train,
        y_train
    )

    print(
        "✅ MLP training completed."
    )

    # =====================================================
    # EVALUATION
    # =====================================================

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print()
    print("=" * 60)
    print("📈 MODEL EVALUATION")
    print("=" * 60)
    print()

    print(
        f"Accuracy: "
        f"{accuracy * 100:.2f}%"
    )

    print()

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    # =====================================================
    # SAVE
    # =====================================================

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    print("=" * 60)
    print("💾 MLP MODEL SAVED")
    print("=" * 60)
    print()

    print(
        f"📁 {MODEL_PATH}"
    )

    print()
    print(
        "✅ PAIOS MLP MODEL READY"
    )
    print()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()