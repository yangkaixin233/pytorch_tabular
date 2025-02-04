# Pytorch Tabular
# Author: Manu Joseph <manujoseph@gmail.com>
# For license information, see LICENSE.TXT
"""AutomaticFeatureInteraction Config."""
from dataclasses import dataclass, field
from typing import Optional

from pytorch_tabular.config import ModelConfig


@dataclass
class DANetConfig(ModelConfig):
    """DANet configuration
    Args:
        n_layers (int): Number of Blocks in the DANet. Defaults to 16

        abstlay_dim_1 (int): The dimension for the intermediate output in the
                first ABSTLAY layer in a Block. Defaults to 32

        abstlay_dim_2 (int): The dimension for the intermediate output in the
                second ABSTLAY layer in a Block. Defaults to 64

        k (int): The number of feature groups in the ABSTLAY layer. Defaults to 5

        dropout_rate (float): Dropout to be applied in the Block. Defaults to 0.1

        task (str): Specify whether the problem is regression or classification. `backbone` is a task which
                considers the model as a backbone to generate features. Mostly used internally for SSL and related
                tasks.. Choices are: [`regression`,`classification`,`backbone`].

        head (Optional[str]): The head to be used for the model. Should be one of the heads defined in
                `pytorch_tabular.models.common.heads`. Defaults to  LinearHead. Choices are:
                [`None`,`LinearHead`,`MixtureDensityHead`].

        head_config (Optional[Dict]): The config as a dict which defines the head. If left empty, will be
                initialized as default linear head.

        embedding_dims (Optional[List]): The dimensions of the embedding for each categorical column as a
                list of tuples (cardinality, embedding_dim). If left empty, will infer using the cardinality of
                the categorical column using the rule min(50, (x + 1) // 2)

        embedding_dropout (float): Dropout to be applied to the Categorical Embedding. Defaults to 0.1

        batch_norm_continuous_input (bool): If True, we will normalize the continuous layer by passing it
                through a BatchNorm layer.

        learning_rate (float): The learning rate of the model. Defaults to 1e-3.

        loss (Optional[str]): The loss function to be applied. By Default it is MSELoss for regression and
                CrossEntropyLoss for classification. Unless you are sure what you are doing, leave it at MSELoss
                or L1Loss for regression and CrossEntropyLoss for classification

        metrics (Optional[List[str]]): the list of metrics you need to track during training. The metrics
                should be one of the functional metrics implemented in ``torchmetrics``. By default, it is
                accuracy if classification and mean_squared_error for regression

        metrics_params (Optional[List]): The parameters to be passed to the metrics function. `task` is forced to
                be `multiclass` because the multiclass version can handle binary as well and for simplicity we are
                only using `multiclass`.

        metrics_prob_input (Optional[List]): Is a mandatory parameter for classification metrics defined in the config.
            This defines whether the input to the metric function is the probability or the class. Length should be
            same as the number of metrics. Defaults to None.

        target_range (Optional[List]): The range in which we should limit the output variable. Currently
                ignored for multi-target regression. Typically used for Regression problems. If left empty, will
                not apply any restrictions

        seed (int): The seed for reproducibility. Defaults to 42
    """

    n_layers: int = field(
        default=16,
        metadata={"help": "Number of Blocks in the DANet. Each block has 2 Abstlay Blocks each. Defaults to 16"},
    )

    abstlay_dim_1: int = field(
        default=32,
        metadata={
            "help": "The dimension for the intermediate output in the first ABSTLAY layer in a Block. Defaults to 32"
        },
    )

    abstlay_dim_2: Optional[int] = field(
        default=None,
        metadata={
            "help": "The dimension for the intermediate output in the second ABSTLAY layer in a Block. "
            "If None, it will be twice abstlay_dim_1. Defaults to None"
        },
    )
    k: int = field(
        default=5,
        metadata={"help": "The number of feature groups in the ABSTLAY layer. Defaults to 5"},
    )
    dropout_rate: float = field(
        default=0.1,
        metadata={"help": "Dropout to be applied in the Block. Defaults to 0.1"},
    )
    block_activation: str = field(
        default="LeakyReLU",
        metadata={
            "help": "The activation type in the classification head. The default activation in PyTorch"
            " like ReLU, TanH, LeakyReLU, etc."
            " https://pytorch.org/docs/stable/nn.html#non-linear-activations-weighted-sum-nonlinearity"
        },
    )

    _module_src: str = field(default="models.danet")
    _model_name: str = field(default="DANetModel")
    _backbone_name: str = field(default="DANetBackbone")
    _config_name: str = field(default="DANetConfig")

    def __post_init__(self):
        assert self.virtual_batch_size is not None, "virtual_batch_size cannot be None for DANet "
        " since it uses GhostBatchNorm in the architecture. Please set it to a value less than or "
        "equal to the batch_size, preferably something small ike 256 or 512"
        if self.abstlay_dim_2 is None:
            self.abstlay_dim_2 = self.abstlay_dim_1 * 2
        return super().__post_init__()


# if __name__ == "__main__":
#     from pytorch_tabular.utils import generate_doc_dataclass
#     print(generate_doc_dataclass(FTTransformerConfig))
