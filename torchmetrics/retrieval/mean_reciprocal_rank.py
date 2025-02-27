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
from torch import Tensor, tensor

from torchmetrics.functional.retrieval.reciprocal_rank import retrieval_reciprocal_rank
from torchmetrics.retrieval.retrieval_metric import RetrievalMetric


class RetrievalMRR(RetrievalMetric):
    """
    Computes `Mean Reciprocal Rank
    <https://en.wikipedia.org/wiki/Mean_reciprocal_rank>`__.

    Works with binary target data. Accepts float predictions from a model output.

    Forward accepts

    - ``indexes`` (long tensor): ``(N, ...)``
    - ``preds`` (float tensor): ``(N, ...)``
    - ``target`` (long or bool tensor): ``(N, ...)``

    ``indexes``, ``preds`` and ``target`` must have the same dimension.
    ``indexes`` indicate to which query a prediction belongs.
    Predictions will be first grouped by ``indexes`` and then `MRR` will be computed as the mean
    of the `Reciprocal Rank` over each query.

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

    Example:
        >>> from torchmetrics import RetrievalMRR
        >>> indexes = tensor([0, 0, 0, 1, 1, 1, 1])
        >>> preds = tensor([0.2, 0.3, 0.5, 0.1, 0.3, 0.5, 0.2])
        >>> target = tensor([False, False, True, False, True, False, True])
        >>> mrr = RetrievalMRR()
        >>> mrr(indexes, preds, target)
        tensor(0.7500)
    """

    def _metric(self, preds: Tensor, target: Tensor) -> Tensor:
        valid_indexes = (target != self.exclude)
        return retrieval_reciprocal_rank(preds[valid_indexes], target[valid_indexes])
