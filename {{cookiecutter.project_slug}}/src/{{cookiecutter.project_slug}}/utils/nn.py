from contextlib import contextmanager
import torch


def tiny_value_of_dtype(dtype: torch.dtype):
    """
    Returns a moderately tiny value for a given PyTorch data type that is used to avoid numerical
    issues such as division by zero.
    This is different from `info_value_of_dtype(dtype).tiny` because it causes some NaN bugs.
    Only supports floating point dtypes.
    """
    if not dtype.is_floating_point:
        raise TypeError("Only supports floating point dtypes.")
    if dtype == torch.float or dtype == torch.double:
        return 1e-13
    elif dtype == torch.half:
        return 1e-4
    else:
        raise TypeError("Does not support dtype " + str(dtype))


def masked_mean(
    vector: torch.Tensor,
    mask: torch.BoolTensor,
    dim: int,
    keepdim: bool = False,
) -> torch.Tensor:
    """
    To calculate mean along certain dimensions on masked values

    # Parameters

    vector : `torch.Tensor`
        The vector to calculate mean.
    mask : `torch.BoolTensor`
        The mask of the vector. It must be broadcastable with vector.
    dim : `int`
        The dimension to calculate mean
    keepdim : `bool`
        Whether to keep dimension

    # Returns

    `torch.Tensor`
        A `torch.Tensor` of including the mean values.
    """
    replaced_vector = vector.masked_fill(~mask, 0.0)

    value_sum = torch.sum(replaced_vector, dim=dim, keepdim=keepdim)
    dtype = vector.dtype
    value_count = torch.sum(mask, dim=dim, keepdim=keepdim).to(
        dtype=dtype
    ) + tiny_value_of_dtype(dtype)
    return value_sum / value_count


def masked_sum(
    vector: torch.Tensor,
    mask: torch.BoolTensor,
    dim: int,
    keepdim: bool = False,
) -> torch.Tensor:
    """
    To calculate sum along certain dimensions on masked values

    # Parameters

    vector : `torch.Tensor`
        The vector to calculate sum.
    mask : `torch.BoolTensor`
        The mask of the vector. It must be broadcastable with vector.
    dim : `int`
        The dimension to calculate sum
    keepdim : `bool`
        Whether to keep dimension

    # Returns

    `torch.Tensor`
        A `torch.Tensor` of including the sum values.
    """
    replaced_vector = vector.masked_fill(~mask, 0.0)

    return torch.sum(replaced_vector, dim=dim, keepdim=keepdim)


def get_mask_from_sequence_lengths(
    sequence_lengths: torch.Tensor, max_length: int
) -> torch.BoolTensor:
    """
    Given a variable of shape `(batch_size,)` that represents the sequence lengths of each batch
    element, this function returns a `(batch_size, max_length)` mask variable.  For example, if
    our input was `[2, 2, 3]`, with a `max_length` of 4, we'd return
    `[[1, 1, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0]]`.

    We require `max_length` here instead of just computing it from the input `sequence_lengths`
    because it lets us avoid finding the max, then copying that value from the GPU to the CPU so
    that we can use it to construct a new tensor.
    """
    # (batch_size, max_length)
    ones = sequence_lengths.new_ones(sequence_lengths.size(0), max_length)
    range_tensor = ones.cumsum(dim=1)
    return sequence_lengths.unsqueeze(1) >= range_tensor


dtype_map = {
    "float32": torch.float32,
    "float64": torch.float64,
    "float16": torch.float16,
    "bfloat16": torch.bfloat16,
}


def dtype(string: str) -> torch.dtype:
    """
    Convert a string to a PyTorch data type.

    # Parameters

    string : `str`
        The string to convert.

    # Returns

    `torch.dtype`
        The PyTorch data type.
    """
    if string in dtype_map:
        return dtype_map[string]
    else:
        raise ValueError(f"Unknown dtype: {string}")


# Define a function to select the appropriate dtype
def get_autocast_dtype():
    if torch.cuda.get_device_properties(0).major >= 8:  # Ampere and later architectures
        return torch.bfloat16
    else:
        return torch.float16


@contextmanager
def no_grad(no_grad_: bool = True):
    if no_grad_:
        with torch.no_grad():
            yield
    else:
        yield
