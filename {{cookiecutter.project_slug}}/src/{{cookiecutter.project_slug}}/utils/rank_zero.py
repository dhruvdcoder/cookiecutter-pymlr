{% if cookiecutter.use_lightning_utilities == "y" %}
from typing import Any, Optional, Union
from lightning_utilities.core.rank_zero import rank_zero_info, rank_zero_warn, rank_zero_debug, rank_zero_only, rank_prefixed_message
{% elif cookiecutter.use_torchtnt == "y" %}
from torchtnt.utils.rank_zero_log import rank_zero_info, rank_zero_warn, rank_zero_debug, rank_zero_error, rank_zero_only, get_global_rank
from typing import Any, Optional, Union
get_rank = get_global_rank
def rank_prefixed_message(message: str, rank: Optional[int]) -> str:
    """Add a prefix with the rank to a message."""
    if rank is not None:
        # specify the rank of the process being logged
        return f"[rank: {rank}] {message}"
    return message
{% endif %}

# Don't use RankedLogger