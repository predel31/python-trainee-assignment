import aiohttp
import logging
from asyncio import TimeoutError
from aiohttp import ClientError

logger = logging.getLogger(__name__)


async def get_text(url: str) -> str | None:
    """
    This function is used to get a text from url async.

    Args:
        url (str): our url to get data

    Returns:
        (str | None): matrix as string
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if 400 <= resp.status < 500:
                    logger.error("Client error")
                elif resp.status >= 500:
                    logger.error("server error")
                else:
                    return await resp.text()
    except ClientError as ex:
        logger.error(f"There are problems with connection {ex}")
    except TimeoutError as ex:
        logger.error(f"Timeout error {ex}")


def prepare_matrix(text: str) -> list[list[int]]:
    """
    Prepare matrix from raw string representation to python list object

    Args:
        text (str): raw string to prepare

    Returns:
        (list[list[int]]): prepared matrix
    """

    try:
        matrix = []
        for line in text.split('\n'):
            if line and line[0] != '+':
                matrix.append([int(num) for num in line[1:-1].split('|')])

        if matrix and not all([len(matrix) == len(line) for line in matrix]):
            raise ValueError("Matrix is not squared")
    except ValueError as ex:
        logger.warning(ex)
        return []

    return matrix


def traverse_matrix(matrix: list[list[int]], output: list[int] = None) -> list[int]:
    """
    Function to traverse matrix in the revert clockwise order

    Args:
        matrix (list[list[int]]): matrix object to traverse
        output (list[int]): help variable for recursive runs.
                            You don't need to provide for initial run

    Returns:
        (list[int]): traversed matrix
    """
    if output is None:
        output = []

    if not len(matrix):
        return output

    matrix = list(zip(*matrix[::-1]))
    output.extend(matrix[0][::-1])
    traverse_matrix(matrix[1:], output)


async def get_matrix(url: str) -> list[int]:
    """
    Main library function for user. Get url as a string to
    fetch the data, convert it and travers. Handle network errors.

    Args:
        url (str): url to get the data with matrix in text representation

    Returns:
        (list[int]): traversed matrix in the revert clockwise order
    """
    output = []
    text = await get_text(url)
    traverse_matrix(prepare_matrix(text), output)
    return output
