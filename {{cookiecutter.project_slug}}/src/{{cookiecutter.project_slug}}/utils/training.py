from typing import Any, Callable, Dict, Optional, Set, Tuple, TypedDict, Union
import logging
import glob
import os
import re
import time

import torch
import torch.distributed as dist


logger = logging.getLogger(__name__)


class TrainerState(TypedDict):
    epochs_completed: int
    batches_in_epoch_completed: int


class CheckpointState(TypedDict):
    model_state: Dict[str, Any]
    trainer_state: TrainerState


class CheckpointClosure:
    def __init__(self):
        self.checkpoint_state = None
        self.called = False

    def call(self) -> CheckpointState:
        raise NotImplementedError

    def __call__(self) -> CheckpointState:
        if not self.called:
            self.checkpoint_state = self.call()
            self.called = True
        return self.checkpoint_state


def device_mapping(cuda_device: int):
    """
    In order to `torch.load()` a GPU-trained model onto a CPU (or specific GPU),
    you have to supply a `map_location` function. Call this with
    the desired `cuda_device` to get the function that `torch.load()` needs.
    """

    def inner_device_mapping(storage: torch.Storage, location) -> torch.Storage:
        if cuda_device >= 0:
            return storage.cuda(cuda_device)
        else:
            return storage

    return inner_device_mapping


class HasBeenWarned:
    tqdm_ignores_underscores = False


def description_from_metrics(metrics: Dict[str, float]) -> str:
    if not HasBeenWarned.tqdm_ignores_underscores and any(
        metric_name.startswith("_") for metric_name in metrics
    ):
        logger.warning(
            'Metrics with names beginning with "_" will '
            "not be logged to the tqdm progress bar."
        )
        HasBeenWarned.tqdm_ignores_underscores = True
    return (
        ", ".join(
            [
                "%s: %.4f" % (name, value)
                for name, value in metrics.items()
                if not name.startswith("_")
            ]
        )
        + " ||"
    )


