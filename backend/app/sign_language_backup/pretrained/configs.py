from dataclasses import dataclass, field

import transformers
import timm


# ============================================================
# LSTM CONFIGURATION
# ============================================================

@dataclass
class LstmConfig:
    input_size: int = 134
    hidden_size: int = 256
    num_layers: int = 5
    batch_first: bool = True
    bidirectional: bool = True
    dropout: float = 0.2


# ============================================================
# XGBOOST CONFIGURATION
# ============================================================

@dataclass
class XgbConfig:
    booster: str = "gbtree"
    silent: int = 0
    max_depth: int = 2

    subsample: float = 0.9923301318585108
    colsample_bytree: float = 0.7747027267489391

    reg_lambda: int = 3

    objective: str = "multi:softprob"
    eval_metric: str = "mlogloss"

    # Use "hist" if CUDA/GPU is not available.
    tree_method: str = "gpu_hist"


# ============================================================
# TRANSFORMER CONFIGURATION
# ============================================================

@dataclass
class TransformerConfig:
    """
    Configuration for the AI4Bharat INCLUDE Transformer.

    The pretrained checkpoint:
        include_no_cnn_transformer_small.pth

    expects:

        input_size              = 134
        hidden_size             = 256
        intermediate_size       = 3072
        attention_heads         = 4
        transformer_layers      = 2
        max_sequence_length     = 256
    """

    # --------------------------------------------------------
    # Model size
    # --------------------------------------------------------

    size: str

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    input_size: int = 134

    # --------------------------------------------------------
    # Positional embedding
    # --------------------------------------------------------

    max_position_embeddings: int = field(
        default=256,
        repr=False
    )

    # --------------------------------------------------------
    # Layer normalization
    # --------------------------------------------------------

    layer_norm_eps: float = field(
        default=1e-12,
        repr=False
    )

    # --------------------------------------------------------
    # Dropout
    # --------------------------------------------------------

    hidden_dropout_prob: float = field(
        default=0.1,
        repr=False
    )

    # --------------------------------------------------------
    # Transformer dimensions
    # --------------------------------------------------------

    hidden_size: int = field(
        default=512,
        repr=False
    )

    intermediate_size: int = field(
        default=3072,
        repr=False
    )

    num_attention_heads: int = field(
        default=8,
        repr=False
    )

    num_hidden_layers: int = field(
        default=4,
        repr=False
    )

    # --------------------------------------------------------
    # HuggingFace BERT configuration
    # --------------------------------------------------------

    model_config: transformers.BertConfig = field(
        init=False,
        repr=False
    )

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __post_init__(self):

        if self.size not in ["small", "large"]:
            raise ValueError(
                f"Invalid Transformer size: {self.size}. "
                f"Expected 'small' or 'large'."
            )

        # ----------------------------------------------------
        # INCLUDE SMALL
        # ----------------------------------------------------

        if self.size == "small":

            self.hidden_size = 256

            self.intermediate_size = 3072

            self.num_attention_heads = 4

            self.num_hidden_layers = 2

        # ----------------------------------------------------
        # INCLUDE LARGE
        # ----------------------------------------------------

        elif self.size == "large":

            self.hidden_size = 512

            self.intermediate_size = 3072

            self.num_attention_heads = 8

            self.num_hidden_layers = 4

        # ----------------------------------------------------
        # Create BERT configuration
        # ----------------------------------------------------

        self.model_config = transformers.BertConfig(

            hidden_size=self.hidden_size,

            intermediate_size=self.intermediate_size,

            num_attention_heads=self.num_attention_heads,

            num_hidden_layers=self.num_hidden_layers,

            max_position_embeddings=self.max_position_embeddings,

            layer_norm_eps=self.layer_norm_eps,

            hidden_dropout_prob=self.hidden_dropout_prob,

            attention_probs_dropout_prob=self.hidden_dropout_prob,

            # Important for the current Transformers version.
            _attn_implementation="eager",
        )


# ============================================================
# CNN CONFIGURATION
# ============================================================

@dataclass
class CnnConfig:

    model: str = "mobilenetv2_100"

    output_dim: int = 1280

    def __post_init__(self):

        available_models = timm.list_models(pretrained=True)

        if self.model not in available_models:

            raise ValueError(
                f"CNN model '{self.model}' is not available "
                f"in timm."
            )