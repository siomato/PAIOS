import numpy as np

from app.sign_language.pretrained.preprocessing import (
    FEATURE_SIZE, SEQUENCE_LENGTH, preprocess_clip,
)
from app.sign_language.pretrained.pretrained_model import get_model


def test_preprocess_shape_and_scale():
    x = np.zeros((10, FEATURE_SIZE), dtype=np.float32)
    x[:, 0] = 0.5
    x[:, 1] = 0.5
    out = preprocess_clip(x)
    assert out.shape == (SEQUENCE_LENGTH, FEATURE_SIZE)
    assert out[0, 0] == 960.0
    assert out[0, 1] == 540.0
    assert np.all(out[10:] == 0)


def test_model_checkpoint_contract():
    model = get_model()
    assert model.loaded
    assert len(model.labels) == 263
    assert model.model.l1.weight.shape == (256, 134)
    assert model.model.l2.weight.shape == (263, 256)
    dummy = np.zeros((SEQUENCE_LENGTH, FEATURE_SIZE), dtype=np.float32)
    result = model.predict(dummy)
    assert set(("gesture", "confidence", "recognized")) <= result.keys()
