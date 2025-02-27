# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Any, Callable, Optional

from torch import Tensor, tensor

from torchmetrics.functional.retrieval.recall import retrieval_recall
from torchmetrics.retrieval.retrieval_metric import IGNORE_IDX, RetrievalMetric


class RetrievalRecall(RetrievalMetric):
    """
    Computes `Recall
    <https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)#Recall>`__.

    Works with binary target data. Accepts float predictions from a model output.

    Forward accepts:

    - ``indexes`` (long tensor): ``(N, ...)``
    - ``preds`` (float tensor): ``(N, ...)``
    - ``target`` (long or bool tensor): ``(N, ...)``

    ``indexes``, ``preds`` and ``target`` must have the same dimension.
    ``indexes`` indicate to which query a prediction belongs.
    Predictions will be first grouped by ``indexes`` and then `Recall` will be computed as the mean
    of the `Recall` over each query.

    Args:
        empty_target_action:
            Specify what to do with queries that do not have at least a positive ``target``. Choose from:

                - ``'skip'``: skip those queries (default); if all queries are skipped, ``0.0`` is returned
                - ``'error'``: raise a ``ValueError``
                - ``'pos'``: score on those queries is counted as ``1.0``
                - ``'neg'``: score on those queries is counted as ``0.0``

        exclude:
            Do not take into account predictions where the ``target`` is equal to this value. default `-100`
        compute_on_step:
            Forward only calls ``update()`` and return None if this is set to False. default: True
        dist_sync_on_step:
            Synchronize metric state across processes at each ``forward()``
            before returning the value at the step. default: False
        process_group:
            Specify the process group on which synchronization is called. default: None (which selects
            the entire world)
        dist_sync_fn:
            Callback that performs the allgather operation on the metric state. When `None`, DDP
            will be used to perform the allgather. default: None
        k: consider only the top k elements for each query. default: None

    Example:
        >>> from torchmetrics import RetrievalRecall
        >>> indexes = tensor([0, 0, 0, 1, 1, 1, 1])
        >>> preds = tensor([0.2, 0.3, 0.5, 0.1, 0.3, 0.5, 0.2])
        >>> target = tensor([False, False, True, False, True, False, True])
        >>> r2 = RetrievalRecall(k=2)
        >>> r2(indexes, preds, target)
        tensor(0.7500)
    """

    def __init__(
        self,
        empty_target_action: str = 'skip',
        exclude: int = IGNORE_IDX,
        compute_on_step: bool = True,
        dist_sync_on_step: bool = False,
        process_group: Optional[Any] = None,
        dist_sync_fn: Callable = None,
        k: int = None
    ):
        super().__init__(
            empty_target_action=empty_target_action,
            exclude=exclude,
            compute_on_step=compute_on_step,
            dist_sync_on_step=dist_sync_on_step,
            process_group=process_group,
            dist_sync_fn=dist_sync_fn
        )

        if (k is not None) and not (isinstance(k, int) and k > 0):
            raise ValueError("`k` has to be a positive integer or None")
        self.k = k

    def _metric(self, preds: Tensor, target: Tensor) -> Tensor:
        valid_indexes = (target != self.exclude)
        return retrieval_recall(preds[valid_indexes], target[valid_indexes], k=self.k)
