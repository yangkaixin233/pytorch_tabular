# Pytorch Tabular
# Author: Manu Joseph <manujoseph@gmail.com>
# For license information, see LICENSE.TXT
"""DANet Model."""

import torch
import torch.nn as nn
from omegaconf import DictConfig

from pytorch_tabular.models.common.layers.embeddings import Embedding1dLayer

from ..base_model import BaseModel
from .arch_blocks import BasicBlock


class DANetBackbone(nn.Module):
    def __init__(
        self,
        n_continuous_features: int,
        cat_embedding_dims: list,
        n_layers: int,
        abstlay_dim_1: int,
        abstlay_dim_2: int,
        k: int,
        dropout_rate: float,
        block_activation: nn.Module,
        virtual_batch_size: int,
        embedding_dropout: float,
        batch_norm_continuous_input: bool,
    ):
        super().__init__()
        self.cat_embedding_dims = cat_embedding_dims
        self.n_continuous_features = n_continuous_features
        self.input_dim = n_continuous_features + sum([y for x, y in cat_embedding_dims])
        self.n_layers = n_layers
        self.abstlay_dim_1 = abstlay_dim_1
        self.abstlay_dim_2 = abstlay_dim_2
        self.k = k
        self.dropout_rate = dropout_rate
        self.block_activation = block_activation
        self.virtual_batch_size = virtual_batch_size
        self.batch_norm_continuous_input = batch_norm_continuous_input
        self.embedding_dropout = embedding_dropout

        self.output_dim = self.abstlay_dim_2
        self._build_network()

    def _build_network(self):
        params = {
            "fix_input_dim": self.input_dim,
            "k": self.k,
            "virtual_batch_size": self.virtual_batch_size,
            "abstlay_dim_1": self.abstlay_dim_1,
            "abstlay_dim_2": self.abstlay_dim_2,
            "drop_rate": self.dropout_rate,
            "block_activation": self.block_activation,
        }
        self.init_layer = BasicBlock(self.input_dim, **params)
        self.layers = nn.ModuleList()
        for i in range(self.n_layers - 1):
            self.layers.append(BasicBlock(self.abstlay_dim_2, **params))

    def _build_embedding_layer(self):
        return Embedding1dLayer(
            continuous_dim=self.n_continuous_features,
            categorical_embedding_dims=self.cat_embedding_dims,
            embedding_dropout=self.embedding_dropout,
            batch_norm_continuous_input=self.batch_norm_continuous_input,
            virtual_batch_size=self.virtual_batch_size,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.init_layer(x)
        for layer in self.layers:
            out = layer(x, pre_out=out)
        return out

    # Not Tested Properly
    # def _calculate_feature_importance(self):
    #     n, h, f, _ = self.attention_weights_[0].shape
    #     device = self.attention_weights_[0].device
    #     L = len(self.attention_weights_)
    #     self.local_feature_importance = torch.zeros((n, f), device=device)
    #     for attn_weights in self.attention_weights_:
    #         self.local_feature_importance += attn_weights[:, :, :, -1].sum(dim=1)
    #     self.local_feature_importance = (1 / (h * L)) * self.local_feature_importance[
    #         :, :-1
    #     ]
    #     self.feature_importance_ = (
    #         self.local_feature_importance.mean(dim=0).detach().cpu().numpy()
    #     )
    # self.feature_importance_count_+=attn_weights.shape[0]


class DANetModel(BaseModel):
    def __init__(self, config: DictConfig, **kwargs):
        super().__init__(config, **kwargs)

    @property
    def backbone(self):
        return self._backbone

    @property
    def embedding_layer(self):
        return self._embedding_layer

    @property
    def head(self):
        return self._head

    def _build_network(self):
        # Backbone
        self._backbone = DANetBackbone(
            cat_embedding_dims=self.hparams.embedding_dims,
            n_continuous_features=self.hparams.continuous_dim,
            n_layers=self.hparams.n_layers,
            abstlay_dim_1=self.hparams.abstlay_dim_1,
            abstlay_dim_2=self.hparams.abstlay_dim_2,
            k=self.hparams.k,
            dropout_rate=self.hparams.dropout_rate,
            block_activation=getattr(nn, self.hparams.block_activation)(),
            virtual_batch_size=self.hparams.virtual_batch_size,
            embedding_dropout=self.hparams.embedding_dropout,
            batch_norm_continuous_input=self.hparams.batch_norm_continuous_input,
        )
        # Embedding Layer
        self._embedding_layer = self._backbone._build_embedding_layer()
        # Head
        self._head = self._get_head_from_config()
