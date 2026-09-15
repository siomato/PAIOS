import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class PositionEmbedding(nn.Module):
    """
    Positional embedding used by the INCLUDE Transformer.
    """

    def __init__(self, config):
        super().__init__()

        self.position_embeddings = nn.Embedding(
            config.max_position_embeddings,
            config.hidden_size,
        )

        self.LayerNorm = nn.LayerNorm(
            config.hidden_size,
            eps=config.layer_norm_eps,
        )

        self.dropout = nn.Dropout(
            config.hidden_dropout_prob,
        )

        self.register_buffer(
            "position_ids",
            torch.arange(
                config.max_position_embeddings
            ).expand((1, -1)),
        )

    def forward(self, x):
        seq_length = x.size(1)

        position_ids = self.position_ids[:, :seq_length]

        position_embeddings = self.position_embeddings(
            position_ids
        )

        x = x + position_embeddings
        x = self.LayerNorm(x)
        x = self.dropout(x)

        return x


class SelfAttention(nn.Module):
    """
    Compatibility implementation of the attention mechanism
    used by the INCLUDE Transformer checkpoint.

    This deliberately avoids HuggingFace BertSelfAttention so
    the pretrained checkpoint can run with modern transformers.
    """

    def __init__(self, config):
        super().__init__()

        hidden_size = config.hidden_size
        num_heads = config.num_attention_heads

        if hidden_size % num_heads != 0:
            raise ValueError(
                "hidden_size must be divisible by num_attention_heads"
            )

        self.num_attention_heads = num_heads
        self.attention_head_size = hidden_size // num_heads
        self.all_head_size = hidden_size

        self.query = nn.Linear(
            hidden_size,
            hidden_size,
        )

        self.key = nn.Linear(
            hidden_size,
            hidden_size,
        )

        self.value = nn.Linear(
            hidden_size,
            hidden_size,
        )

        self.dropout = nn.Dropout(
            config.attention_probs_dropout_prob
            if hasattr(config, "attention_probs_dropout_prob")
            else 0.1
        )

    def transpose_for_scores(self, x):
        """
        [batch, sequence, hidden]
        ->
        [batch, heads, sequence, head_size]
        """

        new_shape = (
            x.size(0),
            x.size(1),
            self.num_attention_heads,
            self.attention_head_size,
        )

        x = x.view(*new_shape)

        return x.permute(
            0,
            2,
            1,
            3,
        )

    def forward(self, hidden_states):
        query_layer = self.transpose_for_scores(
            self.query(hidden_states)
        )

        key_layer = self.transpose_for_scores(
            self.key(hidden_states)
        )

        value_layer = self.transpose_for_scores(
            self.value(hidden_states)
        )

        # ---------------------------------------------------------
        # Attention scores
        # ---------------------------------------------------------

        attention_scores = torch.matmul(
            query_layer,
            key_layer.transpose(-1, -2),
        )

        attention_scores = attention_scores / math.sqrt(
            self.attention_head_size
        )

        # ---------------------------------------------------------
        # Softmax
        # ---------------------------------------------------------

        attention_probs = F.softmax(
            attention_scores,
            dim=-1,
        )

        attention_probs = self.dropout(
            attention_probs
        )

        # ---------------------------------------------------------
        # Context
        # ---------------------------------------------------------

        context_layer = torch.matmul(
            attention_probs,
            value_layer,
        )

        # [batch, heads, seq, head]
        # ->
        # [batch, seq, heads, head]

        context_layer = context_layer.permute(
            0,
            2,
            1,
            3,
        ).contiguous()

        # Merge heads

        context_layer = context_layer.view(
            context_layer.size(0),
            context_layer.size(1),
            self.all_head_size,
        )

        return context_layer


class TransformerLayer(nn.Module):
    """
    BERT-style Transformer layer matching the parameter
    structure of the INCLUDE checkpoint.
    """

    def __init__(self, config):
        super().__init__()

        hidden_size = config.hidden_size

        # ---------------------------------------------------------
        # Self attention
        # ---------------------------------------------------------

        self.attention = nn.Module()

        self.attention.self = SelfAttention(
            config
        )

        # ---------------------------------------------------------
        # Attention output
        # ---------------------------------------------------------

        self.attention.output = nn.Module()

        self.attention.output.dense = nn.Linear(
            hidden_size,
            hidden_size,
        )

        self.attention.output.LayerNorm = nn.LayerNorm(
            hidden_size,
            eps=config.layer_norm_eps,
        )

        self.attention.output.dropout = nn.Dropout(
            config.hidden_dropout_prob
        )

        # ---------------------------------------------------------
        # Intermediate FFN
        # ---------------------------------------------------------

        self.intermediate = nn.Module()

        self.intermediate.dense = nn.Linear(
            hidden_size,
            config.intermediate_size,
        )

        # ---------------------------------------------------------
        # Output FFN
        # ---------------------------------------------------------

        self.output = nn.Module()

        self.output.dense = nn.Linear(
            config.intermediate_size,
            hidden_size,
        )

        self.output.LayerNorm = nn.LayerNorm(
            hidden_size,
            eps=config.layer_norm_eps,
        )

        self.output.dropout = nn.Dropout(
            config.hidden_dropout_prob
        )

    def forward(self, x):

        # =========================================================
        # SELF ATTENTION
        # =========================================================

        attention_output = self.attention.self(
            x
        )

        attention_output = self.attention.output.dense(
            attention_output
        )

        attention_output = self.attention.output.dropout(
            attention_output
        )

        attention_output = self.attention.output.LayerNorm(
            attention_output + x
        )

        # =========================================================
        # FEED FORWARD NETWORK
        # =========================================================

        intermediate_output = self.intermediate.dense(
            attention_output
        )

        intermediate_output = F.gelu(
            intermediate_output
        )

        layer_output = self.output.dense(
            intermediate_output
        )

        layer_output = self.output.dropout(
            layer_output
        )

        layer_output = self.output.LayerNorm(
            layer_output + attention_output
        )

        return layer_output


class Transformer(nn.Module):
    """
    INCLUDE Transformer.

    Input:
        [batch, sequence_length, 134]

    Output:
        [batch, 263]
    """

    def __init__(self, config, n_classes=263):
        super().__init__()

        # =========================================================
        # INPUT PROJECTION
        # =========================================================

        self.l1 = nn.Linear(
            in_features=config.input_size,
            out_features=config.hidden_size,
        )

        # =========================================================
        # POSITION EMBEDDING
        # =========================================================

        self.embedding = PositionEmbedding(
            config
        )

        # =========================================================
        # TRANSFORMER LAYERS
        # =========================================================

        self.layers = nn.ModuleList(
            [
                TransformerLayer(config)
                for _ in range(
                    config.num_hidden_layers
                )
            ]
        )

        # =========================================================
        # CLASSIFICATION
        # =========================================================

        self.l2 = nn.Linear(
            in_features=config.hidden_size,
            out_features=n_classes,
        )

    def forward(self, x):

        # 134 -> 256

        x = self.l1(x)

        # Add positional information

        x = self.embedding(x)

        # Transformer encoder

        for layer in self.layers:
            x = layer(x)

        # =========================================================
        # TEMPORAL MAX POOLING
        # =========================================================

        x = torch.max(
            x,
            dim=1,
        ).values

        # =========================================================
        # DROPOUT
        # =========================================================

        x = F.dropout(
            x,
            p=0.2,
            training=self.training,
        )

        # =========================================================
        # CLASSIFIER
        # =========================================================

        x = self.l2(x)

        return x