class Checkpointer:
    """
    This class implements the functionality for checkpointing your model and trainer state
    during training. It is agnostic as to what those states look like (they are typed as
    `Dict[str, Any]`), but they will be fed to `torch.save` so they should be serializable
    in that sense. They will also be restored as `Dict[str, Any]`, which means the calling
    code is responsible for knowing what to do with them.

    Parameters:
    - serialization_dir: Directory where checkpoints are saved.
    - save_completed_epochs: Saves model and trainer state at the end of each completed epoch.
    - save_every_num_seconds: If set, makes sure we never go longer than this number of seconds between saving a model.
    - save_every_num_batches: If set, makes sure we never go longer than this number of batches between saving a model.
    - keep_most_recent_by_count: Number of model checkpoints to keep on disk.
    - keep_most_recent_by_age: Number of seconds we'll keep a checkpoint before deleting it.
    """

    def __init__(
        self,
        serialization_dir: Union[str, os.PathLike],
        save_completed_epochs: bool = True,
        save_every_num_seconds: Optional[float] = None,
        save_every_num_batches: Optional[int] = None,
        keep_most_recent_by_count: Optional[int] = 2,
        keep_most_recent_by_age: Optional[int] = None,
    ) -> None:
        self._serialization_dir = str(serialization_dir)
        self._save_completed_epochs = save_completed_epochs
        self._save_every_num_seconds = save_every_num_seconds
        self._save_every_num_batches = save_every_num_batches
        self._keep_most_recent_by_count = keep_most_recent_by_count
        self._keep_most_recent_by_age = keep_most_recent_by_age
        self._last_save_time = time.time()
        self._last_save_num_epochs_completed = 0
        self._last_save_num_batches_in_epoch_completed = 0
        self._rank = (
            0
            if not dist.is_available() or not dist.is_initialized()
            else dist.get_rank()
        )
        self.state_is_sharded = False

        if (
            dist.is_available()
            and dist.is_initialized()
            and save_every_num_seconds is not None
        ):
            raise ValueError(
                "Checkointer parameter 'save_every_num_seconds' is not supported in distributed training"
            )

    @property
    def _is_primary(self) -> bool:
        return self._rank == 0

    def _model_state_path(
        self, epochs_completed: int, batches_in_epoch_completed: int
    ) -> str:
        path = os.path.join(
            self._serialization_dir,
            f"model_state_e{epochs_completed}_b{batches_in_epoch_completed}",
        )
        if self.state_is_sharded:
            return path + f"_w{self._rank}.pt"
        else:
            return path + ".pt"

    def _training_state_path(
        self, epochs_completed: int, batches_in_epoch_completed: int
    ) -> str:
        path = os.path.join(
            self._serialization_dir,
            f"training_state_e{epochs_completed}_b{batches_in_epoch_completed}",
        )
        if self.state_is_sharded:
            return path + f"_w{self._rank}.pt"
        else:
            return path + ".pt"

    _model_state_file_re = re.compile(
        r"(.*[/\\])?model_state_e(\d+)_b(\d+)(_w\d+)?\.pt$"
    )
    _training_state_file_re = re.compile(
        r"(.*[/\\])?training_state_e(\d+)_b(\d+)(_w\d+)?\.pt$"
    )

    @classmethod
    def _parse_model_state_path(
        cls, path: Union[str, os.PathLike]
    ) -> Optional[Tuple[int, int]]:
        match = cls._model_state_file_re.match(str(path))
        if match is None:
            return None
        else:
            try:
                return int(match.group(2)), int(match.group(3))
            except ValueError:
                return None

    @classmethod
    def _parse_training_state_path(
        cls, path: Union[str, os.PathLike]
    ) -> Optional[Tuple[int, int]]:
        match = cls._training_state_file_re.match(str(path))
        if match is None:
            return None
        else:
            try:
                return int(match.group(2)), int(match.group(3))
            except ValueError:
                return None

    def _find_all_checkpoints(self) -> Set[Tuple[int, int]]:
        """Returns a set of tuples, each representing a checkpoint."""
        checkpoints = set()
        pattern = (
            f"model_state_e*_b*_w{self._rank}.pt"
            if self.state_is_sharded
            else "model_state_e*_b*.pt"
        )
        for model_state_file in glob.iglob(
            os.path.join(self._serialization_dir, pattern)
        ):
            point_in_time = self._parse_model_state_path(model_state_file)
            if point_in_time is None:
                continue
            else:
                checkpoints.add(point_in_time)
        return checkpoints

    def _remove_checkpoint(
        self, epochs_completed: int, batches_in_epoch_completed: int
    ):
        for state_name in ("model_state", "training_state"):
            pattern = (
                f"{state_name}_e{epochs_completed}_b{batches_in_epoch_completed}*.pt"
            )
            for fname in glob.iglob(os.path.join(self._serialization_dir, pattern)):
                os.remove(fname)

    def maybe_save_checkpoint(
        self,
        checkpoint_closure: Callable[[], CheckpointState],
        num_epochs_completed: int,
        num_batches_in_epoch_completed: int,
        end_of_epoch: bool = False,
    ) -> bool:
        """
        Figures out whether we need to save a checkpoint, and does so if necessary.
        """
        if num_epochs_completed == self._last_save_num_epochs_completed:
            last_save_num_batches_in_epoch_completed = (
                self._last_save_num_batches_in_epoch_completed
            )
        else:
            last_save_num_batches_in_epoch_completed = 0

        should_save = (
            (end_of_epoch and self._save_completed_epochs)
            or (
                self._save_every_num_seconds is not None
                and (time.time() - self._last_save_time >= self._save_every_num_seconds)
            )
            or (
                self._save_every_num_batches is not None
                and (
                    num_batches_in_epoch_completed
                    - last_save_num_batches_in_epoch_completed
                    >= self._save_every_num_batches
                )
            )
        )

        if should_save:
            self.save_checkpoint(checkpoint_closure)
            return True
        return False

    def save_checkpoint(
        self,
        checkpoint_closure: Callable[[], CheckpointState],
    ) -> None:
        if self._serialization_dir is None:
            return

        tcps = checkpoint_closure()  # get the CheckpointState
        if tcps is None:
            assert not self._is_primary and not self.state_is_sharded
            return

        epochs_completed = tcps["trainer_state"]["epochs_completed"]
        batches_in_epoch_completed = tcps["trainer_state"]["batches_in_epoch_completed"]

        model_state_path = self._model_state_path(
            epochs_completed,
            batches_in_epoch_completed,
        )
        if not os.path.isfile(model_state_path):
            logger.info(f"Saving model state to {model_state_path}")
            torch.save(tcps["model_state"], model_state_path)

        trainer_state_path = self._training_state_path(
            epochs_completed,
            batches_in_epoch_completed,
        )
        if not os.path.isfile(trainer_state_path):
            logger.info(f"Saving training state to {trainer_state_path}")
            torch.save(tcps["trainer_state"], trainer_state_path)

        self._last_save_time = time.time()
        self._last_save_num_epochs_completed = epochs_completed
        self._last_save_num_batches_in_epoch_completed = batches_in_epoch_completed

        if self._is_primary and (
            self._keep_most_recent_by_age is not None
            or self._keep_most_recent_by_count is not None
        ):
            checkpoints = list(self._find_all_checkpoints())
            checkpoints.sort(reverse=True)

            # Keep the most recent n checkpoints
            if self._keep_most_recent_by_count is not None:
                checkpoints_to_keep = set(
                    checkpoints[: self._keep_most_recent_by_count]
                )
            else:
                checkpoints_to_keep = set()

            # Keep the youngest checkpoints by age
            now = time.time()
            if self._keep_most_recent_by_age is not None:
                for checkpoint in checkpoints:
                    checkpoint_mtime = max(
                        os.path.getmtime(n)
                        for n in [
                            self._model_state_path(*checkpoint),
                            self._training_state_path(*checkpoint),
                        ]
                    )
                    if now - checkpoint_mtime <= self._keep_most_recent_by_age:
                        checkpoints_to_keep.add(checkpoint)

            # Remove everything we're not keeping
            for checkpoint in checkpoints:
                if checkpoint not in checkpoints_to_keep:
                    self._remove_checkpoint(*checkpoint)

    def find_latest_checkpoint(self) -> Optional[Tuple[str, str]]:
        """
        Return the location of the latest model and training state files.
        If there isn't a valid checkpoint then return None.
        """
        checkpoints = self._find_all_checkpoints()
        if len(checkpoints) <= 0:
            return None
        last_checkpoint = max(checkpoints)
        return self._model_state_path(*last_checkpoint), self._training_state_path(
            *last_checkpoint
        )

    def load_checkpoint(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Loads model state from a `serialization_dir` corresponding to the last saved checkpoint.
        This includes a training state, which is serialized separately from model parameters. This function
        should only be used to continue training - if you wish to load a model for inference/load parts
        of a model into a new computation graph, you should use the native Pytorch functions:
        `model.load_state_dict(torch.load("/path/to/model/weights.pt"))`

        If `self._serialization_dir` does not exist or does not contain any checkpointed weights,
        this function will do nothing and return empty dicts.

        Returns:
        - states: The model state and the training state.
        """
        latest_checkpoint = self.find_latest_checkpoint()
        if latest_checkpoint is None:
            return None

        model_path, training_state_path = latest_checkpoint

        # Load the parameters onto CPU, then transfer to GPU.
        # This avoids potential OOM on GPU for large models that
        # load parameters onto GPU then make a new GPU copy into the parameter
        # buffer. The GPU transfer happens implicitly in load_state_dict.
        model_state = torch.load(model_path, map_location=torch.device("cpu"))
        training_state = torch.load(
            training_state_path, map_location=torch.device("cpu")
        )
        return {"model_state": model_state, "trainer_state": training_state}
